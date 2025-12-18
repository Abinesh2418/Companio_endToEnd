"""
Productivity & Motivation Feature Routes
Handles smart reminders, daily check-ins, activity logs, and productivity analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from .models import (
    UserProductivityProfileDB, ActivityLogDB, ReminderDB,
    ProductivityProfileResponse, ActivityLogCreate, ActivityLogResponse,
    ReminderResponse, ReminderUpdateStatus
)
from ai.productivity_analyzer import ProductivityAnalyzer
from ai.reminder_generator import ReminderGenerator

router = APIRouter(prefix="/api", tags=["Productivity & Reminders"])

# Initialize AI services
productivity_analyzer = ProductivityAnalyzer()
reminder_generator = ReminderGenerator()


@router.get("/productivity/profile", response_model=ProductivityProfileResponse)
async def get_productivity_profile(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Get user's productivity profile including high-productivity hours,
    low-energy periods, and activity statistics
    """
    # Get or create profile
    profile = db.query(UserProductivityProfileDB).filter(
        UserProductivityProfileDB.user_id == user_id
    ).first()
    
    if not profile:
        # Create new profile with defaults
        analysis = productivity_analyzer.analyze_user_productivity(db, user_id)
        
        profile = UserProductivityProfileDB(
            user_id=user_id,
            high_productivity_hours=analysis["high_productivity_hours"],
            low_energy_hours=analysis["low_energy_hours"],
            total_activities=analysis["total_activities"],
            completed_tasks_count=analysis["completed_tasks"],
            missed_tasks_count=analysis["missed_tasks"],
            preferred_reminder_times=["09:00", "14:00", "18:00"],
            reminder_frequency="medium",
            average_response_time_minutes=analysis["average_response_time_minutes"],
            reminder_engagement_rate=0.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return ProductivityProfileResponse.model_validate(profile)


@router.post("/productivity/analyze")
async def analyze_productivity(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Re-analyze user's productivity patterns and update profile
    """
    analysis = productivity_analyzer.analyze_user_productivity(db, user_id)
    
    # Update profile
    profile = db.query(UserProductivityProfileDB).filter(
        UserProductivityProfileDB.user_id == user_id
    ).first()
    
    if profile:
        profile.high_productivity_hours = analysis["high_productivity_hours"]
        profile.low_energy_hours = analysis["low_energy_hours"]
        profile.total_activities = analysis["total_activities"]
        profile.completed_tasks_count = analysis["completed_tasks"]
        profile.missed_tasks_count = analysis["missed_tasks"]
        profile.average_response_time_minutes = analysis["average_response_time_minutes"]
        profile.updated_at = datetime.now()
        db.commit()
        db.refresh(profile)
    
    return {
        "message": "Productivity analysis completed",
        "analysis": analysis
    }


@router.post("/productivity/daily-checkin", response_model=ReminderResponse, status_code=201)
async def create_daily_checkin(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Create a daily check-in reminder (only once per day)
    """
    # Check if a daily check-in already exists within the last 24 hours
    now = datetime.utcnow()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    existing_checkin = db.query(ReminderDB).filter(
        ReminderDB.user_id == user_id,
        ReminderDB.reminder_type == "daily_checkin",
        ReminderDB.created_at >= twenty_four_hours_ago
    ).first()
    
    if existing_checkin:
        raise HTTPException(
            status_code=400,
            detail="Daily check-in already generated for today. Come back tomorrow! 😊"
        )
    
    reminder = reminder_generator.generate_daily_checkin(
        db, user_id, scheduled_time=now
    )
    
    # Set to delivered status immediately
    reminder.status = "delivered"
    reminder.delivered_at = now
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return ReminderResponse.model_validate(reminder)


@router.post("/productivity/reminders/generate", status_code=201)
async def generate_reminders(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Generate all needed reminders based on current state
    Always generates at least one reminder regardless of time
    """
    # Generate needed reminders
    reminders = reminder_generator.detect_and_generate_needed_reminders(db, user_id)
    
    # Save to database
    for reminder in reminders:
        db.add(reminder)
    
    db.commit()
    
    return {
        "message": "Reminders generated successfully",
        "reminders_generated": len(reminders),
        "reminders": [ReminderResponse.model_validate(r) for r in reminders]
    }


@router.get("/productivity/reminders")
async def get_reminders(
    user_id: str = "default_user",
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get user's reminders
    
    Filter by status: pending, delivered, seen, dismissed
    """
    query = db.query(ReminderDB).filter(ReminderDB.user_id == user_id)
    
    if status:
        query = query.filter(ReminderDB.status == status)
    
    reminders = query.order_by(ReminderDB.scheduled_time.desc()).limit(limit).all()
    
    return {
        "reminders": [ReminderResponse.model_validate(r) for r in reminders],
        "count": len(reminders)
    }


@router.get("/productivity/reminders/pending")
async def get_pending_reminders(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Get all pending reminders that should be delivered now
    """
    now = datetime.now()
    
    reminders = db.query(ReminderDB).filter(
        ReminderDB.user_id == user_id,
        ReminderDB.status == "pending",
        ReminderDB.scheduled_time <= now
    ).order_by(ReminderDB.scheduled_time).all()
    
    # Mark as delivered
    for reminder in reminders:
        reminder.status = "delivered"
        reminder.delivered_at = now
    
    db.commit()
    
    return {
        "reminders": [ReminderResponse.model_validate(r) for r in reminders],
        "count": len(reminders)
    }


@router.patch("/productivity/reminders/{reminder_id}/status")
async def update_reminder_status(
    reminder_id: str,
    status_update: ReminderUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Update reminder status (seen, dismissed)
    """
    reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    now = datetime.utcnow()
    
    if status_update.status == "seen":
        reminder.status = "seen"
        reminder.seen_at = now
    elif status_update.status == "dismissed":
        reminder.status = "dismissed"
        reminder.dismissed_at = now
    
    if status_update.action_taken is not None:
        reminder.action_taken = status_update.action_taken
    
    # Log activity
    activity = ActivityLogDB(
        user_id=reminder.user_id,
        activity_type=f"reminder_{status_update.status}",
        related_entity_type="reminder",
        related_entity_id=reminder_id,
        timestamp=now
    )
    db.add(activity)
    
    db.commit()
    db.refresh(reminder)
    
    return {
        "message": "Reminder status updated",
        "reminder": ReminderResponse.model_validate(reminder)
    }


@router.delete("/productivity/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a reminder
    """
    reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "Reminder deleted successfully"}


@router.post("/activity/log", response_model=ActivityLogResponse)
async def log_activity(
    activity: ActivityLogCreate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Log user activity for productivity tracking
    
    Activity types:
    - task_created
    - task_completed
    - task_updated
    - task_missed
    - goal_created
    - goal_updated
    - reminder_seen
    - reminder_dismissed
    """
    activity_log = ActivityLogDB(
        user_id=user_id,
        activity_type=activity.activity_type,
        related_entity_type=activity.related_entity_type,
        related_entity_id=activity.related_entity_id,
        activity_data=activity.activity_data,
        timestamp=datetime.now()
    )
    
    db.add(activity_log)
    
    # Update productivity profile stats
    profile = db.query(UserProductivityProfileDB).filter(
        UserProductivityProfileDB.user_id == user_id
    ).first()
    
    if profile:
        profile.total_activities += 1
        if activity.activity_type == "task_completed":
            profile.completed_tasks_count += 1
        elif activity.activity_type == "task_missed":
            profile.missed_tasks_count += 1
        profile.updated_at = datetime.now()
    
    db.commit()
    db.refresh(activity_log)
    
    return ActivityLogResponse.model_validate(activity_log)


@router.get("/activity/history")
async def get_activity_history(
    user_id: str = "default_user",
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get user's activity history for the specified number of days
    """
    since = datetime.now() - timedelta(days=days)
    
    activities = db.query(ActivityLogDB).filter(
        ActivityLogDB.user_id == user_id,
        ActivityLogDB.timestamp >= since
    ).order_by(ActivityLogDB.timestamp.desc()).all()
    
    return {
        "activities": [ActivityLogResponse.model_validate(a) for a in activities],
        "count": len(activities),
        "period_days": days
    }


@router.get("/productivity/insights")
async def get_productivity_insights(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Get comprehensive productivity insights and recommendations
    """
    profile = db.query(UserProductivityProfileDB).filter(
        UserProductivityProfileDB.user_id == user_id
    ).first()
    
    analysis = productivity_analyzer.analyze_user_productivity(db, user_id)
    
    # Calculate engagement metrics
    total_reminders = db.query(ReminderDB).filter(
        ReminderDB.user_id == user_id
    ).count()
    
    acted_reminders = db.query(ReminderDB).filter(
        ReminderDB.user_id == user_id,
        ReminderDB.action_taken == True
    ).count()
    
    engagement_rate = (acted_reminders / total_reminders * 100) if total_reminders > 0 else 0
    
    # Get optimal time for next reminder
    next_optimal_time = productivity_analyzer.get_optimal_reminder_time(db, user_id)
    
    return {
        "profile": ProductivityProfileResponse.model_validate(profile) if profile else None,
        "analysis": analysis,
        "engagement": {
            "total_reminders": total_reminders,
            "acted_on": acted_reminders,
            "engagement_rate": round(engagement_rate, 2)
        },
        "recommendations": {
            "next_optimal_reminder_time": next_optimal_time.isoformat(),
            "should_send_reminder_now": productivity_analyzer.should_send_reminder_now(db, user_id)
        }
    }


@router.delete("/productivity/reminders/clear-all")
async def clear_all_reminders(db: Session = Depends(get_db)):
    """
    Clear all reminders (for testing/debugging)
    """
    count = db.query(ReminderDB).delete()
    db.commit()
    return {
        "message": f"Cleared {count} reminders",
        "count": count
    }
