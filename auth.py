# auth.py
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from db import SessionLocal
from models import User

router = APIRouter()

# ------------ CONFIG ----------------
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ------------ DB Dependency ---------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------ Schemas ---------------
class SignupSchema(BaseModel):
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ------------ Utility Functions -----
def create_jwt(data: dict):
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGO)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    return pwd_context.hash(password)


# ------------ ROUTES ----------------
@router.post("/signup", response_model=TokenResponse)
def signup(user: SignupSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    hashed = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_jwt({"sub": str(new_user.id)})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(user: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(401, "Invalid email or password")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(401, "Invalid email or password")

    token = create_jwt({"sub": str(db_user.id)})
    return {"access_token": token}


# ------------ PROTECTED ROUTE HELPER ----
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Token expired or invalid")

    user = db.query(User).get(int(user_id))
    if not user:
        raise HTTPException(401, "User not found")
    return user
