"""
Reminder Generator - Generates context-aware, motivational reminders
based on user's tasks, goals, and activity patterns.

Feature 2 → Sub Feature 3
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from features.productivity.models import ReminderDB
from features.goals.models import GoalDB
from features.tasks.models import TaskDB
import random


class ReminderGenerator:
    """
    Generates context-aware reminders and motivational messages
    that are positive, encouraging, and non-guilt-based.
    """
    
    def __init__(self):
        self.motivational_messages = {
            "morning": [
                "Good morning! Ready to make today count? ☀️",
                "A fresh start awaits! Let's tackle those goals together. 💪",
                "New day, new opportunities. You've got this! 🌟",
                "Morning! Time to turn those dreams into achievements. ✨"
            ],
            "progress": [
                "You're making great progress! Keep up the momentum! 🚀",
                "Look how far you've come! Every step counts. 🎯",
                "Proud of your dedication! You're on the right track. 🌈",
                "Your consistency is paying off! Keep going! ⭐"
            ],
            "missed_task": [
                "No worries! Life happens. Ready to get back on track? 💚",
                "It's okay to miss a step. What matters is getting back up! 🌱",
                "Let's reset and refocus. You've got this! 🔄",
                "Every moment is a chance for a fresh start. Let's go! ✨"
            ],
            "completion": [
                "Awesome work! You completed another task! 🎉",
                "You're crushing it! Another win in the books! 🏆",
                "Look at you go! Keep that energy up! ⚡",
                "Success! You're building great habits! 🌟"
            ],
            "weekly": [
                "Week check-in! You've accomplished so much. What's next? 📊",
                "Time to reflect on your amazing progress this week! 💭",
                "Another week of growth! Ready for the next challenge? 🎯",
                "Your weekly journey continues. Stay focused! 🌟"
            ],
            "encouragement": [
                "Remember: progress, not perfection. You're doing great! 💙",
                "Small steps lead to big results. Keep moving forward! 🚶",
                "Believe in yourself as much as we believe in you! 🌈",
                "You're capable of amazing things. One task at a time! ✨"
            ]
        }
    
    def generate_daily_checkin(
        self, 
        db: Session, 
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate daily check-in reminder"""
        
        # Get user's active goals
        goals = db.query(GoalDB).all()
        goal_count = len(goals)
        
        # Get pending tasks
        pending_tasks = db.query(TaskDB).filter(
            TaskDB.status == "Not Started"
        ).count()
        
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
        
        # Determine greeting based on time of day (UTC will be converted to local time in frontend)
        hour = scheduled_time.hour
        if 5 <= hour < 12:
            greeting = random.choice(self.motivational_messages["morning"])
        elif 12 <= hour < 17:
            greeting = "Good afternoon! Ready to power through? 🌞"
        elif 17 <= hour < 21:
            greeting = "Good evening! Let's make the most of your time! 🌆"
        else:
            greeting = "Hey there! Late night productivity session? 🌙"
        
        # Create personalized message (time will be displayed by frontend in user's local timezone)
        message_parts = [
            greeting,
            f"\n\nYou have {goal_count} active goal(s) and {pending_tasks} task(s) waiting for you.",
            "\n\nWhat would you like to focus on right now?"
        ]
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="daily_checkin",
            title="Daily Check-In ☀️",
            message="".join(message_parts),
            motivation_level="encouraging",
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        return reminder
    
    def generate_missed_task_reminder(
        self,
        db: Session,
        task: TaskDB,
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate gentle reminder for missed task"""
        
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
        
        motivation_msg = random.choice(self.motivational_messages["missed_task"])
        
        message = f"{motivation_msg}\n\nTask: {task.title}\n\nTake your time, and when you're ready, let's get it done together!"
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="missed_task",
            goal_id=task.goal_id,
            task_id=task.id,
            title="Gentle Nudge 💚",
            message=message,
            motivation_level="gentle",
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        return reminder
    
    def generate_progress_update(
        self,
        db: Session,
        goal: GoalDB,
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate progress update reminder"""
        
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
        
        # Calculate goal progress
        total_tasks = db.query(TaskDB).filter(TaskDB.goal_id == goal.id).count()
        completed_tasks = db.query(TaskDB).filter(
            TaskDB.goal_id == goal.id,
            TaskDB.status == "Completed"
        ).count()
        
        if total_tasks > 0:
            progress_percent = int((completed_tasks / total_tasks) * 100)
        else:
            progress_percent = 0
        
        motivation_msg = random.choice(self.motivational_messages["progress"])
        
        message = (
            f"{motivation_msg}\n\n"
            f"Goal: {goal.title}\n"
            f"Progress: {completed_tasks}/{total_tasks} tasks ({progress_percent}%)\n\n"
            f"Keep that momentum going! 🚀"
        )
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="progress_update",
            goal_id=goal.id,
            title="Progress Update 📊",
            message=message,
            motivation_level="positive",
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        return reminder
    
    def generate_completion_celebration(
        self,
        db: Session,
        task: TaskDB,
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate celebration message for task completion"""
        
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
        
        celebration_msg = random.choice(self.motivational_messages["completion"])
        
        message = (
            f"{celebration_msg}\n\n"
            f"You completed: {task.title}\n\n"
            f"Every accomplishment, big or small, is worth celebrating! 🎉"
        )
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="celebration",
            goal_id=task.goal_id,
            task_id=task.id,
            title="Achievement Unlocked! 🏆",
            message=message,
            motivation_level="positive",
            scheduled_time=scheduled_time,
            status="delivered",
            delivered_at=scheduled_time
        )
        
        return reminder
    
    def generate_weekly_review(
        self,
        db: Session,
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate weekly progress review reminder"""
        
        if scheduled_time is None:
            # Schedule for Sunday evening
            now = datetime.utcnow()
            days_until_sunday = (6 - now.weekday()) % 7
            scheduled_time = (now + timedelta(days=days_until_sunday)).replace(hour=18, minute=0)
        
        # Get weekly stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        completed_this_week = db.query(TaskDB).filter(
            TaskDB.status == "Completed",
            TaskDB.updated_at >= week_ago
        ).count()
        
        motivation_msg = random.choice(self.motivational_messages["weekly"])
        
        message = (
            f"{motivation_msg}\n\n"
            f"This week, you completed {completed_this_week} task(s)!\n\n"
            f"Take a moment to reflect on your progress and plan for the week ahead. 📝"
        )
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="weekly_review",
            title="Weekly Review 📅",
            message=message,
            motivation_level="encouraging",
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        return reminder
    
    def generate_custom_motivation(
        self,
        db: Session,
        user_id: str = "default_user",
        scheduled_time: Optional[datetime] = None
    ) -> ReminderDB:
        """Generate general motivational message"""
        
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
        
        motivation_msg = random.choice(self.motivational_messages["encouragement"])
        
        # Add context about current goals and tasks
        goal_count = db.query(GoalDB).count()
        task_count = db.query(TaskDB).filter(TaskDB.status == "Not Started").count()
        
        message_parts = [
            motivation_msg,
            f"\n\nYou have {goal_count} active goal(s)."
        ]
        
        if task_count > 0:
            message_parts.append(f"\nReady to tackle one of your {task_count} pending task(s)? Every small step counts! 🌟")
        else:
            message_parts.append("\nYou're all caught up! Great work staying on top of your goals! ✨")
        
        reminder = ReminderDB(
            user_id=user_id,
            reminder_type="motivation",
            title="You've Got This! 💪",
            message="".join(message_parts),
            motivation_level="encouraging",
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        return reminder
    
    def detect_and_generate_needed_reminders(
        self,
        db: Session,
        user_id: str = "default_user"
    ) -> List[ReminderDB]:
        """
        Analyze current state and generate all needed reminders
        
        Returns:
            List of reminders that should be created
        """
        reminders_to_create = []
        now = datetime.utcnow()
        
        # 1. Check for pending tasks that need attention
        pending_tasks = db.query(TaskDB).filter(
            TaskDB.status == "Not Started"
        ).limit(5).all()
        
        if len(pending_tasks) >= 3:
            # Generate motivational reminder to start working on tasks
            motivation_msg = random.choice(self.motivational_messages["encouragement"])
            reminder = ReminderDB(
                user_id=user_id,
                reminder_type="motivation",
                title="Time to Make Progress! 🚀",
                message=f"{motivation_msg}\n\nYou have {len(pending_tasks)} tasks waiting. Pick one and let's get started!",
                motivation_level="encouraging",
                scheduled_time=now,
                status="pending"
            )
            reminders_to_create.append(reminder)
        
        # 2. Check for goals and their progress
        goals = db.query(GoalDB).all()
        for goal in goals:
            total_tasks = db.query(TaskDB).filter(TaskDB.goal_id == goal.id).count()
            completed = db.query(TaskDB).filter(
                TaskDB.goal_id == goal.id,
                TaskDB.status == "Completed"
            ).count()
            in_progress = db.query(TaskDB).filter(
                TaskDB.goal_id == goal.id,
                TaskDB.status == "In Progress"
            ).count()
            
            # Generate progress update for any goal with tasks
            if total_tasks > 0:
                progress_pct = (completed / total_tasks) * 100
                
                # If goal has good progress, celebrate it
                if progress_pct >= 25 and progress_pct < 100:
                    reminder = self.generate_progress_update(db, goal, user_id)
                    reminders_to_create.append(reminder)
                    break  # Only one progress reminder at a time
                
                # If goal has tasks in progress, encourage continuation
                elif in_progress > 0:
                    reminder = ReminderDB(
                        user_id=user_id,
                        reminder_type="progress_update",
                        goal_id=goal.id,
                        title=f"Keep Going! 💪",
                        message=f"You're making progress on '{goal.title}'!\n\nYou have {in_progress} task(s) in progress. Let's keep the momentum going! 🌟",
                        motivation_level="encouraging",
                        scheduled_time=now,
                        status="pending"
                    )
                    reminders_to_create.append(reminder)
                    break
        
        # 3. If no specific reminders, generate general motivation
        if len(reminders_to_create) == 0:
            reminder = self.generate_custom_motivation(db, user_id, now)
            reminders_to_create.append(reminder)
        
        # Ensure we always return at least one reminder
        if len(reminders_to_create) == 0:
            # Fallback: create a generic motivational reminder
            reminder = ReminderDB(
                user_id=user_id,
                reminder_type="motivation",
                title="Keep Going! 💪",
                message="You're doing great! Remember: every small step counts towards your goals. Keep up the excellent work! 🌟",
                motivation_level="encouraging",
                scheduled_time=now,
                status="pending"
            )
            reminders_to_create.append(reminder)
        
        return reminders_to_create
