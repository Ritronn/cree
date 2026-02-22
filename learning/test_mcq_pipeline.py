"""
Tests for the Adaptive MCQ Generation Pipeline
================================================
Tests cover:
  - USER_STATE_CONFIG validation
  - extract_technical_content() with mocked Gemini API
  - generate_mcqs() for all 4 user states
  - generate_mcqs() error handling & edge cases
  - run_pipeline() end-to-end with mocked API
  - JSON parsing robustness (markdown fences, malformed output)
"""

import pytest
import json
import re
from unittest.mock import patch, MagicMock

# ── Import the module under test ────────────────────────────────────────────
# We patch genai.configure and GenerativeModel at import time so no real API
# call is made when the module loads.
with patch("google.generativeai.configure"), \
     patch("google.generativeai.GenerativeModel"):
    import mcq_pipeline as mp  # adjust if the file has a different name


# ─── Fixtures ───────────────────────────────────────────────────────────────

SAMPLE_TRANSCRIPT = """
Hey guys welcome back to the channel! Don't forget to smash that like button
and subscribe if you haven't already. Today we're going to talk about machine learning.

So machine learning is basically a subset of artificial intelligence where systems
learn from data. There are three main types: supervised learning, unsupervised learning,
and reinforcement learning.

In supervised learning, the model is trained on labeled data. For example, if you want
to classify emails as spam or not spam, you'd train on thousands of emails that are
already labeled. Common algorithms include linear regression for continuous outputs
and logistic regression for classification.

Unsupervised learning deals with unlabeled data. The model tries to find hidden patterns.
K-means clustering is a popular example — it groups similar data points together.

Reinforcement learning is different. An agent learns by interacting with an environment
and receiving rewards or penalties. Think of how AlphaGo learned to play Go.

Anyway that's all for today guys! Hit subscribe, see you in the next one!
"""

SAMPLE_TECHNICAL_CONTENT = """
• Machine Learning is a subset of AI where systems learn from data.
• Three types: supervised, unsupervised, reinforcement learning.
• Supervised learning uses labeled data (e.g. spam classification).
• Common supervised algorithms: linear regression, logistic regression.
• Unsupervised learning finds hidden patterns in unlabeled data.
• K-means clustering groups similar data points.
• Reinforcement learning: agent learns via rewards/penalties.
"""


def _make_mcq_list(count: int) -> list:
    """Helper: build a list of well-formed MCQ dicts."""
    return [
        {
            "question": f"Question {i}?",
            "options": {
                "A": f"Option A{i}",
                "B": f"Option B{i}",
                "C": f"Option C{i}",
                "D": f"Option D{i}",
            },
            "answer": "A",
            "explanation": f"Explanation for question {i}.",
        }
        for i in range(1, count + 1)
    ]


def _mock_response(text: str) -> MagicMock:
    """Return a MagicMock that mimics a Gemini GenerateContentResponse."""
    resp = MagicMock()
    resp.text = text
    return resp


# ═════════════════════════════════════════════════════════════════════════════
# 1. USER_STATE_CONFIG validation
# ═════════════════════════════════════════════════════════════════════════════

class TestUserStateConfig:
    """Validate the static USER_STATE_CONFIG dictionary."""

    def test_all_four_states_exist(self):
        assert set(mp.USER_STATE_CONFIG.keys()) == {1, 2, 3, 4}

    @pytest.mark.parametrize("state_id", [1, 2, 3, 4])
    def test_required_keys_present(self, state_id):
        cfg = mp.USER_STATE_CONFIG[state_id]
        for key in ("label", "num_questions", "difficulty", "instruction", "take_break"):
            assert key in cfg, f"Missing key '{key}' in state {state_id}"

    def test_confused_state_values(self):
        cfg = mp.USER_STATE_CONFIG[1]
        assert cfg["label"] == "confused"
        assert cfg["num_questions"] == 20
        assert cfg["difficulty"] == "beginner"
        assert cfg["take_break"] is False

    def test_bored_state_values(self):
        cfg = mp.USER_STATE_CONFIG[2]
        assert cfg["label"] == "bored"
        assert cfg["num_questions"] == 20
        assert cfg["difficulty"] == "advanced"
        assert cfg["take_break"] is False

    def test_overloaded_state_values(self):
        cfg = mp.USER_STATE_CONFIG[3]
        assert cfg["label"] == "overloaded"
        assert cfg["num_questions"] == 10
        assert cfg["difficulty"] == "easy"
        assert cfg["take_break"] is True

    def test_focused_state_values(self):
        cfg = mp.USER_STATE_CONFIG[4]
        assert cfg["label"] == "focused"
        assert cfg["num_questions"] == 20
        assert cfg["difficulty"] == "intermediate-to-advanced"
        assert cfg["take_break"] is False


# ═════════════════════════════════════════════════════════════════════════════
# 2. extract_technical_content
# ═════════════════════════════════════════════════════════════════════════════

