"""
Gemini-based Adaptive MCQ Generation Service
Integrates with the existing content processing pipeline
"""
import google.generativeai as genai
import json
import re
from django.conf import settings
from django.utils import timezone

# Configure Gemini API
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', 'AIzaSyAL99Z0RtQuCqKM_cvSay6yIVDsHGvDntc')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def clean_and_parse_json(raw_text: str, context: str = "Gemini") -> list:
    """
    Robust JSON parsing with multiple fallback strategies.
    
    Args:
        raw_text: Raw response text from Gemini
        context: Context string for logging
    
    Returns:
        Parsed JSON list
    
    Raises:
        json.JSONDecodeError: If all parsing strategies fail
    """
    # Clean markdown formatting
    cleaned = re.sub(r'^```json\s*', '', raw_text)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    
    # Remove control characters that break JSON parsing (except newlines for now)
    cleaned = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', ' ', cleaned)
    
    # Replace smart quotes with regular quotes
    cleaned = cleaned.replace('"', '"').replace('"', '"')
    cleaned = cleaned.replace(''', "'").replace(''', "'")
    
    # Try to find and extract just the JSON array if there's extra text
    json_match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    
    print(f"[{context}] Attempting to parse JSON (length: {len(cleaned)} chars)")
    
    try:
        # First attempt: direct parsing
        questions = json.loads(cleaned)
        
        # Post-process: remove newlines from all string values
        for q in questions:
            if 'question' in q:
                q['question'] = q['question'].replace('\n', ' ').replace('\r', ' ')
            if 'explanation' in q:
                q['explanation'] = q['explanation'].replace('\n', ' ').replace('\r', ' ')
            if 'concept' in q:
                q['concept'] = q['concept'].replace('\n', ' ').replace('\r', ' ')
            if 'options' in q and isinstance(q['options'], dict):
                for key in q['options']:
                    q['options'][key] = q['options'][key].replace('\n', ' ').replace('\r', ' ')
        
        return questions
        
    except json.JSONDecodeError as e:
        print(f"[{context}] First parse failed at position {e.pos}: {e.msg}")
        print(f"[{context}] Context around error: ...{cleaned[max(0, e.pos-50):e.pos+50]}...")
        
        # Second attempt: Try to fix common issues
        # Fix trailing commas
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        
        # Replace newlines within string values (between quotes)
        # This is a heuristic approach
        def replace_newlines_in_strings(match):
            return match.group(0).replace('\n', ' ').replace('\r', ' ')
        
        cleaned = re.sub(r'"[^"]*"', replace_newlines_in_strings, cleaned)
        
        try:
            questions = json.loads(cleaned)
            
            # Post-process again
            for q in questions:
                if 'question' in q:
                    q['question'] = q['question'].replace('\n', ' ').replace('\r', ' ')
                if 'explanation' in q:
                    q['explanation'] = q['explanation'].replace('\n', ' ').replace('\r', ' ')
                if 'concept' in q:
                    q['concept'] = q['concept'].replace('\n', ' ').replace('\r', ' ')
                if 'options' in q and isinstance(q['options'], dict):
                    for key in q['options']:
                        q['options'][key] = q['options'][key].replace('\n', ' ').replace('\r', ' ')
            
            return questions
            
        except json.JSONDecodeError as e2:
            print(f"[{context}] Second parse failed: {e2}")
            print(f"[{context}] Full response (first 1000 chars): {raw_text[:1000]}")
            raise

