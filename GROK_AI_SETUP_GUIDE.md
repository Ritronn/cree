# Grok AI Integration Setup Guide 🤖

## Overview

Your Adaptive Learning Platform now uses **Grok AI** (by xAI) for:
1. **Question Generation** - Automatically generate MCQ, short answer, and problem-solving questions
2. **Answer Assessment** - Intelligently evaluate student responses
3. **RAG Chat** - Provide context-aware tutoring and Q&A during study sessions

## What Changed

### Before (Groq API)
- Used Groq API with Llama models
- Required separate RAG backend for chat
- Environment variable: `GROQ_API_KEY`

### After (Grok AI)
- Uses Grok AI API (xAI)
- Integrated chat directly with Grok AI
- Environment variable: `XAI_API_KEY`
- Single API for all AI features

## Setup Instructions

### Step 1: Get Your Grok AI API Key

1. Visit [https://x.ai/api](https://x.ai/api) or [https://console.x.ai](https://console.x.ai)
2. Sign up or log in to your xAI account
3. Navigate to API Keys section
4. Create a new API key
5. Copy your API key (starts with `xai-...`)

### Step 2: Configure Environment Variables

1. Open `learning/.env` file (create if it doesn't exist)
2. Add your Grok AI API key:

```bash
# Grok AI API Key (xAI)
XAI_API_KEY=xai-your-actual-api-key-here
```

3. Save the file

### Step 3: Verify Installation

The system will automatically use Grok AI when the API key is configured. If the API key is missing or invalid, it will fall back to template-based generation.

## Features Using Grok AI

### 1. Question Generation

**File:** `learning/adaptive_learning/question_generator.py`

**Capabilities:**
- Generate Multiple Choice Questions (MCQ)
- Generate Short Answer Questions
- Generate Problem-Solving Questions
- Adaptive difficulty levels (easy, medium, hard)
- Context-aware based on study content

**API Endpoint:** `https://api.x.ai/v1/chat/completions`
**Model:** `grok-beta`

**Example Usage:**
```python
from adaptive_learning.question_generator import QuestionGenerator

qg = QuestionGenerator()
questions = qg.generate_mcq_questions(
    content="Your study content here",
    concepts=["concept1", "concept2"],
    difficulty=2,  # 1=easy, 2=medium, 3=hard
    count=5
)
```

### 2. Answer Assessment

**Capabilities:**
- Evaluate open-ended answers
- Provide detailed feedback
- Score answers (0-100)
- Confidence scoring

**Example Usage:**
```python
result = qg.assess_answer(
    question="What is photosynthesis?",
    expected_answer="Process by which plants convert light to energy",
    user_answer="Plants use sunlight to make food",
    question_type="short_answer"
)
# Returns: {score: 85, is_correct: True, feedback: "...", confidence: 0.9}
```

### 3. RAG Chat Integration

**File:** `learning/adaptive_learning/rag_chat_integration.py`

**Capabilities:**
- Context-aware Q&A during study sessions
- Intelligent tutoring based on study content
- Real-time help and clarification
- Keeps students focused on study material

**API Endpoint:** Same as question generation
**Model:** `grok-beta`

**Example Usage:**
```python
from adaptive_learning.rag_chat_integration import RAGChatIntegration

response = RAGChatIntegration.send_query(
    session_id=123,
    query="Can you explain this concept in simpler terms?",
    context="Optional additional context"
)
# Returns: {success: True, response: "...", sources: [...], confidence: 0.9}
```

## API Configuration

### Request Format

```json
{
  "model": "grok-beta",
  "messages": [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User query"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### Response Format

```json
{
  "choices": [
    {
      "message": {
        "content": "AI response here"
      }
    }
  ]
}
```

## Fallback Mechanism

If Grok AI is unavailable or the API key is not configured, the system automatically falls back to:

1. **Template-based question generation** - Uses predefined templates
2. **Keyword-based assessment** - Simple keyword matching
3. **Error messages for chat** - Informs user that chat is unavailable

This ensures the platform continues to function even without AI capabilities.

## Error Handling

### Common Errors

1. **API Key Not Found**
   - Error: `XAI_API_KEY not found`
   - Solution: Add API key to `.env` file

2. **Connection Error**
   - Error: `Grok AI API not available`
   - Solution: Check internet connection

3. **Timeout**
   - Error: `Request timeout`
   - Solution: Try again, API might be slow

4. **Rate Limiting**
   - Error: `429 Too Many Requests`
   - Solution: Wait and retry, or upgrade API plan

### Retry Logic

The system automatically retries failed requests:
- Max retries: 3
- Exponential backoff: 1s, 2s, 3s
- Timeout: 30 seconds per request

## Cost Considerations

### Grok AI Pricing (as of 2026)

Check current pricing at [https://x.ai/pricing](https://x.ai/pricing)

**Typical Usage:**
- Question generation: ~500-1000 tokens per request
- Answer assessment: ~200-500 tokens per request
- Chat query: ~500-1500 tokens per request

**Optimization Tips:**
1. Limit content context to 5000 characters
2. Use appropriate temperature settings
3. Set reasonable max_tokens limits
4. Cache frequently used questions

## Testing

### Test Question Generation

```bash
cd learning
python manage.py shell
```

```python
from adaptive_learning.question_generator import QuestionGenerator

qg = QuestionGenerator()
questions = qg.generate_mcq_questions(
    content="Python is a programming language",
    concepts=["Python", "Programming"],
    difficulty=1,
    count=2
)
print(questions)
```

### Test Chat Integration

```bash
cd learning
python manage.py shell
```

```python
from adaptive_learning.rag_chat_integration import RAGChatIntegration
from adaptive_learning.models import StudySession

# Get a session ID from your database
session = StudySession.objects.first()
response = RAGChatIntegration.send_query(
    session_id=session.id,
    query="What is this content about?"
)
print(response)
```

## Monitoring

### Check API Usage

Monitor your API usage at the xAI console:
- Total requests
- Token usage
- Error rates
- Response times

### Logs

Check Django logs for AI-related messages:
```bash
# In your Django server output
"XAI_API_KEY not found, using template fallback"
"Grok AI API error for MCQ: ..."
"Grok AI assessment failed: ..."
```

## Security Best Practices

1. **Never commit API keys** - Use `.env` file (already in `.gitignore`)
2. **Rotate keys regularly** - Generate new keys periodically
3. **Monitor usage** - Watch for unusual activity
4. **Set rate limits** - Configure appropriate limits in xAI console
5. **Use environment variables** - Never hardcode keys

## Troubleshooting

### Issue: Questions are template-based, not AI-generated

**Check:**
1. Is `XAI_API_KEY` set in `.env`?
2. Is the API key valid?
3. Check Django logs for error messages

**Solution:**
```bash
# Verify API key is loaded
cd learning
python manage.py shell
```
```python
import os
print(os.environ.get('XAI_API_KEY'))  # Should print your key
```

### Issue: Chat returns error messages

**Check:**
1. Is the study session valid?
2. Does the session have content?
3. Is the API key configured?

**Solution:**
Check the response for specific error messages and follow the guidance provided.

### Issue: Slow response times

**Possible causes:**
1. Large content context
2. Network latency
3. API rate limiting

**Solutions:**
1. Reduce context size (already limited to 5000 chars)
2. Check internet connection
3. Wait and retry

## Migration from Groq

If you were using Groq API before:

1. **Update environment variable:**
   ```bash
   # Old
   GROQ_API_KEY=...
   
   # New
   XAI_API_KEY=...
   ```

2. **No code changes needed** - The system automatically uses the new API

3. **Remove old dependencies:**
   ```bash
   pip uninstall groq
   ```

4. **Test thoroughly** - Verify all features work with Grok AI

## Support

- **xAI Documentation:** [https://docs.x.ai](https://docs.x.ai)
- **API Status:** [https://status.x.ai](https://status.x.ai)
- **Community:** xAI Discord/Forum

## Summary

✅ Grok AI integrated for question generation
✅ Grok AI integrated for answer assessment  
✅ Grok AI integrated for RAG chat
✅ Automatic fallback to templates
✅ Comprehensive error handling
✅ Retry logic with exponential backoff
✅ Environment variable configuration

Your adaptive learning platform is now powered by Grok AI! 🚀
