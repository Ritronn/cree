"""
Categorization Engine for the Eisenhower Matrix Task Management system.

Tries Groq AI classification first, falls back to formula-based scoring.
"""
from datetime import datetime
from django.utils import timezone


def calculate_urgency_score(deadline):
    """
    Calculate urgency score based on time until deadline.

    Returns float 0.0 - 1.0
    """
    now = timezone.now()
    time_until_deadline = deadline - now
    hours_remaining = time_until_deadline.total_seconds() / 3600

    if hours_remaining <= 24:
        return 1.0
    elif hours_remaining <= 48:
        return 0.8
    elif hours_remaining <= 168:   # 1 week
        return 0.5
    elif hours_remaining <= 336:   # 2 weeks
        return 0.3
    else:
        return 0.1


def calculate_importance_score(task):
    """
    Calculate importance score based on task attributes.

    Uses available fields; handles simplified and full model gracefully.
    Returns float 0.0 - 1.0
    """
    score = 0.0

    # Graded assignment bonus (if field exists)
    if getattr(task, 'is_graded', False):
        score += 0.4

    # High time estimate bonus (>4 hours)
    if task.estimated_time_hours and float(task.estimated_time_hours) > 4:
        score += 0.3

    # Core course bonus (if course FK exists)
    course = getattr(task, 'course', None)
    if course and getattr(course, 'is_core', False):
        score += 0.2

    # User high priority bonus (if field exists)
    user_priority = getattr(task, 'user_priority', 'medium')
    if user_priority == 'high':
        score += 0.3

    # Exam related bonus (if field exists)
    if getattr(task, 'is_exam_related', False):
        score += 0.2

    return min(score, 1.0)


def assign_quadrant(urgency_score, importance_score):
    """
    Assign task to Eisenhower Matrix quadrant based on urgency and importance scores.
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
    Orchestrate full task categorization.

    1. Try Groq AI classification first.
    2. Fall back to formula-based scoring if Groq fails/unavailable.
    3. Returns None if task is manually categorized.

    Returns dict: {urgency_score, importance_score, quadrant}
    """
    if task.is_manually_categorized:
        return None

    # Try Groq AI first
    try:
        from .groq_classifier import classify_with_groq
        groq_result = classify_with_groq(
            title=task.title,
            description=getattr(task, 'description', '') or '',
            deadline=task.deadline,
            estimated_hours=float(task.estimated_time_hours),
        )
        if groq_result:
            return {
                'urgency_score': groq_result['urgency_score'],
                'importance_score': groq_result['importance_score'],
                'quadrant': groq_result['quadrant'],
            }
    except Exception:
        pass  # Fall through to formula

    # Formula-based fallback
    urgency_score = calculate_urgency_score(task.deadline)
    importance_score = calculate_importance_score(task)
    quadrant = assign_quadrant(urgency_score, importance_score)

    return {
        'urgency_score': urgency_score,
        'importance_score': importance_score,
        'quadrant': quadrant,
    }