# User state configuration
USER_STATE_CONFIG = {
    1: {
        "label": "confused",
        "num_questions": 20,
        "difficulty": "beginner",
        "instruction": "The user is confused. Generate 20 SIMPLE questions that reinforce basic understanding. All questions should be easy to build confidence.",
        "take_break": False,
        "difficulty_distribution": "all_easy"
    },
    2: {
        "label": "bored",
        "num_questions": 20,
        "difficulty": "advanced",
        "instruction": "The user is bored. Generate 20 CHALLENGING questions. First 15 should be intermediate-advanced, last 5 should be very difficult to challenge the user.",
        "take_break": False,
        "difficulty_distribution": "progressive_hard"
    },
    3: {
        "label": "overloaded",
        "num_questions": 10,
        "difficulty": "easy",
        "instruction": "The user is overloaded. Generate only 10 EASY questions focusing on key takeaways. Keep it simple and straightforward.",
        "take_break": True,
        "difficulty_distribution": "all_easy"
    },
    4: {
        "label": "focused",
        "num_questions": 20,
        "difficulty": "intermediate-to-advanced",
        "instruction": "The user is focused. Generate 20 questions: First 15 should be intermediate level, last 5 should be significantly harder to test deep understanding.",
        "take_break": False,
        "difficulty_distribution": "progressive"
    },
}


def extract_technical_content(transcript: str) -> str:
    """Extract educational content from transcript."""
    prompt = f"""You are an educational content extractor.
Remove: filler, jokes, timestamps, sponsor segments, "like and subscribe", greetings.
Extract: key concepts, definitions, facts, processes, examples.
Output as structured bullet points grouped by topic.

RAW TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

OUTPUT (bullet points only):"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error extracting content: {e}")
        return transcript  # Fallback to original


def generate_adaptive_mcqs(technical_content: str, user_state: int = 4) -> dict:
    """Generate adaptive MCQs based on user state."""
    if user_state not in USER_STATE_CONFIG:
        user_state = 4  # Default to focused

    config = USER_STATE_CONFIG[user_state]
    num_q = config["num_questions"]
    instruction = config["instruction"]
    difficulty = config["difficulty"]

    prompt = f"""You are an expert quiz generator.

CONTEXT: {instruction}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {num_q}

RULES:
- Generate EXACTLY {num_q} MCQ questions
- Each question must be DIRECTLY answerable from the provided content
- Each question must have 4 options (A, B, C, D)
- Only one correct answer
- Include brief explanation for correct answer
- Vary question types (definition, application, analysis)

CONTENT:
\"\"\"
{technical_content}
\"\"\"

Return ONLY valid JSON array (no markdown, no extra text):
[{{
  "question": "Question text?",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "answer": "A",
  "explanation": "Why A is correct."
}}]"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        questions = clean_and_parse_json(raw, "Gemini MCQ")

        return {
            "user_state": config["label"],
            "difficulty": difficulty,
            "num_questions": len(questions),
            "take_break_suggestion": config["take_break"],
            "questions": questions,
            "success": True
        }
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        return {
            "success": False,
            "error": str(e),
            "questions": []
        }