class TestExtractTechnicalContent:
    """Tests for the transcript → clean content extraction."""

    @patch.object(mp.model, "generate_content")
    def test_returns_stripped_text(self, mock_gen):
        mock_gen.return_value = _mock_response("  Bullet points here  \n")
        result = mp.extract_technical_content("some transcript")
        assert result == "Bullet points here"

    @patch.object(mp.model, "generate_content")
    def test_passes_transcript_in_prompt(self, mock_gen):
        mock_gen.return_value = _mock_response("ok")
        mp.extract_technical_content("MY_UNIQUE_TRANSCRIPT_TOKEN")
        prompt_sent = mock_gen.call_args[0][0]
        assert "MY_UNIQUE_TRANSCRIPT_TOKEN" in prompt_sent

    @patch.object(mp.model, "generate_content")
    def test_prompt_asks_for_bullet_points(self, mock_gen):
        mock_gen.return_value = _mock_response("ok")
        mp.extract_technical_content("anything")
        prompt_sent = mock_gen.call_args[0][0]
        assert "bullet points" in prompt_sent.lower()

    @patch.object(mp.model, "generate_content")
    def test_handles_empty_transcript(self, mock_gen):
        mock_gen.return_value = _mock_response("")
        result = mp.extract_technical_content("")
        assert result == ""


# ═════════════════════════════════════════════════════════════════════════════
# 3. generate_mcqs  — happy paths
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateMCQsHappyPath:
    """Verify MCQ generation for each user state with valid API responses."""

    @pytest.mark.parametrize("state_id", [1, 2, 3, 4])
    @patch.object(mp.model, "generate_content")
    def test_returns_correct_structure(self, mock_gen, state_id):
        cfg = mp.USER_STATE_CONFIG[state_id]
        questions = _make_mcq_list(cfg["num_questions"])
        mock_gen.return_value = _mock_response(json.dumps(questions))

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, state_id)

        assert result["user_state"] == cfg["label"]
        assert result["difficulty"] == cfg["difficulty"]
        assert result["num_questions"] == cfg["num_questions"]
        assert result["take_break_suggestion"] == cfg["take_break"]
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == cfg["num_questions"]

    @patch.object(mp.model, "generate_content")
    def test_overloaded_has_break_message(self, mock_gen):
        questions = _make_mcq_list(10)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 3)
        assert result["take_break_suggestion"] is True
        assert result["break_message"] is not None
        assert "break" in result["break_message"].lower()

    @pytest.mark.parametrize("state_id", [1, 2, 4])
    @patch.object(mp.model, "generate_content")
    def test_no_break_message_for_other_states(self, mock_gen, state_id):
        cfg = mp.USER_STATE_CONFIG[state_id]
        questions = _make_mcq_list(cfg["num_questions"])
        mock_gen.return_value = _mock_response(json.dumps(questions))

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, state_id)
        assert result["take_break_suggestion"] is False
        assert result["break_message"] is None

    @patch.object(mp.model, "generate_content")
    def test_question_dict_keys(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)
        q = result["questions"][0]
        assert "question" in q
        assert "options" in q
        assert "answer" in q
        assert "explanation" in q
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}


# ═════════════════════════════════════════════════════════════════════════════
# 4. generate_mcqs — JSON parsing edge cases
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateMCQsJsonParsing:
    """Ensure generate_mcqs handles various raw output formats."""

    @patch.object(mp.model, "generate_content")
    def test_strips_markdown_code_fences(self, mock_gen):
        questions = _make_mcq_list(20)
        raw = "```json\n" + json.dumps(questions) + "\n```"
        mock_gen.return_value = _mock_response(raw)

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)
        assert len(result["questions"]) == 20

    @patch.object(mp.model, "generate_content")
    def test_strips_code_fences_with_extra_whitespace(self, mock_gen):
        questions = _make_mcq_list(20)
        raw = "```json  \n" + json.dumps(questions) + "\n  ```"
        mock_gen.return_value = _mock_response(raw)

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)
        assert len(result["questions"]) == 20

    @patch.object(mp.model, "generate_content")
    def test_plain_json_no_fences(self, mock_gen):
        questions = _make_mcq_list(10)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        result = mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 3)
        assert len(result["questions"]) == 10

    @patch.object(mp.model, "generate_content")
    def test_raises_on_invalid_json(self, mock_gen):
        mock_gen.return_value = _mock_response("this is not json at all")

        with pytest.raises(json.JSONDecodeError):
            mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)


# ═════════════════════════════════════════════════════════════════════════════
# 5. generate_mcqs — error handling
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateMCQsErrorHandling:
    """Validate error scenarios."""

    def test_invalid_state_raises_value_error(self):
        with pytest.raises(ValueError, match="user_state must be 1-4"):
            mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 0)

    def test_state_5_raises_value_error(self):
        with pytest.raises(ValueError, match="user_state must be 1-4"):
            mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 5)

    def test_negative_state_raises_value_error(self):
        with pytest.raises(ValueError, match="user_state must be 1-4"):
            mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, -1)

    @patch.object(mp.model, "generate_content")
    def test_api_exception_propagates(self, mock_gen):
        mock_gen.side_effect = RuntimeError("API quota exceeded")

        with pytest.raises(RuntimeError, match="API quota exceeded"):
            mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)


