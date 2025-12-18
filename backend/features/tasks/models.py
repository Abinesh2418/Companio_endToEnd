from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class TaskDB(Base):
    """SQLAlchemy model for tasks table"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="Not Started")
    dependencies = Column(JSON, nullable=False, default=list)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with goal
    goal = relationship("GoalDB", back_populates="tasks")


class Task(BaseModel):
    """
    Task model representing a single task within a goal.
    Tasks are organized by weeks and days, with support for dependencies.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    week_number: int  # Which week this task belongs to (1-indexed)
    day_number: Optional[int] = None  # Which day within the week (1-7), None for week-level tasks
    title: str
    description: Optional[str] = None
    status: str = "Not Started"  # Not Started, In Progress, Completed
    dependencies: List[str] = []  # List of task IDs that must be completed first
    order: int = 0  # Order within the week/day
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "task-uuid-1",
                "goal_id": "goal-uuid-1",
                "week_number": 1,
                "day_number": 1,
                "title": "Learn JSX Syntax",
                "description": "Understand JSX syntax and how to write components",
                "status": "Not Started",
                "dependencies": [],
                "order": 0
            }
        }


class TaskCreate(BaseModel):
    """Request model for creating a new task"""
    goal_id: str
    week_number: int
    day_number: Optional[int] = None
    title: str
    description: Optional[str] = None
    dependencies: List[str] = []
    order: int = 0


class TaskUpdate(BaseModel):
    """Request model for updating task details"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    dependencies: Optional[List[str]] = None
    order: Optional[int] = None
    week_number: Optional[int] = None
    day_number: Optional[int] = None


class TaskReorder(BaseModel):
    """Request model for reordering a single task"""
    task_id: str
    new_order: int
    new_week_number: Optional[int] = None


class TaskBulkReorder(BaseModel):
    """Request model for bulk reordering multiple tasks"""
    tasks: List[TaskReorder]


class TaskResponse(BaseModel):
    """Response model for task operations"""
    task: Task
    is_locked: bool = False  # True if dependencies are not yet completed
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": {
                    "id": "task-uuid-1",
                    "goal_id": "goal-uuid-1",
                    "week_number": 1,
                    "day_number": 1,
                    "title": "Learn JSX Syntax",
                    "status": "Not Started"
                },
                "is_locked": False
            }
        }
