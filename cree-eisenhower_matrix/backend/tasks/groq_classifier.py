"""
Groq AI-based task classifier for Eisenhower Matrix categorization.
Falls back to formula-based scoring if Groq API is unavailable.
"""
import os
import json
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


def classify_with_groq(title, description, deadline, estimated_hours):
    """
    Use Groq AI to classify a task into the Eisenhower Matrix.

    Returns dict with urgency_score, importance_score, quadrant, reasoning
    or None if Groq is unavailable.
    """
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_api_key or groq_api_key == 'your-groq-api-key-here':
        logger.info("Groq API key not set — using formula-based fallback")
        return None

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)

        now = timezone.now()
        if hasattr(deadline, 'strftime'):
            deadline_str = deadline.strftime('%Y-%m-%d %H:%M UTC')
            hours_until = (deadline - now).total_seconds() / 3600
        else:
            deadline_str = str(deadline)
            hours_until = 48

        prompt = f"""You are an expert productivity coach. Classify this task using the Eisenhower Matrix.

Task Title: {title}
Description: {description or 'No description provided'}
Deadline: {deadline_str} ({max(0, round(hours_until, 1))} hours from now)
Estimated Time: {estimated_hours} hours

Eisenhower Matrix rules:
- URGENT = deadline within 24h → urgency 1.0, within 48h → 0.8, within 1 week → 0.5, within 2 weeks → 0.3, beyond → 0.1
- IMPORTANT = task has significant consequences, is goal-aligned, requires expertise, or is exam/work-critical
- Quadrants: urgent_important (Do First), important_not_urgent (Schedule), urgent_not_important (Delegate), neither (Eliminate)

Respond ONLY with valid JSON, no explanation:
{{
  "urgency_score": 0.0-1.0,
  "importance_score": 0.0-1.0,
  "quadrant": "urgent_important|important_not_urgent|urgent_not_important|neither",
  "reasoning": "one sentence explanation"
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a productivity assistant that classifies tasks. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200,
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)

        # Validate and clamp scores
        urgency = max(0.0, min(1.0, float(result.get('urgency_score', 0.5))))
        importance = max(0.0, min(1.0, float(result.get('importance_score', 0.5))))
        quadrant = result.get('quadrant', 'neither')
        if quadrant not in ['urgent_important', 'important_not_urgent', 'urgent_not_important', 'neither']:
            quadrant = _assign_quadrant(urgency, importance)

        logger.info(f"Groq classified '{title}' → {quadrant} (U:{urgency} I:{importance})")
        return {
            'urgency_score': urgency,
            'importance_score': importance,
            'quadrant': quadrant,
            'reasoning': result.get('reasoning', ''),
        }

    except json.JSONDecodeError as e:
        logger.warning(f"Groq returned invalid JSON: {e}. Falling back to formula.")
        return None
    except Exception as e:
        logger.warning(f"Groq classification failed: {e}. Falling back to formula.")
        return None


def _assign_quadrant(urgency_score, importance_score):
    """Assign quadrant based on urgency/importance thresholds."""
    if urgency_score >= 0.6 and importance_score >= 0.6:
        return 'urgent_important'
    elif urgency_score < 0.6 and importance_score >= 0.6:
        return 'important_not_urgent'
    elif urgency_score >= 0.6 and importance_score < 0.6:
        return 'urgent_not_important'
    else:
        return 'neither'
