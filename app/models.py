from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean # Import Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func
from app.dependencies import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True) # CHANGED: Renamed for clarity and security
    tier = Column(String, default="Basic")
    is_pro = Column(Boolean, default=False) # ADDED: For rate limiting logic

    chatrooms = relationship("Chatroom", back_populates="creator")
    messages = relationship("Message", back_populates="user")


class Chatroom(Base):
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="chatrooms")
    messages = relationship("Message", back_populates="chatroom")


class ChatMember(Base):
    __tablename__ = "chat_members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text)
    response = Column(Text) # Consider if this is truly needed; 'content' and 'role' often suffice
    role = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="messages")
    chatroom = relationship("Chatroom", back_populates="messages")


Base.metadata.create_all(bind=engine)