def generate_test2_questions(topic: str, user_state: int, weak_concepts: set, score: float) -> dict:
    """
    Generate Test 2: ALWAYS 15 simplified + 5 harder questions.
    
    Args:
        topic: Topic name
        user_state: Not used - Test 2 is always simplified
        weak_concepts: Set of concepts user got wrong
        score: Test 1 score percentage
    
    Returns:
        dict with questions and metadata
    """
    weak_list = ', '.join(weak_concepts) if weak_concepts else 'None - student did well'

    # Test 2 is ALWAYS: 15 easier questions + 5 harder questions
    prompt = f"""You are an expert quiz generator creating TEST 2 (follow-up test) for the topic: {topic}

CONTEXT: Student scored {score:.0f}% on Test 1.
WEAK CONCEPTS from Test 1: {weak_list}

TEST 2 STRUCTURE (ALWAYS):
- Questions 1-15: EASIER/SIMPLIFIED questions
  * If weak concepts exist: Focus on those concepts with clearer, simpler questions
  * If no weak concepts: Cover fundamental concepts in a straightforward way
- Questions 16-20: HARDER questions
  * Challenge the student with advanced concepts or tricky scenarios
  * Test deeper understanding and application

RULES:
- Generate EXACTLY 20 MCQ questions about {topic}
- Each question must have 4 options (A, B, C, D)
- Only one correct answer
- Include brief explanation for correct answer (single line, no newlines)
- Questions 1-15 should be noticeably EASIER than typical questions
- Questions 16-20 should be CHALLENGING
- CRITICAL: Do NOT use newlines, line breaks, or \\n characters anywhere in the JSON
- CRITICAL: Keep all text on single lines - no multi-line strings
- CRITICAL: Use spaces instead of newlines for readability in explanations

Return ONLY valid JSON array (no markdown, no extra text, no newlines in strings):
[
  {{
    "question": "Question text here?",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "answer": "B",
    "explanation": "Brief explanation why B is correct",
    "concept": "Specific concept being tested",
    "difficulty_level": "easy|hard"
  }}
]"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        questions = clean_and_parse_json(raw_text, "Gemini Test2")
        
        print(f"[Gemini Test2] Generated {len(questions)} questions (15 easier + 5 harder) for topic: {topic}")
        
        return {
            "success": True,
            "num_questions": len(questions),
            "difficulty": "adaptive",
            "topic": topic,
            "questions": questions
        }
    except json.JSONDecodeError as e:
        print(f"[Gemini Test2] JSON parsing error: {e}")
        print(f"[Gemini Test2] Raw response (first 500 chars): {raw_text[:500]}")
        return {
            "success": False,
            "error": f"Failed to parse Gemini response: {str(e)}",
            "questions": []
        }
    except Exception as e:
        print(f"[Gemini Test2] Error generating questions: {e}")
        return {
            "success": False,
            "error": str(e),
            "questions": []
        }


def generate_questions_from_topic(topic: str, user_state: int = 4) -> dict:
    """
    Generate MCQs directly from a topic name (e.g., "Python", "Machine Learning").
    
    Args:
        topic: Topic name or subject (e.g., "Python", "Data Structures")
        user_state: 1=confused, 2=bored, 3=overloaded, 4=focused
    
    Returns:
        dict with questions and metadata
    """
    if user_state not in USER_STATE_CONFIG:
        user_state = 4  # Default to focused

    config = USER_STATE_CONFIG[user_state]
    num_q = config["num_questions"]
    instruction = config["instruction"]
    difficulty = config["difficulty"]
    distribution = config.get("difficulty_distribution", "progressive")

    # Build difficulty-specific instructions
    if distribution == "all_easy":
        difficulty_guide = "All questions should be EASY level - testing basic concepts and definitions."
    elif distribution == "progressive":
        difficulty_guide = f"Questions 1-15: INTERMEDIATE level. Questions 16-{num_q}: HARD level (challenging, requiring deep understanding)."
    elif distribution == "progressive_hard":
        difficulty_guide = f"Questions 1-15: INTERMEDIATE-ADVANCED level. Questions 16-{num_q}: VERY HARD level (expert-level, tricky scenarios)."
    else:
        difficulty_guide = "Vary difficulty appropriately."

    prompt = f"""You are an expert quiz generator for the topic: {topic}

CONTEXT: {instruction}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {num_q}

DIFFICULTY DISTRIBUTION:
{difficulty_guide}

RULES:
- Generate EXACTLY {num_q} MCQ questions about {topic}
- Follow the difficulty distribution strictly
- Cover fundamental concepts, practical applications, and best practices
- Each question must have 4 options (A, B, C, D)
- Only one correct answer
- Include brief explanation for correct answer (single line, no newlines)
- Vary question types (definition, application, analysis, problem-solving)
- Questions should be educational and test real understanding
- For HARD questions: use edge cases, tricky scenarios, or require synthesis of multiple concepts
- CRITICAL: Do NOT use newlines, line breaks, or \\n characters anywhere in the JSON
- CRITICAL: Keep all text on single lines - no multi-line strings
- CRITICAL: Use spaces instead of newlines for readability in explanations

