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

# User state configuration
USER_STATE_CONFIG = {
    1: {
        "label": "confused",
        "num_questions": 20,
        "difficulty": "beginner",
        "instruction": "The user is confused. Generate SIMPLE questions that reinforce basic understanding.",
        "take_break": False,
    },
    2: {
        "label": "bored",
        "num_questions": 20,
        "difficulty": "advanced",
        "instruction": "The user is bored. Generate CHALLENGING questions that require deeper thinking.",
        "take_break": False,
    },
    3: {
        "label": "overloaded",
        "num_questions": 10,
        "difficulty": "easy",
        "instruction": "The user is overloaded. Generate only 10 EASY questions focusing on key takeaways.",
        "take_break": True,
    },
    4: {
        "label": "focused",
        "num_questions": 20,
        "difficulty": "intermediate-to-advanced",
        "instruction": "The user is focused. Gradually INCREASE difficulty.",
        "take_break": False,
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

        # Strip markdown code fences
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        questions = json.loads(raw)

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

    Args:
        session_id: StudySession ID
        user: User instance
        content: Content instance

    Returns:
        Assessment instance with generated questions
    """
    from .models import Assessment, Question

    # Default to focused state (state detection can be added later)
    learning_state = 4

    # Get content transcript
    transcript = content.transcript
    if not transcript:
        raise ValueError("Content has no transcript to generate questions from")

    # Generate MCQs using Gemini (2-step pipeline)
    result = process_content_and_generate_mcqs(transcript, learning_state)

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
    from .models import StudySession
    from datetime import timedelta
    try:
        session = StudySession.objects.get(id=session_id)
        session.test_available_until = timezone.now() + timedelta(hours=6)
        session.save()
    except StudySession.DoesNotExist:
        pass

    print(f"[Gemini] Created assessment {assessment.id} with {result['num_questions']} questions")

    return assessment


def create_followup_assessment(test1_assessment_id, score_percentage=None):
    """
    Create Test 2 (adaptive retry) based on Test 1 results.

    - Identifies concepts the user got wrong in Test 1
    - Generates simplified questions on weak concepts + some new concepts
    - Sets 6-hour expiry window
    - Uses Test 1 score percentage to determine difficulty

    Args:
        test1_assessment_id: Assessment ID for the completed Test 1
        score_percentage: Test 1 score (0-100) — lower = easier Test 2

    Returns:
        Assessment instance for Test 2
    """
    from .models import Assessment, Question, UserAnswer
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

    # Get content transcript
    transcript = test1.content.transcript
    if not transcript:
        raise ValueError("Content has no transcript for followup test")

    # First extract technical content
    technical_content = extract_technical_content(transcript)

    # Determine difficulty based on Test 1 score
    if score_percentage is None:
        score_percentage = test1.score or 50
    
    if score_percentage < 40:
        difficulty_label = 'beginner'
        difficulty_level = 1
        difficulty_instruction = 'Make questions VERY SIMPLE and fundamental.'
    elif score_percentage < 60:
        difficulty_label = 'easy'
        difficulty_level = 1
        difficulty_instruction = 'Make questions EASIER than Test 1 with clearer explanations.'
    elif score_percentage < 80:
        difficulty_label = 'intermediate'
        difficulty_level = 2
        difficulty_instruction = 'Keep questions at a moderate level, slightly easier for weak concepts.'
    else:
        difficulty_label = 'advanced'
        difficulty_level = 3
        difficulty_instruction = 'Make questions HARDER and more analytical since the student performed well.'

    # Build adaptive prompt for Test 2
    wrong_list = ', '.join(wrong_concepts) if wrong_concepts else 'None'
    all_list = ', '.join(all_concepts)

    prompt = f"""You are an expert quiz generator creating a FOLLOW-UP test.

CONTEXT: A student scored {score_percentage:.0f}% on Test 1.
Concepts they got WRONG: {wrong_list}
All concepts from Test 1: {all_list}

DIFFICULTY: {difficulty_label} — {difficulty_instruction}

TASK: Generate exactly 20 multiple choice questions with this distribution:
- 12 questions: SIMPLIFIED versions of the concepts the student got WRONG. {difficulty_instruction}
- 8 questions: NEW concepts from the content that were NOT in Test 1.

If the student got everything right, generate 10 harder questions + 10 new concept questions.

CONTENT:
\"\"\"
{technical_content}
\"\"\"

Return ONLY valid JSON array (no markdown, no extra text):
[{{
  "question": "Question text?",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "answer": "A",
  "explanation": "Why A is correct.",
  "concept": "Concept being tested"
}}]"""

    try:
        print(f"[Followup] Generating Test 2 for assessment {test1_assessment_id}...")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        questions_data = json.loads(raw)

        if not isinstance(questions_data, list) or len(questions_data) == 0:
            raise ValueError("No valid questions generated for Test 2")

        # Filter valid questions
        valid_questions = [q for q in questions_data if all(k in q for k in ['question', 'options', 'answer', 'explanation'])]

        if not valid_questions:
            raise ValueError("All generated questions are invalid")

        # Create Test 2 assessment with score-based difficulty
        test2 = Assessment.objects.create(
            content=test1.content,
            user=test1.user,
            session=test1.session,
            test_number=2,
            parent_assessment=test1,
            expires_at=timezone.now() + timedelta(hours=6),
            difficulty_level=difficulty_level,
            total_questions=len(valid_questions)
        )

        # Create questions
        for idx, q_data in enumerate(valid_questions):
            options_dict = q_data['options']
            options_list = [
                options_dict.get('A', ''),
                options_dict.get('B', ''),
                options_dict.get('C', ''),
                options_dict.get('D', '')
            ]

            answer_letter = q_data['answer'].upper()
            correct_index = ord(answer_letter) - ord('A')

            Question.objects.create(
                assessment=test2,
                question_text=q_data['question'],
                options=options_list,
                correct_answer_index=correct_index,
                explanation=q_data.get('explanation', ''),
                difficulty=test2.difficulty_level,
                concept=q_data.get('concept', 'General'),
                order=idx
            )

        print(f"[Followup] Created Test 2 (ID: {test2.id}) with {len(valid_questions)} questions")
        return test2

    except json.JSONDecodeError as e:
        print(f"[Followup] JSON parsing error: {e}")
        raise ValueError(f"Failed to parse Test 2 questions: {e}")
    except Exception as e:
        print(f"[Followup] Error generating Test 2: {e}")
        raise
