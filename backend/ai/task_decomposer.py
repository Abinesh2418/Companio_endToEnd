"""
Intelligent Task Breakdown Engine
Rule-based logic to decompose goals into structured weekly and daily tasks.
"""

from typing import List, Dict, Any
from features.goals.models import GoalResponse
from features.tasks.models import Task


class TaskDecomposer:
    """
    Decomposes high-level goals into structured weekly and daily tasks
    using rule-based logic.
    """
    
    # Knowledge base for common learning topics
    TOPIC_TEMPLATES = {
        "react": {
            "foundation": ["JSX Syntax", "Components Basics", "Props"],
            "intermediate": ["State Management", "Hooks (useState, useEffect)", "Event Handling"],
            "advanced": ["Context API", "Custom Hooks", "Performance Optimization"],
            "project": ["Mini Project"]
        },
        "python": {
            "foundation": ["Syntax & Variables", "Data Types", "Control Flow"],
            "intermediate": ["Functions", "OOP Basics", "File Handling"],
            "advanced": ["Decorators", "Generators", "Async Programming"],
            "project": ["CLI Application"]
        },
        "javascript": {
            "foundation": ["Variables & Types", "Functions", "Arrays & Objects"],
            "intermediate": ["DOM Manipulation", "Async/Await", "Promises"],
            "advanced": ["Closures", "Prototypes", "ES6+ Features"],
            "project": ["Interactive Web App"]
        },
        "data_structures": {
            "foundation": ["Arrays", "Linked Lists", "Stacks & Queues"],
            "intermediate": ["Trees", "Hash Tables", "Graphs"],
            "advanced": ["Advanced Trees", "Dynamic Programming", "Algorithm Analysis"],
            "project": ["Algorithm Implementation"]
        },
        "default": {
            "foundation": ["Introduction & Setup", "Basic Concepts", "Core Fundamentals"],
            "intermediate": ["Intermediate Topics", "Practical Applications", "Best Practices"],
            "advanced": ["Advanced Concepts", "Optimization Techniques", "Real-world Scenarios"],
            "project": ["Capstone Project"]
        }
    }
    
    def __init__(self):
        self.task_counter = 0
    
    def detect_topic(self, goal_title: str) -> str:
        """
        Detect the learning topic from goal title.
        Returns the template key or 'default'.
        """
        title_lower = goal_title.lower()
        
        for topic in self.TOPIC_TEMPLATES.keys():
            if topic in title_lower:
                return topic
        
        return "default"
    
    def generate_tasks_for_goal(self, goal: GoalResponse) -> List[Task]:
        """
        Generate structured weekly and daily tasks for a given goal.
        
        Args:
            goal: The GoalResponse object to break down
            
        Returns:
            List of Task objects organized by weeks
        """
        tasks = []
        topic = self.detect_topic(goal.title)
        template = self.TOPIC_TEMPLATES.get(topic, self.TOPIC_TEMPLATES["default"])
        
        # Determine task distribution based on intensity
        tasks_per_week = self._get_tasks_per_week(goal.intensity)
        
        # Get all task titles based on duration
        all_task_titles = self._distribute_tasks_across_weeks(
            template, 
            goal.duration_weeks,
            tasks_per_week
        )
        
        # Create Task objects with dependencies
        task_id_map = {}  # Map (week, order) to task_id for dependencies
        
        for week_num, week_tasks in enumerate(all_task_titles, start=1):
            for order, task_title in enumerate(week_tasks):
                task = Task(
                    goal_id=goal.id,
                    week_number=week_num,
                    day_number=None,  # Week-level tasks
                    title=task_title,
                    description=f"Complete {task_title} for {goal.title}",
                    status="Not Started",
                    dependencies=[],
                    order=order
                )
                
                # Add dependencies: each task depends on the previous one
                if order > 0:
                    prev_task_key = (week_num, order - 1)
                    if prev_task_key in task_id_map:
                        task.dependencies.append(task_id_map[prev_task_key])
                elif week_num > 1:
                    # First task of a week depends on last task of previous week
                    prev_week_last_task_key = (week_num - 1, len(all_task_titles[week_num - 2]) - 1)
                    if prev_week_last_task_key in task_id_map:
                        task.dependencies.append(task_id_map[prev_week_last_task_key])
                
                task_id_map[(week_num, order)] = task.id
                tasks.append(task)
        
        return tasks
    
    def _get_tasks_per_week(self, intensity: str) -> int:
        """Determine number of tasks per week based on intensity"""
        intensity_map = {
            "Light": 2,
            "Normal": 3,
            "Aggressive": 4,
            # Support alternative naming
            "Relaxed": 2,
            "Intense": 4
        }
        return intensity_map.get(intensity, 3)
    
    def _distribute_tasks_across_weeks(
        self, 
        template: Dict[str, List[str]], 
        duration_weeks: int,
        tasks_per_week: int
    ) -> List[List[str]]:
        """
        Distribute tasks from template across the specified number of weeks.
        
        Returns:
            List of weeks, where each week contains a list of task titles
        """
        # Flatten template tasks in logical order
        all_tasks = []
        for category in ["foundation", "intermediate", "advanced", "project"]:
            all_tasks.extend(template.get(category, []))
        
        # Calculate total tasks needed
        total_tasks_needed = duration_weeks * tasks_per_week
        
        # Adjust task list to match duration
        if len(all_tasks) < total_tasks_needed:
            # Expand tasks by adding sub-tasks or practice tasks
            all_tasks = self._expand_task_list(all_tasks, total_tasks_needed)
        elif len(all_tasks) > total_tasks_needed:
            # Prioritize most important tasks
            all_tasks = all_tasks[:total_tasks_needed]
        
        # Distribute into weeks
        weekly_tasks = []
        for week in range(duration_weeks):
            start_idx = week * tasks_per_week
            end_idx = start_idx + tasks_per_week
            week_task_list = all_tasks[start_idx:end_idx]
            weekly_tasks.append(week_task_list)
        
        return weekly_tasks
    
    def _expand_task_list(self, tasks: List[str], target_count: int) -> List[str]:
        """Expand task list by adding practice and review tasks"""
        expanded = tasks.copy()
        
        while len(expanded) < target_count:
            if len(expanded) < target_count - 1:
                expanded.append(f"Practice & Review")
            else:
                expanded.append("Final Review")
        
        return expanded


def check_task_dependencies(task: Task, all_tasks: List[Task]) -> bool:
    """
    Check if a task's dependencies are completed.
    
    Args:
        task: The task to check
        all_tasks: List of all tasks for the goal
        
    Returns:
        True if all dependencies are completed, False otherwise
    """
    if not task.dependencies:
        return True
    
    task_map = {t.id: t for t in all_tasks}
    
    for dep_id in task.dependencies:
        dep_task = task_map.get(dep_id)
        if not dep_task or dep_task.status != "Completed":
            return False
    
    return True
