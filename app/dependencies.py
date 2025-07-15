import os
from dotenv import load_dotenv
from pathlib import Path
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import jwt, JWTError  # ✅ Make sure JWTError is imported
import redis

# ✅ Load .env from the project root
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# ✅ Load ENV vars
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# ✅ Redis configuration (no SSL for Redis Cloud free-tier)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# ✅ Validate .env loading
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not loaded — check your .env file path or variable names.")

# ✅ SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Redis client factory
def redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )

# ✅ JWT generator
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Auth token extraction
oauth2_scheme = HTTPBearer()

# ✅ Authenticated user extractor
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        mobile: str = payload.get("sub")
        if mobile is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from app.models import User  # Avoid circular import
    user = db.query(User).filter(User.mobile == mobile).first()
    if user is None:
        raise credentials_exception

    return user