Return ONLY valid JSON array (no markdown, no extra text, no newlines in strings):
[
  {{
    "question": "Question text here?",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "answer": "B",
    "explanation": "Brief explanation why B is correct",
    "concept": "Specific concept being tested",
    "difficulty_level": "easy|intermediate|hard"
  }}
]"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        questions = clean_and_parse_json(raw_text, "Gemini")
        
        print(f"[Gemini] Generated {len(questions)} questions for topic: {topic} (state: {config['label']})")
        
        return {
            "success": True,
            "num_questions": len(questions),
            "difficulty": difficulty,
            "user_state": user_state,
            "topic": topic,
            "questions": questions
        }
    except json.JSONDecodeError as e:
        print(f"[Gemini] JSON parsing error: {e}")
        print(f"[Gemini] Raw response (first 500 chars): {raw_text[:500]}")
        return {
            "success": False,
            "error": f"Failed to parse Gemini response: {str(e)}",
            "questions": []
        }
    except Exception as e:
        print(f"[Gemini] Error generating questions: {e}")
        return {
            "success": False,
            "error": str(e),
            "questions": []
        }


def process_content_and_generate_mcqs(transcript: str, user_state: int = 4) -> dict:
    """
    Full pipeline: Extract technical content -> Generate adaptive MCQs

    Args:
        transcript: Raw transcript text
        user_state: 1=confused, 2=bored, 3=overloaded, 4=focused

    Returns:
        dict with questions and metadata
    """
    print(f"[Gemini MCQ] Extracting technical content...")
    technical_content = extract_technical_content(transcript)

    print(f"[Gemini MCQ] Generating MCQs for user state: {USER_STATE_CONFIG.get(user_state, {}).get('label', 'focused')}...")
    result = generate_adaptive_mcqs(technical_content, user_state)

    # Add extracted content for reference
    result["extracted_content"] = technical_content

    return result


# ============================================================================
# DJANGO MODEL INTEGRATION
# ============================================================================

def create_assessment_from_session(session_id, user, content):
    """
    Create assessment with adaptive questions based on study session.
    Uses workspace name as the topic for question generation.

    Args:
        session_id: StudySession ID
        user: User instance
        content: Content instance (can be None)

    Returns:
        Assessment instance with generated questions
    """
    from .models import Assessment, Question, StudySession

    # Get the session to extract workspace name
    try:
        session = StudySession.objects.get(id=session_id)
        topic = session.workspace_name or "General Programming"
    except StudySession.DoesNotExist:
        topic = "General Programming"

    print(f"[Gemini] Generating questions for topic: {topic}")

    # Default to focused state (state detection can be added later)
    learning_state = 4

    # Generate questions based on workspace name/topic
    result = generate_questions_from_topic(topic, learning_state)

    if not result.get('success'):
        raise Exception(f"MCQ generation failed: {result.get('error')}")

    # Map difficulty to numeric level
    difficulty_map = {
        'beginner': 1,
        'easy': 1,
        'intermediate': 2,
        'intermediate-to-advanced': 2,
        'advanced': 3,
        'hard': 3,
    }
    difficulty_level = difficulty_map.get(result['difficulty'], 2)

    # Create Assessment
    assessment = Assessment.objects.create(
        content=content,
        user=user,
        session_id=session_id,
        test_number=1,
        difficulty_level=difficulty_level,
        total_questions=result['num_questions']
    )

    # Create Questions
    for idx, q_data in enumerate(result['questions']):
        # Convert options dict to list
        options_dict = q_data['options']
        options_list = [
            options_dict.get('A', ''),
            options_dict.get('B', ''),
            options_dict.get('C', ''),
            options_dict.get('D', '')
        ]

        # Get correct answer index
        answer_letter = q_data['answer'].upper()
        correct_index = ord(answer_letter) - ord('A')

        Question.objects.create(
            assessment=assessment,
            question_text=q_data['question'],
            options=options_list,
            correct_answer_index=correct_index,
            explanation=q_data.get('explanation', ''),
            difficulty=difficulty_level,
            concept=q_data.get('concept', 'General'),
            order=idx
        )

    # Set test_available_until on the session
    from datetime import timedelta
    try:
        session.test_available_until = timezone.now() + timedelta(hours=6)
        session.save()
    except:
        pass

    print(f"[Gemini] Created assessment {assessment.id} with {result['num_questions']} questions for topic: {topic}")

    return assessment


