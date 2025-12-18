"""
User Authentication Models
Handles user registration, login, and session management with PostgreSQL
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import hashlib
import secrets
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Session
from database import Base


class UserDB(Base):
    """SQLAlchemy User model for database"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class User(BaseModel):
    """Pydantic User model"""
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None
    token: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserAuth:
    """User authentication handler using PostgreSQL database"""
    
    def __init__(self):
        """Initialize UserAuth (no parameters needed)"""
        pass
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self) -> str:
        """Generate a simple session token"""
        return secrets.token_urlsafe(32)
    
    def register(self, user_data: UserCreate, db: Session) -> Optional[User]:
        """Register a new user"""
        # Check if email already exists
        if db.query(UserDB).filter(UserDB.email == user_data.email).first():
            return None
        
        # Check if username already exists
        if db.query(UserDB).filter(UserDB.username == user_data.username).first():
            return None
        
        # Create new user
        user_id = secrets.token_urlsafe(16)
        hashed_password = self._hash_password(user_data.password)
        
        new_user = UserDB(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            created_at=datetime.utcnow(),
            last_login=None
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return User.from_orm(new_user)
    
    def login(self, login_data: UserLogin, db: Session) -> Optional[tuple[User, str]]:
        """Login user and return user with token"""
        hashed_password = self._hash_password(login_data.password)
        
        # Find user by email and password
        user_db = db.query(UserDB).filter(
            UserDB.email == login_data.email,
            UserDB.password == hashed_password
        ).first()
        
        if not user_db:
            return None
        
        # Update last login
        user_db.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user_db)
        
        user = User.from_orm(user_db)
        token = self._generate_token()
        
        return user, token
    
    def get_user_by_id(self, user_id: str, db: Session) -> Optional[User]:
        """Get user by ID"""
        user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
        if user_db:
            return User.from_orm(user_db)
        return None
    
    def get_user_by_email(self, email: str, db: Session) -> Optional[User]:
        """Get user by email"""
        user_db = db.query(UserDB).filter(UserDB.email == email).first()
        if user_db:
            return User.from_orm(user_db)
        return None


# In-memory session storage (for simplicity, consider Redis for production)
active_sessions = {}

def create_session(user_id: str, token: str):
    """Create a session"""
    active_sessions[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }

def get_session(token: str) -> Optional[str]:
    """Get user_id from session token"""
    session = active_sessions.get(token)
    if session:
        return session["user_id"]
    return None

def delete_session(token: str):
    """Delete a session (logout)"""
    if token in active_sessions:
        del active_sessions[token]
