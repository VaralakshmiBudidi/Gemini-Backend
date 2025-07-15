# routes/subscription.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import SubscriptionStatusResponse
import stripe
import os
import json

router = APIRouter(tags=["Subscription"])

# ✅ Load your Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ✅ Environment configs
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")  # e.g., price_123abc
SUCCESS_URL = "http://localhost:8000/subscription/status"  # replace in production
CANCEL_URL = "http://localhost:8000/user/me"    # replace in production

# 1. Create Stripe Checkout Session
@router.post("/subscribe/pro")
def create_checkout_session(user: User = Depends(get_current_user)):
    if not STRIPE_PRICE_ID:
        raise HTTPException(status_code=500, detail="Stripe price ID is not set in .env")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1
            }],
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            metadata={"user_id": user.id}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. Handle Stripe Webhook
@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    try:
        event = json.loads(payload)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get("metadata", {}).get("user_id")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    user.tier = "Pro"
                    db.commit()
        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 3. Get Subscription Tier
@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(user: User = Depends(get_current_user)):
    return {"tier": user.tier}
