from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    tenant = None
    if user_in.tenant_name:
        tenant = db.query(Tenant).filter(Tenant.name == user_in.tenant_name).first()
    if not tenant:
        tenant = Tenant(name=user_in.tenant_name or user_in.email.split("@")[0])
        db.add(tenant)
        db.flush()

    new_user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password), tenant_id=tenant.id)
    db.add(new_user)
    db.commit()

    return {"access_token": "dummytoken", "token_type": "bearer"}