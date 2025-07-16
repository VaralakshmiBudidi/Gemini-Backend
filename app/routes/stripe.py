from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
import os
from app.models import User
from app.dependencies import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/webhook", tags=["Stripe"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")

        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.tier = "Pro"
                user.is_pro= True
                db.commit()

    return {"status": "success"}
