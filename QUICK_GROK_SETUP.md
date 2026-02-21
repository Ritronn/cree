# Quick Grok AI Setup ⚡

## 1. Add Your API Key

Edit `learning/.env`:
```bash
XAI_API_KEY=xai-your-actual-key-here
```

Get your key: https://console.x.ai

## 2. Restart Backend

```bash
cd learning
python manage.py runserver
```

## 3. Test Integration

```bash
cd learning
python test_grok_integration.py
```

## 4. What Works Now

✅ **Question Generation** - AI-powered MCQ, short answer, problem-solving
✅ **Answer Assessment** - Intelligent grading with feedback
✅ **RAG Chat** - Context-aware tutoring during study sessions
✅ **ML Model** - Logic preserved for future use
✅ **Fallback System** - Works even without API key

## 5. Quick Test

```bash
cd learning
python manage.py shell
```

```python
from adaptive_learning.question_generator import QuestionGenerator
qg = QuestionGenerator()
questions = qg.generate_mcq_questions("Test content", ["Test"], 1, 1)
print(questions)
```

## Done! 🎉

Your system now uses Grok AI for all AI features while keeping ML model logic intact for future use.
