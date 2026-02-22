import os
import json
import logging
import re
from groq import Groq

logger = logging.getLogger(__name__)

def generate_flashcards_from_topic(topic, description="", scope="specific_topics"):
    """
    Use Groq AI to generate a set of short, high-quality revision cards
    (Que-Que Cards) for a specific topic. Imitates the concise explanatory style
    of GeeksForGeeks.
    """
    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment")
        return []

    client = Groq(api_key=api_key)

    # Determine count and scope instructions
    if scope == "full_syllabus":
        count = 15
        scope_instruction = "Cover the entire syllabus comprehensively from top to bottom."
    elif scope == "overview":
        count = 3
        scope_instruction = "Provide only a high-level overview of the topic."
    else:  # specific_topics
        count = 5
        scope_instruction = "Focus strictly on the specific key concepts of this topic."

    prompt = f"""You are an expert educator. Create {count} high-quality revision cards (Que-Que Cards) for the topic: "{topic}".
Description context: {description}
Scope instructions: {scope_instruction}

Each card should have:
1. A clear, concise question, concept name, or sub-topic name in broad terms.
2. A short, "GeeksForGeeks style" explanation or answer (bullet points preferred, very concise).

Respond ONLY with a JSON array of objects:
[
  {{
    "question": "What is ...?",
    "answer": "Concise explanation..."
  }},
  ...
]

Keep it extremely short and useful for last-minute revision."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional teacher. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()
        
        # Robustly find the JSON array [ ... ]
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            content = match.group(0)
        
        cards = json.loads(content)
        return cards
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return []
