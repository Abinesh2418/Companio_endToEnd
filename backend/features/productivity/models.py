"""
Models for Smart Proactive Productivity & Motivation System
Feature 2 → Sub Feature 3
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, time
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean
from database import Base
import uuid


class UserProductivityProfileDB(Base):
    """SQLAlchemy model for user productivity profiles"""
    __tablename__ = "user_productivity_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True, default="default_user")
    
    # Productivity windows (stored as JSON)
    high_productivity_hours = Column(JSON, nullable=False, default=list)  # List of hour ranges
    low_energy_hours = Column(JSON, nullable=False, default=list)
    
    # Activity statistics
    total_activities = Column(Integer, nullable=False, default=0)
    completed_tasks_count = Column(Integer, nullable=False, default=0)
    missed_tasks_count = Column(Integer, nullable=False, default=0)
    
    # Reminder preferences
    preferred_reminder_times = Column(JSON, nullable=False, default=list)
    reminder_frequency = Column(String, nullable=False, default="medium")  # low, medium, high
    
    # Responsiveness metrics
    average_response_time_minutes = Column(Float, nullable=True)
    reminder_engagement_rate = Column(Float, nullable=False, default=0.0)
    
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class ActivityLogDB(Base):
    """SQLAlchemy model for tracking user activity"""
    __tablename__ = "activity_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default_user")
    
    activity_type = Column(String, nullable=False)  # task_created, task_completed, task_updated, etc.
    related_entity_type = Column(String, nullable=True)  # goal, task, reminder
    related_entity_id = Column(String, nullable=True)
    
    activity_data = Column(JSON, nullable=True)  # Additional context
    
    timestamp = Column(DateTime, nullable=False, default=datetime.now)


class ReminderDB(Base):
    """SQLAlchemy model for reminders"""
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default_user")
    
    reminder_type = Column(String, nullable=False)  # daily_checkin, missed_task, progress_update, motivation
    
    # Related entities
    goal_id = Column(String, nullable=True)
    task_id = Column(String, nullable=True)
    
    # Message content
    title = Column(String(200), nullable=False)
    message = Column(String, nullable=False)
    motivation_level = Column(String, nullable=False, default="neutral")  # positive, encouraging, gentle
    
    # Scheduling
    scheduled_time = Column(DateTime, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String, nullable=False, default="pending")  # pending, delivered, seen, dismissed
    
    # User interaction
    seen_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    action_taken = Column(Boolean, nullable=False, default=False)  # Did user act on the reminder?
    
    created_at = Column(DateTime, nullable=False, default=datetime.now)


# Pydantic schemas for API

class ProductivityProfileResponse(BaseModel):
    """Schema for productivity profile response"""
    id: str
    user_id: str
    high_productivity_hours: List[Dict[str, int]]  # [{start: 9, end: 12}, ...]
    low_energy_hours: List[Dict[str, int]]
    total_activities: int
    completed_tasks_count: int
    missed_tasks_count: int
    preferred_reminder_times: List[str]
    reminder_frequency: str
    average_response_time_minutes: Optional[float]
    reminder_engagement_rate: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogCreate(BaseModel):
    """Schema for logging activity"""
    activity_type: str = Field(..., description="Type of activity")
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    activity_data: Optional[Dict] = None


class ActivityLogResponse(BaseModel):
    """Schema for activity log response"""
    id: str
    user_id: str
    activity_type: str
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    activity_data: Optional[Dict]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ReminderResponse(BaseModel):
    """Schema for reminder response"""
    id: str
    user_id: str
    reminder_type: str
    goal_id: Optional[str]
    task_id: Optional[str]
    title: str
    message: str
    motivation_level: str
    scheduled_time: datetime
    delivered_at: Optional[datetime]
    status: str
    seen_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    action_taken: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReminderUpdateStatus(BaseModel):
    """Schema for updating reminder status"""
    status: str = Field(..., description="New status: seen, dismissed")
    action_taken: Optional[bool] = False
