"""
Goals Feature Routes
Handles goal creation, reading, updating, and deletion (CRUD operations)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from database import get_db
from .models import GoalDB, GoalCreate, GoalResponse
from features.tasks.models import TaskDB

router = APIRouter(prefix="/api/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=201)
async def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """
    Create a new goal with auto-calculated dates
    
    Args:
        goal: GoalCreate schema with title, duration_weeks, priority, intensity
        db: Database session
    
    Returns:
        GoalResponse: Created goal with generated ID and calculated dates
    
    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        # Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=goal.duration_weeks)
        created_at = datetime.now()
        
        # Create database model
        db_goal = GoalDB(
            id=str(uuid.uuid4()),
            title=goal.title,
            duration_weeks=goal.duration_weeks,
            priority=goal.priority,
            intensity=goal.intensity,
            start_date=start_date,
            end_date=end_date,
            created_at=created_at
        )
        
        # Save to database
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        
        # Return as Pydantic model
        return GoalResponse(
            id=db_goal.id,
            title=db_goal.title,
            duration_weeks=db_goal.duration_weeks,
            priority=db_goal.priority,
            intensity=db_goal.intensity,
            start_date=db_goal.start_date,
            end_date=db_goal.end_date,
            created_at=db_goal.created_at
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the goal")


@router.get("")
async def get_goals(db: Session = Depends(get_db)):
    """
    Retrieve all goals
    
    Args:
        db: Database session
    
    Returns:
        List of all created goals
    """
    goals = db.query(GoalDB).all()
    
    # Convert to Pydantic models
    goal_responses = [
        GoalResponse(
            id=g.id,
            title=g.title,
            duration_weeks=g.duration_weeks,
            priority=g.priority,
            intensity=g.intensity,
            start_date=g.start_date,
            end_date=g.end_date,
            created_at=g.created_at
        ) for g in goals
    ]
    
    return {"goals": goal_responses, "count": len(goal_responses)}


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific goal by ID
    
    Args:
        goal_id: UUID of the goal
        db: Database session
        
    Returns:
        GoalResponse: The requested goal
        
    Raises:
        HTTPException: 404 if goal not found
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return GoalResponse(
        id=db_goal.id,
        title=db_goal.title,
        duration_weeks=db_goal.duration_weeks,
        priority=db_goal.priority,
        intensity=db_goal.intensity,
        start_date=db_goal.start_date,
        end_date=db_goal.end_date,
        created_at=db_goal.created_at
    )


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(goal_id: str, goal: GoalCreate, db: Session = Depends(get_db)):
    """
    Update an existing goal
    
    Args:
        goal_id: UUID of the goal to update
        goal: Updated goal data
        db: Database session
        
    Returns:
        GoalResponse: Updated goal
        
    Raises:
        HTTPException: 404 if goal not found, 400 if validation fails
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    try:
        # Calculate new dates
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=goal.duration_weeks)
        
        # Update goal fields
        db_goal.title = goal.title
        db_goal.duration_weeks = goal.duration_weeks
        db_goal.priority = goal.priority
        db_goal.intensity = goal.intensity
        db_goal.start_date = start_date
        db_goal.end_date = end_date
        
        db.commit()
        db.refresh(db_goal)
        
        return GoalResponse(
            id=db_goal.id,
            title=db_goal.title,
            duration_weeks=db_goal.duration_weeks,
            priority=db_goal.priority,
            intensity=db_goal.intensity,
            start_date=db_goal.start_date,
            end_date=db_goal.end_date,
            created_at=db_goal.created_at
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the goal")


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    """
    Delete a goal
    
    Args:
        goal_id: UUID of the goal to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if goal not found
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Count associated tasks before deletion
    tasks_count = db.query(TaskDB).filter(TaskDB.goal_id == goal_id).count()
    
    goal_title = db_goal.title
    
    # Delete goal (tasks will be deleted automatically due to cascade)
    db.delete(db_goal)
    db.commit()
    
    return {
        "message": "Goal deleted successfully",
        "deleted_goal_title": goal_title,
        "deleted_goal_id": goal_id,
        "deleted_tasks_count": tasks_count
    }