def create_followup_assessment(test1_assessment_id, score_percentage=None):
    """
    Create Test 2 (adaptive retry) based on Test 1 results.
    Uses workspace name for topic-based question generation.

    - Identifies concepts the user got wrong in Test 1
    - Generates questions based on performance and user state
    - Sets 6-hour expiry window
    - Uses Test 1 score percentage to determine user state

    Args:
        test1_assessment_id: Assessment ID for the completed Test 1
        score_percentage: Test 1 score (0-100) — determines user state

    Returns:
        Assessment instance for Test 2
    """
    from .models import Assessment, Question, UserAnswer, StudySession
    from datetime import timedelta

    try:
        test1 = Assessment.objects.get(id=test1_assessment_id, is_completed=True, test_number=1)
    except Assessment.DoesNotExist:
        raise ValueError("Test 1 not found or not completed")

    # Check if Test 2 already exists
    existing_test2 = Assessment.objects.filter(
        parent_assessment=test1,
        test_number=2
    ).first()
    if existing_test2:
        print(f"[Followup] Test 2 already exists (ID: {existing_test2.id})")
        return existing_test2

    # Get topic from session workspace name
    try:
        session = StudySession.objects.get(id=test1.session_id)
        topic = session.workspace_name or "General Programming"
    except:
        topic = "General Programming"

    # Identify wrong concepts from Test 1
    user_answers = UserAnswer.objects.filter(
        question__assessment=test1,
        user=test1.user
    ).select_related('question')

    wrong_concepts = set()
    all_concepts = set()
    for answer in user_answers:
        all_concepts.add(answer.question.concept)
        if not answer.is_correct:
            wrong_concepts.add(answer.question.concept)

    # Determine user state based on Test 1 score
    if score_percentage is None:
        score_percentage = test1.score or 50
    
    # Map score to user state
    if score_percentage < 40:
        user_state = 1  # confused - simplify
        difficulty_level = 1
    elif score_percentage < 60:
        user_state = 3  # overloaded - reduce questions, simplify
        difficulty_level = 1
    elif score_percentage < 80:
        user_state = 4  # focused - balanced
        difficulty_level = 2
    else:
        user_state = 2  # bored - make it harder
        difficulty_level = 3

    state_label = USER_STATE_CONFIG[user_state]['label']
    print(f"[Followup] Test 1 score: {score_percentage:.0f}% → User state: {state_label}")

    # Build context about weak areas
    wrong_list = ', '.join(wrong_concepts) if wrong_concepts else 'None'
    
    # Generate Test 2 questions with adaptive difficulty
    result = generate_test2_questions(topic, user_state, wrong_concepts, score_percentage)

    if not result.get('success'):
        raise Exception(f"Test 2 generation failed: {result.get('error')}")

    # Create Test 2 assessment
    test2 = Assessment.objects.create(
        content=test1.content,
        user=test1.user,
        session_id=test1.session_id,
        test_number=2,
        parent_assessment=test1,
        expires_at=timezone.now() + timedelta(hours=6),
        difficulty_level=difficulty_level,
        total_questions=result['num_questions']
    )

    # Create questions
    for idx, q_data in enumerate(result['questions']):
        # Convert options dict to list
        options_dict = q_data['options']
        options_list = [
            options_dict.get('A', ''),
            options_dict.get('B', ''),
            options_dict.get('C', ''),
            options_dict.get('D', '')
        ]

        # Get correct answer index
        answer_letter = q_data['answer'].upper()
        correct_index = ord(answer_letter) - ord('A')

        Question.objects.create(
            assessment=test2,
            question_text=q_data['question'],
            options=options_list,
            correct_answer_index=correct_index,
            explanation=q_data.get('explanation', ''),
            difficulty=difficulty_level,
            concept=q_data.get('concept', 'General'),
            order=idx
        )

    print(f"[Followup] Created Test 2 (ID: {test2.id}) with {result['num_questions']} questions")
    print(f"[Followup] Weak concepts from Test 1: {wrong_list}")

    return test2
