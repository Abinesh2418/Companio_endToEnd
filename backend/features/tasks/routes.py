"""
Tasks Feature Routes
Handles intelligent task breakdown, task CRUD operations, and task management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func, cast, String
import uuid

from database import get_db
from features.goals.models import GoalDB, GoalResponse
from .models import Task, TaskDB, TaskCreate, TaskUpdate, TaskResponse, TaskBulkReorder
from ai.task_decomposer import TaskDecomposer, check_task_dependencies

router = APIRouter(prefix="/api", tags=["Tasks"])

# Initialize AI task decomposer
task_decomposer = TaskDecomposer()


@router.post("/goals/{goal_id}/tasks/generate")
async def generate_tasks(goal_id: str, db: Session = Depends(get_db)):
    """
    Generate tasks for a goal using intelligent task breakdown.
    
    Args:
        goal_id: UUID of the goal to generate tasks for
        db: Database session
        
    Returns:
        List of generated tasks with dependency information
        
    Raises:
        HTTPException: 404 if goal not found
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Convert to GoalResponse for task decomposer
    goal = GoalResponse(
        id=db_goal.id,
        title=db_goal.title,
        duration_weeks=db_goal.duration_weeks,
        priority=db_goal.priority,
        intensity=db_goal.intensity,
        start_date=db_goal.start_date,
        end_date=db_goal.end_date,
        created_at=db_goal.created_at
    )
    
    # Generate tasks using the decomposer
    tasks = task_decomposer.generate_tasks_for_goal(goal)
    
    # Store tasks in database
    for task in tasks:
        db_task = TaskDB(
            id=task.id,
            goal_id=task.goal_id,
            week_number=task.week_number,
            day_number=task.day_number,
            title=task.title,
            description=task.description,
            status=task.status,
            dependencies=task.dependencies,
            order=task.order,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        db.add(db_task)
    
    db.commit()
    
    # Build response with lock status
    task_responses = []
    for task in tasks:
        is_locked = not check_task_dependencies(task, tasks)
        task_responses.append(TaskResponse(task=task, is_locked=is_locked))
    
    return {
        "goal_id": goal_id,
        "goal_title": goal.title,
        "tasks": task_responses,
        "total_tasks": len(tasks)
    }


@router.get("/goals/{goal_id}/tasks")
async def get_tasks_by_goal(goal_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all tasks for a specific goal.
    
    Args:
        goal_id: UUID of the goal
        db: Database session
        
    Returns:
        List of tasks organized by weeks with lock status
        
    Raises:
        HTTPException: 404 if goal not found
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Get all tasks for this goal from database
    db_tasks = db.query(TaskDB).filter(TaskDB.goal_id == goal_id).order_by(TaskDB.week_number, TaskDB.order).all()
    
    # Convert to Pydantic Task models
    goal_tasks = [
        Task(
            id=t.id,
            goal_id=t.goal_id,
            week_number=t.week_number,
            day_number=t.day_number,
            title=t.title,
            description=t.description,
            status=t.status,
            dependencies=t.dependencies,
            order=t.order,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in db_tasks
    ]
    
    # Build response with lock status
    task_responses = []
    for task in goal_tasks:
        is_locked = not check_task_dependencies(task, goal_tasks)
        task_responses.append(TaskResponse(task=task, is_locked=is_locked))
    
    # Organize by weeks
    weeks = {}
    for task_resp in task_responses:
        week_num = task_resp.task.week_number
        if week_num not in weeks:
            weeks[week_num] = []
        weeks[week_num].append(task_resp)
    
    return {
        "goal_id": goal_id,
        "tasks": task_responses,
        "tasks_by_week": weeks,
        "total_tasks": len(goal_tasks)
    }


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get a specific task by ID.
    
    Args:
        task_id: UUID of the task
        db: Database session
        
    Returns:
        TaskResponse with task details and lock status
        
    Raises:
        HTTPException: 404 if task not found
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = Task(
        id=db_task.id,
        goal_id=db_task.goal_id,
        week_number=db_task.week_number,
        day_number=db_task.day_number,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        dependencies=db_task.dependencies,
        order=db_task.order,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )
    
    # Get all tasks for this goal
    db_goal_tasks = db.query(TaskDB).filter(TaskDB.goal_id == task.goal_id).all()
    goal_tasks = [
        Task(
            id=t.id,
            goal_id=t.goal_id,
            week_number=t.week_number,
            day_number=t.day_number,
            title=t.title,
            description=t.description,
            status=t.status,
            dependencies=t.dependencies,
            order=t.order,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in db_goal_tasks
    ]
    
    is_locked = not check_task_dependencies(task, goal_tasks)
    
    return TaskResponse(task=task, is_locked=is_locked)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task's details.
    
    Args:
        task_id: UUID of the task to update
        task_update: Fields to update
        db: Database session
        
    Returns:
        Updated task with lock status
        
    Raises:
        HTTPException: 404 if task not found, 400 if validation fails
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.status is not None:
        # Validate status
        if task_update.status not in ["Not Started", "In Progress", "Completed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        db_task.status = task_update.status
    if task_update.dependencies is not None:
        # Validate dependencies exist
        for dep_id in task_update.dependencies:
            dep_task = db.query(TaskDB).filter(TaskDB.id == dep_id).first()
            if not dep_task:
                raise HTTPException(status_code=400, detail=f"Dependency task {dep_id} not found")
        db_task.dependencies = task_update.dependencies
    if task_update.order is not None:
        db_task.order = task_update.order
    if task_update.week_number is not None:
        db_task.week_number = task_update.week_number
    if task_update.day_number is not None:
        db_task.day_number = task_update.day_number
    
    db_task.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_task)
    
    # Convert to Pydantic model
    task = Task(
        id=db_task.id,
        goal_id=db_task.goal_id,
        week_number=db_task.week_number,
        day_number=db_task.day_number,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        dependencies=db_task.dependencies,
        order=db_task.order,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )
    
    # Get lock status
    db_goal_tasks = db.query(TaskDB).filter(TaskDB.goal_id == task.goal_id).all()
    goal_tasks = [
        Task(
            id=t.id,
            goal_id=t.goal_id,
            week_number=t.week_number,
            day_number=t.day_number,
            title=t.title,
            description=t.description,
            status=t.status,
            dependencies=t.dependencies,
            order=t.order,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in db_goal_tasks
    ]
    is_locked = not check_task_dependencies(task, goal_tasks)
    
    return TaskResponse(task=task, is_locked=is_locked)


@router.post("/goals/{goal_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(goal_id: str, task_create: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new custom task for a goal.
    
    Args:
        goal_id: UUID of the goal
        task_create: Task creation data
        db: Database session
        
    Returns:
        Created task with lock status
        
    Raises:
        HTTPException: 404 if goal not found, 400 if validation fails
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Validate dependencies
    for dep_id in task_create.dependencies:
        dep_task = db.query(TaskDB).filter(TaskDB.id == dep_id).first()
        if not dep_task:
            raise HTTPException(status_code=400, detail=f"Dependency task {dep_id} not found")
    
    # Create task
    task_id = str(uuid.uuid4())
    db_task = TaskDB(
        id=task_id,
        goal_id=goal_id,
        week_number=task_create.week_number,
        day_number=task_create.day_number,
        title=task_create.title,
        description=task_create.description,
        dependencies=task_create.dependencies,
        order=task_create.order,
        status="Not Started",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Convert to Pydantic model
    task = Task(
        id=db_task.id,
        goal_id=db_task.goal_id,
        week_number=db_task.week_number,
        day_number=db_task.day_number,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        dependencies=db_task.dependencies,
        order=db_task.order,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )
    
    # Get lock status
    db_goal_tasks = db.query(TaskDB).filter(TaskDB.goal_id == goal_id).all()
    goal_tasks = [
        Task(
            id=t.id,
            goal_id=t.goal_id,
            week_number=t.week_number,
            day_number=t.day_number,
            title=t.title,
            description=t.description,
            status=t.status,
            dependencies=t.dependencies,
            order=t.order,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in db_goal_tasks
    ]
    is_locked = not check_task_dependencies(task, goal_tasks)
    
    return TaskResponse(task=task, is_locked=is_locked)


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Delete a task.
    
    Args:
        task_id: UUID of the task to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if task not found, 400 if other tasks depend on it
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if any other tasks depend on this one
    dependent_count = db.query(TaskDB).filter(
        func.json_contains(cast(TaskDB.dependencies, String), f'"{task_id}"')
    ).count()
    
    if dependent_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete task. {dependent_count} task(s) depend on it."
        )
    
    task_title = db_task.title
    
    db.delete(db_task)
    db.commit()
    
    return {
        "message": "Task deleted successfully",
        "deleted_task_title": task_title,
        "deleted_task_id": task_id
    }


@router.post("/goals/{goal_id}/tasks/reorder")
async def reorder_tasks(goal_id: str, reorder_data: TaskBulkReorder, db: Session = Depends(get_db)):
    """
    Bulk reorder tasks for a goal.
    
    Args:
        goal_id: UUID of the goal
        reorder_data: List of task reorder instructions
        db: Database session
        
    Returns:
        Updated task list
        
    Raises:
        HTTPException: 404 if goal or task not found, 400 if validation fails
    """
    db_goal = db.query(GoalDB).filter(GoalDB.id == goal_id).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Validate all tasks exist and belong to this goal
    for task_reorder in reorder_data.tasks:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_reorder.task_id).first()
        
        if not db_task:
            raise HTTPException(
                status_code=404, 
                detail=f"Task {task_reorder.task_id} not found"
            )
        
        if db_task.goal_id != goal_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Task {task_reorder.task_id} does not belong to goal {goal_id}"
            )
    
    # Apply reordering
    updated_count = 0
    for task_reorder in reorder_data.tasks:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_reorder.task_id).first()
        db_task.order = task_reorder.new_order
        if task_reorder.new_week_number is not None:
            db_task.week_number = task_reorder.new_week_number
        db_task.updated_at = datetime.now()
        updated_count += 1
    
    db.commit()
    
    # Get all tasks for this goal to return
    db_tasks = db.query(TaskDB).filter(TaskDB.goal_id == goal_id).order_by(TaskDB.week_number, TaskDB.order).all()
    
    goal_tasks = [
        Task(
            id=t.id,
            goal_id=t.goal_id,
            week_number=t.week_number,
            day_number=t.day_number,
            title=t.title,
            description=t.description,
            status=t.status,
            dependencies=t.dependencies,
            order=t.order,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in db_tasks
    ]
    
    # Build response with lock status
    task_responses = []
    for task in goal_tasks:
        is_locked = not check_task_dependencies(task, goal_tasks)
        task_responses.append(TaskResponse(task=task, is_locked=is_locked))
    
    return {
        "message": "Tasks reordered successfully",
        "goal_id": goal_id,
        "updated_count": updated_count,
        "tasks": task_responses
    }
