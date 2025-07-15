from fastapi import FastAPI
from app.models import Base
from app.dependencies import engine
from app.routes import auth, user, chatroom, stripe, subscription

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gemini Backend Clone")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chatroom.router)
app.include_router(stripe.router)
app.include_router(subscription.router)
