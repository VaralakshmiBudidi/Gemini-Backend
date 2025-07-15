# app/routes/chatroom.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks # Import BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, redis_client # Import redis_client
from app import schemas, models
from typing import List
from datetime import date
from app.utils.gemini import generate_content # Ensure this import path is correct

import time # Needed for rate limiting key expiration

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


# Helper function for background saving (moved from messages.py concept)
def _save_messages_background(
    room_id: int,
    user_id: int,
    user_content: str,
    ai_response_text: str,
    db: Session # Pass db session here as it's a background task
):
    # Save user's message
    user_msg = models.Message(
        chatroom_id=room_id,
        user_id=user_id,
        content=user_content,
        role="user",
        # The 'response' field seems redundant if 'content' and 'role' are used.
        # Consider making 'response' nullable or removing it from the model if not consistently used.
        response=""
    )
    db.add(user_msg)
    db.commit() # Commit user message

    # Save assistant's response
    assistant_msg = models.Message(
        chatroom_id=room_id,
        user_id=None, # AI messages are not tied to a specific user_id
        content=ai_response_text,
        role="assistant",
        response="" # The 'response' field seems redundant here too.
    )
    db.add(assistant_msg)
    db.commit() # Commit assistant message


# ✅ POST /chatroom — Create a new chatroom
@router.post("", response_model=schemas.ChatroomResponse)
def create_chatroom(
    data: schemas.ChatroomCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(models.Chatroom).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Chatroom already exists")

    new_room = models.Chatroom(name=data.name, created_by=user.id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    # Add creator as member
    member = models.ChatMember(user_id=user.id, chatroom_id=new_room.id)
    db.add(member)
    db.commit()

    return new_room


# ✅ GET /chatroom — List all chatrooms for the current user
@router.get("", response_model=List[schemas.ChatroomResponse])
def list_user_chatrooms(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    room_ids = (
        db.query(models.ChatMember.chatroom_id)
        .filter_by(user_id=user.id)
        .all()
    )
    ids = [r[0] for r in room_ids]
    return db.query(models.Chatroom).filter(models.Chatroom.id.in_(ids)).all()


# ✅ GET /chatroom/{id} — Get chatroom details
@router.get("/{id}", response_model=schemas.ChatroomResponse)
def get_chatroom(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    room = db.query(models.Chatroom).filter_by(id=id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    return room


# ✅ POST /chatroom/{room_id}/message — Send prompt and get AI reply (Enhanced with features from messages.py)
@router.post("/{room_id}/message", response_model=schemas.GeminiResponse) # Changed response_model
def send_message_to_chatroom(
    room_id: int,
    body: schemas.MessageCreate, # Using MessageCreate
    background_tasks: BackgroundTasks, # Added BackgroundTasks
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    membership = db.query(models.ChatMember).filter_by(user_id=user.id, chatroom_id=room_id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this chatroom")

    # 🔒 Consolidated Rate Limit (using Redis and is_pro from messages.py logic)
    # Ensure User model has 'is_pro' field (we added this previously)
    if not user.is_pro: # Using user.is_pro for rate limiting
        redis = redis_client() # Get redis client
        key = f"rate:{user.id}:{time.strftime('%Y-%m-%d')}"
        count = int(redis.get(key) or 0)
        if count >= 5: # Daily limit 5
            raise HTTPException(
                status_code=429,
                detail="Daily message limit reached. Upgrade to Pro for unlimited access."
            )
        redis.incr(key)
        redis.expire(key, 86400) # Expire after 24 hours

    # Get Gemini AI response immediately for the client
    try:
        response_text = generate_content(body.content).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    # Save user's message and assistant's response in a background task
    # This allows the API to respond faster to the user
    background_tasks.add_task(
        _save_messages_background,
        room_id,
        user.id,
        body.content,
        response_text,
        db # Pass the database session
    )

    return schemas.GeminiResponse(response=response_text) # Return GeminiResponse