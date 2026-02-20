"""
Categorization Engine for the Eisenhower Matrix Task Management system.

This module provides functions to calculate urgency and importance scores,
and assign tasks to appropriate quadrants in the Eisenhower Matrix.
"""
from datetime import datetime
from django.utils import timezone


def calculate_urgency_score(deadline):
    """
    Calculate urgency score based on time until deadline.
    
    Args:
        deadline: datetime object representing task deadline
        
    Returns:
        Float between 0.0 and 1.0
        
    Scoring rules (Requirements 2.2):
        - Within 24 hours: 1.0
        - Within 48 hours: 0.8
        - Within 1 week (168 hours): 0.5
        - Within 2 weeks (336 hours): 0.3
        - Beyond 2 weeks: 0.1
    """
    # Get current time (timezone-aware)
    now = timezone.now()
    
    # Calculate time until deadline
    time_until_deadline = deadline - now
    hours_remaining = time_until_deadline.total_seconds() / 3600
    
    # Apply scoring rules based on hours remaining
    if hours_remaining <= 24:
        return 1.0
    elif hours_remaining <= 48:
        return 0.8
    elif hours_remaining <= 168:  # 1 week
        return 0.5
    elif hours_remaining <= 336:  # 2 weeks
        return 0.3
    else:
        return 0.1


def calculate_importance_score(task):
    """
    Calculate importance score based on task attributes.
    
    Args:
        task: Task object with attributes (is_graded, estimated_time_hours, course.is_core, 
              user_priority, is_exam_related)
        
    Returns:
        Float between 0.0 and 1.0
        
    Scoring rules (Requirements 2.3, 2.4):
        - Graded assignment: +0.4
        - High time estimate (>4 hours): +0.3
        - Core course: +0.2
        - User high priority: +0.3
        - Exam related: +0.2
        - Cap at 1.0
    """
    score = 0.0
    
    # Graded assignment bonus
    if task.is_graded:
        score += 0.4
    
    # High time estimate bonus (>4 hours)
    if task.estimated_time_hours and task.estimated_time_hours > 4:
        score += 0.3
    
    # Core course bonus
    if task.course and task.course.is_core:
        score += 0.2
    
    # User high priority bonus
    if task.user_priority == 'high':
        score += 0.3
    
    # Exam related bonus
    if task.is_exam_related:
        score += 0.2
    
    # Cap at 1.0
    return min(score, 1.0)


def assign_quadrant(urgency_score, importance_score):
    """
    Assign task to Eisenhower Matrix quadrant based on urgency and importance scores.
    
    Args:
        urgency_score: Float between 0.0 and 1.0
        importance_score: Float between 0.0 and 1.0
        
    Returns:
        String representing quadrant: 'urgent_important', 'important_not_urgent',
        'urgent_not_important', or 'neither'
        
    Mapping rules (Requirements 2.5, 2.6, 2.7, 2.8):
        - urgency >= 0.6 AND importance >= 0.6: urgent_important
        - urgency < 0.6 AND importance >= 0.6: important_not_urgent
        - urgency >= 0.6 AND importance < 0.6: urgent_not_important
        - urgency < 0.6 AND importance < 0.6: neither
    """
    if urgency_score >= 0.6 and importance_score >= 0.6:
        return 'urgent_important'
    elif urgency_score < 0.6 and importance_score >= 0.6:
        return 'important_not_urgent'
    elif urgency_score >= 0.6 and importance_score < 0.6:
        return 'urgent_not_important'
    else:
        return 'neither'


def categorize_task(task):
    """
    Orchestrate full task categorization by calculating scores and assigning quadrant.
    
    Args:
        task: Task object with deadline and other attributes
        
    Returns:
        Dictionary with keys: urgency_score, importance_score, quadrant
        
    Behavior (Requirements 2.9, 3.2):
        - Respects is_manually_categorized flag (returns None if True)
        - Calculates urgency score from deadline
        - Calculates importance score from task attributes
        - Assigns quadrant based on scores
    """
    # Respect manual categorization flag
    if task.is_manually_categorized:
        return None
    
    # Calculate scores
    urgency_score = calculate_urgency_score(task.deadline)
    importance_score = calculate_importance_score(task)
    
    # Assign quadrant
    quadrant = assign_quadrant(urgency_score, importance_score)
    
    return {
        'urgency_score': urgency_score,
        'importance_score': importance_score,
        'quadrant': quadrant
    }
