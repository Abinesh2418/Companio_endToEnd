from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from typing import Literal
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from database import Base
import uuid


class GoalDB(Base):
    """SQLAlchemy model for goals table"""
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    priority = Column(String(50), nullable=False)
    intensity = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationship with tasks
    tasks = relationship("TaskDB", back_populates="goal", cascade="all, delete-orphan")


class GoalCreate(BaseModel):
    """Schema for creating a new goal"""
    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    duration_weeks: int = Field(..., gt=0, le=52, description="Duration in weeks (1-52)")
    priority: Literal["Low", "Medium", "High"] = Field(..., description="Priority level")
    intensity: Literal["Light", "Normal", "Aggressive"] = Field(..., description="Learning intensity")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title"""
        v = v.strip()
        if not v:
            raise ValueError('Title cannot be empty or whitespace only')
        return v


class GoalResponse(BaseModel):
    """Schema for goal response"""
    id: str
    title: str
    duration_weeks: int
    priority: str
    intensity: str
    start_date: datetime
    end_date: datetime
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
