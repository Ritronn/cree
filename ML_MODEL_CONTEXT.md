# ML Model Training Context - Adaptive Learning System

## Project Overview
We're building an adaptive learning platform for a hackathon that adjusts difficulty based on student performance. Need a simple ML model to predict the next optimal difficulty level.

---

## Model Requirements

**Type:** Single classification model (Random Forest or XGBoost recommended)

**Purpose:** Predict next difficulty level based on student's assessment performance

**Timeline:** Hackathon project - keep it simple and fast!

---

## Input Features (8 parameters)

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `accuracy` | float | 0-100 | Percentage of correct answers in current session |
| `avg_time_per_question` | float | 10-120 | Average time spent per question (seconds) |
| `first_attempt_correct` | float | 0-100 | Percentage correct on first attempt (no retries) |
| `current_difficulty` | int | 1-3 | Current difficulty level (1=Easy, 2=Medium, 3=Hard) |
| `sessions_completed` | int | 1-50 | Number of sessions completed in this topic |
| `score_trend` | float | -50 to +50 | Score change from previous session (current - previous) |
| `mastery_level` | float | 0-1 | Overall topic mastery (0=beginner, 1=expert) |
| `is_new_topic` | int | 0 or 1 | Is this the student's first session? (1=yes, 0=no) |

---

## Output (Target Variable)

| Output | Type | Range | Description |
|--------|------|-------|-------------|
| `next_difficulty` | int | 1-3 | Recommended difficulty for next session (1=Easy, 2=Medium, 3=Hard) |

**Optional secondary output:**
| Output | Type | Range | Description |
|--------|------|-------|-------------|
| `question_count` | int | 5-15 | Number of questions for next session |

---

## Training Data Format

### CSV Structure
```csv
accuracy,avg_time_per_question,first_attempt_correct,current_difficulty,sessions_completed,score_trend,mastery_level,is_new_topic,next_difficulty,question_count
```

### Sample Data Rows
```csv
accuracy,avg_time_per_question,first_attempt_correct,current_difficulty,sessions_completed,score_trend,mastery_level,is_new_topic,next_difficulty,question_count
45.0,60.0,30.0,2,1,-10.0,0.3,0,1,8
75.0,35.0,65.0,1,3,15.0,0.7,0,2,10
90.0,25.0,85.0,2,5,10.0,0.85,0,3,12
50.0,50.0,40.0,1,1,0.0,0.4,1,1,8
82.0,30.0,75.0,2,4,8.0,0.75,0,2,11
35.0,70.0,25.0,3,2,-25.0,0.35,0,2,9
```

---

## Synthetic Data Generation Guidelines

Generate **5,000-10,000 training samples** with these student personas:

### 1. Fast Learner (30% of data)
- `accuracy`: 80-95%
- `first_attempt_correct`: 70-90%
- `avg_time_per_question`: 20-35 seconds
- `score_trend`: +10 to +20
- `mastery_level`: Increases quickly (0.6-0.9)
- **Output:** Increase difficulty (current + 1, max 3)

### 2. Average Learner (40% of data)
- `accuracy`: 60-75%
- `first_attempt_correct`: 50-65%
- `avg_time_per_question`: 35-50 seconds
- `score_trend`: 0 to +10
- `mastery_level`: Steady growth (0.4-0.7)
- **Output:** Keep same difficulty

### 3. Struggling Learner (30% of data)
- `accuracy`: 30-55%
- `first_attempt_correct`: 20-45%
- `avg_time_per_question`: 50-80 seconds
- `score_trend`: -20 to 0
- `mastery_level`: Slow growth (0.2-0.5)
- **Output:** Decrease difficulty (current - 1, min 1)

### Special Cases to Include:
- **New topic starts:** `is_new_topic=1`, `sessions_completed=1`, `current_difficulty=1`, `mastery_level=0.0-0.3`
- **Plateau scenarios:** Same accuracy for multiple sessions, no score trend
- **Sudden drops:** High accuracy then sudden low accuracy (content too hard)

---

## Business Rules (Hard Constraints)

These rules MUST be enforced in the model or post-processing:

1. **New topics always start at difficulty 1**
   - If `is_new_topic=1` → `next_difficulty=1`

2. **Difficulty boundaries**
   - Minimum: 1 (Easy)
   - Maximum: 3 (Hard)

3. **No skipping levels**
   - Can only change by ±1 level at a time
   - Example: 1→2 ✓, 2→3 ✓, 1→3 ✗

4. **Performance thresholds**
   - If `accuracy < 50%` → Must decrease difficulty
   - If `accuracy > 85%` AND `sessions_completed > 2` → Must increase difficulty

5. **Question count logic** (if implementing)
   - Easy (1): 8-10 questions
   - Medium (2): 10-12 questions
   - Hard (3): 12-15 questions

---

## Model Training Recommendations

### Recommended Algorithms
1. **Random Forest Classifier** (easiest, good baseline)
2. **XGBoost Classifier** (better performance)
3. **Logistic Regression** (simplest fallback)

### Training Steps
1. Generate synthetic data (5k-10k rows)
2. Split: 80% train, 20% test
3. Train model on 8 input features → predict `next_difficulty`
4. Validate with test set
5. Apply business rules as post-processing
6. Export model as `.pkl` or `.joblib` file

### Evaluation Metrics
- **Accuracy**: Should be > 80%
- **Confusion Matrix**: Check if model confuses difficulty levels
- **F1-Score**: Per class (Easy, Medium, Hard)

### Expected Performance
- Training time: < 5 minutes
- Inference time: < 100ms per prediction
- Model size: < 10MB

---

## Deliverables

1. **Trained model file** (`adaptive_model.pkl` or `.joblib`)
2. **Synthetic training data** (`training_data.csv`)
3. **Model performance report** (accuracy, confusion matrix)

---

