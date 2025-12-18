"""
Productivity Analyzer - Analyzes user activity patterns to identify
productive hours and low-energy periods.

Feature 2 → Sub Feature 3
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from features.productivity.models import ActivityLogDB, UserProductivityProfileDB


class ProductivityAnalyzer:
    """
    Analyzes user activity patterns to determine:
    - High productivity time windows
    - Low energy periods
    - Optimal reminder times
    """
    
    def __init__(self):
        self.min_activities_for_analysis = 10
        
    def analyze_user_productivity(self, db: Session, user_id: str = "default_user") -> Dict:
        """
        Analyze user's activity patterns and return productivity insights
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Dict with productivity windows and statistics
        """
        # Get recent activities (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        activities = db.query(ActivityLogDB).filter(
            ActivityLogDB.user_id == user_id,
            ActivityLogDB.timestamp >= thirty_days_ago
        ).all()
        
        if len(activities) < self.min_activities_for_analysis:
            return self._default_productivity_profile()
        
        # Analyze hourly activity distribution
        hourly_activity = defaultdict(int)
        task_completions_by_hour = defaultdict(int)
        
        for activity in activities:
            hour = activity.timestamp.hour
            hourly_activity[hour] += 1
            
            if activity.activity_type == "task_completed":
                task_completions_by_hour[hour] += 1
        
        # Calculate productivity score per hour (completions / activities)
        hourly_productivity = {}
        for hour in range(24):
            if hourly_activity[hour] > 0:
                hourly_productivity[hour] = task_completions_by_hour[hour] / hourly_activity[hour]
            else:
                hourly_productivity[hour] = 0
        
        # Identify high productivity windows (top 25% productive hours with activity)
        active_hours = {h: score for h, score in hourly_productivity.items() if hourly_activity[h] >= 2}
        if active_hours:
            sorted_hours = sorted(active_hours.items(), key=lambda x: x[1], reverse=True)
            top_threshold = len(sorted_hours) // 4 or 1
            high_productivity_hours = [h for h, _ in sorted_hours[:top_threshold]]
        else:
            high_productivity_hours = [9, 10, 14, 15]  # Default work hours
        
        # Identify low energy hours (hours with minimal or no activity)
        low_energy_hours = [h for h in range(24) if hourly_activity[h] == 0 and h not in high_productivity_hours]
        
        # Group consecutive hours into ranges
        high_prod_ranges = self._group_into_ranges(high_productivity_hours)
        low_energy_ranges = self._group_into_ranges(low_energy_hours)
        
        # Calculate response metrics
        response_times = self._calculate_response_times(db, user_id)
        
        return {
            "high_productivity_hours": high_prod_ranges,
            "low_energy_hours": low_energy_ranges,
            "total_activities": len(activities),
            "completed_tasks": sum(1 for a in activities if a.activity_type == "task_completed"),
            "missed_tasks": sum(1 for a in activities if a.activity_type == "task_missed"),
            "average_response_time_minutes": response_times["average"],
            "most_active_hours": sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _group_into_ranges(self, hours: List[int]) -> List[Dict[str, int]]:
        """Group consecutive hours into ranges"""
        if not hours:
            return []
        
        hours = sorted(hours)
        ranges = []
        start = hours[0]
        end = hours[0]
        
        for hour in hours[1:]:
            if hour == end + 1:
                end = hour
            else:
                ranges.append({"start": start, "end": end})
                start = hour
                end = hour
        
        ranges.append({"start": start, "end": end})
        return ranges
    
    def _calculate_response_times(self, db: Session, user_id: str) -> Dict:
        """Calculate average time between reminder delivery and user action"""
        # This is a placeholder - full implementation would track reminder->action timing
        return {
            "average": None,
            "median": None
        }
    
    def _default_productivity_profile(self) -> Dict:
        """Return default productivity profile for new users"""
        return {
            "high_productivity_hours": [{"start": 9, "end": 12}, {"start": 14, "end": 17}],
            "low_energy_hours": [{"start": 0, "end": 7}, {"start": 22, "end": 23}],
            "total_activities": 0,
            "completed_tasks": 0,
            "missed_tasks": 0,
            "average_response_time_minutes": None,
            "most_active_hours": []
        }
    
    def get_optimal_reminder_time(self, db: Session, user_id: str = "default_user") -> datetime:
        """
        Calculate the optimal time to send next reminder based on user's productivity pattern
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Optimal datetime for next reminder
        """
        profile = self.analyze_user_productivity(db, user_id)
        high_prod_hours = profile["high_productivity_hours"]
        
        now = datetime.now()
        current_hour = now.hour
        
        # Find next high productivity window
        for range_dict in high_prod_hours:
            start_hour = range_dict["start"]
            
            if start_hour > current_hour:
                # Schedule for today
                return now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # If no window today, schedule for tomorrow's first high productivity window
        if high_prod_hours:
            next_day = now + timedelta(days=1)
            start_hour = high_prod_hours[0]["start"]
            return next_day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # Default: schedule for 9 AM next day
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    def should_send_reminder_now(self, db: Session, user_id: str = "default_user") -> bool:
        """
        Determine if current time is appropriate for sending a reminder
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            True if reminder should be sent now, False otherwise
        """
        profile = self.analyze_user_productivity(db, user_id)
        current_hour = datetime.now().hour
        
        # Check if current hour is in low energy period
        for range_dict in profile["low_energy_hours"]:
            if range_dict["start"] <= current_hour <= range_dict["end"]:
                return False
        
        # Check if in high productivity period (best time)
        for range_dict in profile["high_productivity_hours"]:
            if range_dict["start"] <= current_hour <= range_dict["end"]:
                return True
        
        # Neutral time - allow reminders
        return True