# ═════════════════════════════════════════════════════════════════════════════
# 6. run_pipeline — end-to-end (both API calls mocked)
# ═════════════════════════════════════════════════════════════════════════════

class TestRunPipeline:
    """Integration-style tests for the full pipeline with mocked API."""

    @patch.object(mp.model, "generate_content")
    def test_full_pipeline_confused_user(self, mock_gen):
        questions = _make_mcq_list(20)
        # First call → extract_technical_content, Second call → generate_mcqs
        mock_gen.side_effect = [
            _mock_response(SAMPLE_TECHNICAL_CONTENT),
            _mock_response(json.dumps(questions)),
        ]

        result = mp.run_pipeline(SAMPLE_TRANSCRIPT, 1)

        assert result["user_state"] == "confused"
        assert result["num_questions"] == 20
        assert result["difficulty"] == "beginner"
        assert "extracted_content" in result
        assert len(result["extracted_content"]) > 0
        assert mock_gen.call_count == 2

    @patch.object(mp.model, "generate_content")
    def test_full_pipeline_overloaded_user(self, mock_gen):
        questions = _make_mcq_list(10)
        mock_gen.side_effect = [
            _mock_response(SAMPLE_TECHNICAL_CONTENT),
            _mock_response(json.dumps(questions)),
        ]

        result = mp.run_pipeline(SAMPLE_TRANSCRIPT, 3)

        assert result["user_state"] == "overloaded"
        assert result["num_questions"] == 10
        assert result["take_break_suggestion"] is True
        assert result["break_message"] is not None

    @patch.object(mp.model, "generate_content")
    def test_full_pipeline_bored_user(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.side_effect = [
            _mock_response(SAMPLE_TECHNICAL_CONTENT),
            _mock_response(json.dumps(questions)),
        ]

        result = mp.run_pipeline(SAMPLE_TRANSCRIPT, 2)

        assert result["user_state"] == "bored"
        assert result["difficulty"] == "advanced"

    @patch.object(mp.model, "generate_content")
    def test_full_pipeline_focused_user(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.side_effect = [
            _mock_response(SAMPLE_TECHNICAL_CONTENT),
            _mock_response(json.dumps(questions)),
        ]

        result = mp.run_pipeline(SAMPLE_TRANSCRIPT, 4)

        assert result["user_state"] == "focused"
        assert result["difficulty"] == "intermediate-to-advanced"
        assert result["num_questions"] == 20

    @patch.object(mp.model, "generate_content")
    def test_pipeline_attaches_extracted_content(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.side_effect = [
            _mock_response("Clean content here"),
            _mock_response(json.dumps(questions)),
        ]

        result = mp.run_pipeline(SAMPLE_TRANSCRIPT, 4)
        assert result["extracted_content"] == "Clean content here"

    @patch.object(mp.model, "generate_content")
    def test_pipeline_extraction_failure_propagates(self, mock_gen):
        mock_gen.side_effect = RuntimeError("Network error")

        with pytest.raises(RuntimeError, match="Network error"):
            mp.run_pipeline(SAMPLE_TRANSCRIPT, 1)


# ═════════════════════════════════════════════════════════════════════════════
# 7. Prompt quality checks
# ═════════════════════════════════════════════════════════════════════════════

class TestPromptQuality:
    """Ensures prompts sent to the LLM contain the right instructions."""

    @patch.object(mp.model, "generate_content")
    def test_mcq_prompt_includes_difficulty(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)
        prompt = mock_gen.call_args[0][0]
        assert "beginner" in prompt.lower()

    @patch.object(mp.model, "generate_content")
    def test_mcq_prompt_includes_question_count(self, mock_gen):
        questions = _make_mcq_list(10)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 3)
        prompt = mock_gen.call_args[0][0]
        assert "10" in prompt

    @patch.object(mp.model, "generate_content")
    def test_mcq_prompt_includes_content(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        mp.generate_mcqs("UNIQUE_CONTENT_MARKER", 2)
        prompt = mock_gen.call_args[0][0]
        assert "UNIQUE_CONTENT_MARKER" in prompt

    @patch.object(mp.model, "generate_content")
    def test_mcq_prompt_requests_json_format(self, mock_gen):
        questions = _make_mcq_list(20)
        mock_gen.return_value = _mock_response(json.dumps(questions))

        mp.generate_mcqs(SAMPLE_TECHNICAL_CONTENT, 1)
        prompt = mock_gen.call_args[0][0]
        assert "json" in prompt.lower()

    @patch.object(mp.model, "generate_content")
    def test_extraction_prompt_mentions_non_educational_removal(self, mock_gen):
        mock_gen.return_value = _mock_response("ok")
        mp.extract_technical_content(SAMPLE_TRANSCRIPT)
        prompt = mock_gen.call_args[0][0]
        assert "non-educational" in prompt.lower() or "remove" in prompt.lower()
