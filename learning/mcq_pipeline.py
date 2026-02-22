import google.generativeai as genai
import json
import re

# ── Config ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

# ── User States ──────────────────────────────────────────────────────────────
# 1 = confused      → simpler questions, 20 Qs
# 2 = bored         → harder/challenging questions, 20 Qs
# 3 = overloaded    → suggest break, only 10 Qs
# 4 = focused       → increased difficulty, 20 Qs

USER_STATE_CONFIG = {
    1: {
        "label": "confused",
        "num_questions": 20,
        "difficulty": "beginner",
        "instruction": (
            "The user is confused. Generate SIMPLE questions that reinforce basic understanding. "
            "Use straightforward language. Focus on definitions and core concepts only. "
            "Avoid tricky or complex scenarios."
        ),
        "take_break": False,
    },
    2: {
        "label": "bored",
        "num_questions": 20,
        "difficulty": "advanced",
        "instruction": (
            "The user is bored. Generate CHALLENGING questions that require deeper thinking. "
            "Include application-based, analytical, or scenario questions. "
            "Avoid trivial or obvious questions."
        ),
        "take_break": False,
    },
    3: {
        "label": "overloaded",
        "num_questions": 10,
        "difficulty": "easy",
        "instruction": (
            "The user is overloaded. Generate only 10 EASY questions focusing on the most "
            "important takeaways. Keep questions short and clear."
        ),
        "take_break": True,
    },
    4: {
        "label": "focused",
        "num_questions": 20,
        "difficulty": "intermediate-to-advanced",
        "instruction": (
            "The user is focused and performing well. Gradually INCREASE difficulty. "
            "Mix conceptual, application, and analysis questions to keep them engaged and growing."
        ),
        "take_break": False,
    },
}


# ── Step 1: Extract Technical Content from Transcript ────────────────────────
def extract_technical_content(transcript: str) -> str:
    """
    Cleans the raw transcript and extracts only the educational/technical content.
    Removes: filler, jokes, like/subscribe, timestamps, sponsor segments, etc.
    """
    prompt = f"""
You are an educational content extractor.

Given the raw YouTube transcript below, do the following:
1. REMOVE all non-educational content: jokes, "like and subscribe", timestamps, 
   sponsor mentions, personal anecdotes unrelated to the topic, filler phrases, 
   greetings/outros, and any repeated content.
2. EXTRACT and ORGANIZE the core technical/educational content:
   - Key concepts and definitions
   - Important facts, formulas, or rules explained
   - Step-by-step processes taught
   - Examples that illustrate a technical point
3. Output as structured bullet points grouped by topic/subtopic.
4. Be comprehensive — don't skip important technical details.
5. Do NOT add any information not present in the transcript.

RAW TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

OUTPUT (structured bullet points only, no preamble):
"""

    response = model.generate_content(prompt)
    return response.text.strip()


# ── Step 2: Generate Adaptive MCQs ───────────────────────────────────────────
def generate_mcqs(technical_content: str, user_state: int) -> dict:
    """
    Generates adaptive MCQs based on extracted content and user's current state.
    Returns a dict with questions list and optional break suggestion.
    """
    if user_state not in USER_STATE_CONFIG:
        raise ValueError(f"user_state must be 1-4, got {user_state}")

    config = USER_STATE_CONFIG[user_state]
    num_q = config["num_questions"]
    instruction = config["instruction"]
    difficulty = config["difficulty"]

    prompt = f"""
You are an expert quiz generator for educational content.

CONTEXT: {instruction}

DIFFICULTY LEVEL: {difficulty}
NUMBER OF QUESTIONS: {num_q}

RULES:
- Generate EXACTLY {num_q} MCQ questions.
- Each question must be DIRECTLY answerable from the provided content only.
- Do NOT use any outside knowledge or hallucinate facts.
- Each question must have exactly 4 options (A, B, C, D).
- Only one option should be correct.
- Include a brief explanation for the correct answer.
- Questions should vary — don't repeat the same concept twice.

CONTENT TO BASE QUESTIONS ON:
\"\"\"
{technical_content}
\"\"\"

Return ONLY a valid JSON array in this exact format, no markdown, no extra text:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "Option A",
      "B": "Option B", 
      "C": "Option C",
      "D": "Option D"
    }},
    "answer": "A",
    "explanation": "Brief explanation why A is correct."
  }}
]
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    questions = json.loads(raw)

    result = {
        "user_state": config["label"],
        "difficulty": difficulty,
        "num_questions": len(questions),
        "take_break_suggestion": config["take_break"],
        "break_message": (
            "⚠️  You seem overloaded. Consider taking a 10-minute break before attempting these questions. "
            "Rest helps retention!"
        ) if config["take_break"] else None,
        "questions": questions,
    }

    return result


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def run_pipeline(transcript: str, user_state: int) -> dict:
    """
    Full pipeline:
      transcript (raw) → extract technical content → generate adaptive MCQs
    
    Args:
        transcript: Raw YouTube transcript string
        user_state: Integer 1-4 representing user's current state
                    1=confused, 2=bored, 3=overloaded, 4=focused
    
    Returns:
        dict with questions and metadata
    """
    print(f"[1/2] Extracting technical content from transcript...")
    technical_content = extract_technical_content(transcript)
    print(f"      ✓ Extracted {len(technical_content.split())} words of clean content")

    print(f"[2/2] Generating MCQs for user state: {USER_STATE_CONFIG[user_state]['label']}...")
    result = generate_mcqs(technical_content, user_state)
    print(f"      ✓ Generated {result['num_questions']} questions ({result['difficulty']} difficulty)")

    # Attach extracted content for debugging / reuse
    result["extracted_content"] = technical_content

    return result


# ── Example Usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Example: paste or load your transcript here
    sample_transcript = """
    Hey guys welcome back to the channel! Don't forget to smash that like button 
    and subscribe if you haven't already. Today we're going to talk about machine learning.
    
    So machine learning is basically a subset of artificial intelligence where systems 
    learn from data. There are three main types: supervised learning, unsupervised learning, 
    and reinforcement learning.
    
    In supervised learning, the model is trained on labeled data. For example, if you want 
    to classify emails as spam or not spam, you'd train on thousands of emails that are 
    already labeled. The algorithm learns the pattern. Common algorithms include linear 
    regression for continuous outputs and logistic regression for classification.
    
    Unsupervised learning deals with unlabeled data. The model tries to find hidden patterns. 
    K-means clustering is a popular example — it groups similar data points together.
    
    Reinforcement learning is different. An agent learns by interacting with an environment 
    and receiving rewards or penalties. Think of how AlphaGo learned to play chess.
    
    Anyway that's all for today guys! Hit subscribe, see you in the next one!
    """

    # Simulate user state (1=confused, 2=bored, 3=overloaded, 4=focused)
    USER_STATE = 1

    result = run_pipeline(sample_transcript, USER_STATE)

    # Print break message if applicable
    if result["take_break_suggestion"]:
        print(f"\n{result['break_message']}\n")

    # Print questions
    print(f"\n=== {result['num_questions']} MCQs | State: {result['user_state']} | Difficulty: {result['difficulty']} ===\n")
    for i, q in enumerate(result["questions"], 1):
        print(f"Q{i}. {q['question']}")
        for key, val in q["options"].items():
            print(f"   {key}. {val}")
        print(f"   ✓ Answer: {q['answer']} — {q['explanation']}\n")

    # Optionally save to JSON
    with open("mcq_output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Saved to mcq_output.json")
