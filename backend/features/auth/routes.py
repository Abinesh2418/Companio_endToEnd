"""
Authentication Feature Routes
Handles user registration, login, logout, and session management
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from .models import (
    UserAuth, UserCreate, UserLogin, UserResponse, User,
    create_session, get_session, delete_session
)
from features.productivity.models import ReminderDB
from ai.reminder_generator import ReminderGenerator
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Initialize services
user_auth = UserAuth()
reminder_generator = ReminderGenerator()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    user_id = get_session(token)
    
    if not user_id:
        return None
    
    return user_auth.get_user_by_id(user_id, db)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    Stores user credentials in PostgreSQL database
    """
    user = user_auth.register(user_data, db)
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    
    # Create session token
    token = user_auth._generate_token()
    create_session(user.id, token)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        last_login=user.last_login,
        token=token
    )


@router.post("/login", response_model=UserResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with email and password
    Returns user info and session token
    Stores login timestamp in PostgreSQL database
    
    Also generates daily check-in reminder (once per day only)
    """
    result = user_auth.login(login_data, db)
    
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    user, token = result
    create_session(user.id, token)
    
    # Check if a daily check-in reminder already exists within the last 24 hours
    now = datetime.utcnow()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    existing_checkin = db.query(ReminderDB).filter(
        ReminderDB.user_id == user.id,
        ReminderDB.reminder_type == "daily_checkin",
        ReminderDB.created_at >= twenty_four_hours_ago
    ).first()
    
    # Only generate a new daily check-in if none exists in the last 24 hours
    if not existing_checkin:
        checkin_reminder = reminder_generator.generate_daily_checkin(
            db, user.id, scheduled_time=now
        )
        checkin_reminder.status = "delivered"
        checkin_reminder.delivered_at = now
        db.add(checkin_reminder)
        db.commit()
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        last_login=user.last_login,
        token=token
    )


@router.post("/logout")
async def logout_user(authorization: Optional[str] = Header(None)):
    """
    Logout user by invalidating session token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    delete_session(token)
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user information
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )
