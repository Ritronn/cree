# Database Schema - Adaptive Learning System

## Core Tables (Study Data Only)

---

## 1. topics
Stores learning topics/subjects

```sql
CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  mastery_level DECIMAL(3,2) DEFAULT 0.00,
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 3),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_topics_user ON topics(user_id);
```

**Fields:**
- `id`: Unique topic identifier
- `user_id`: Reference to user (you'll add this table later)
- `name`: Topic name (e.g., "Python Programming", "Calculus")
- `category`: Broader category (e.g., "Programming", "Math")
- `mastery_level`: Overall mastery (0.0 to 1.0)
- `difficulty_level`: Current difficulty (1=Easy, 2=Medium, 3=Hard)

---

## 2. content_items
Stores uploaded/added learning materials

```sql
CREATE TABLE content_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('youtube', 'pdf', 'ppt')),
  title VARCHAR(500) NOT NULL,
  source_url TEXT,
  file_path TEXT,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_topic ON content_items(topic_id);
```

**Fields:**
- `id`: Unique content identifier
- `topic_id`: Which topic this content belongs to
- `content_type`: youtube, pdf, or ppt
- `title`: Content title
- `source_url`: YouTube URL (if video)
- `file_path`: Local file path (if PDF/PPT)
- `processed`: Has content been extracted and questions generated?

---

## 3. concepts
Key concepts extracted from content

```sql
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concepts_topic ON concepts(topic_id);
CREATE INDEX idx_concepts_content ON concepts(content_id);
```

**Fields:**
- `id`: Unique concept identifier
- `topic_id`: Which topic this concept belongs to
- `content_id`: Which content this was extracted from
- `name`: Concept name (e.g., "Python Functions", "For Loops")
- `description`: Brief description of the concept

---

## 4. questions
Assessment questions generated from content

```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type VARCHAR(20) DEFAULT 'multiple_choice',
  options JSONB,
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 3),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_questions_content ON questions(content_id);
CREATE INDEX idx_questions_concept ON questions(concept_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
```

**Fields:**
- `id`: Unique question identifier
- `content_id`: Source content
- `concept_id`: Which concept this tests
- `question_text`: The actual question
- `question_type`: multiple_choice, true_false, short_answer
- `options`: JSON array of answer choices (for multiple choice)
- `correct_answer`: The correct answer
- `explanation`: Why this is the correct answer
- `difficulty`: 1=Easy, 2=Medium, 3=Hard

**Example `options` JSON:**
```json
["Option A", "Option B", "Option C", "Option D"]
```

---

## 5. assessments
Assessment sessions

```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  assessment_type VARCHAR(20) DEFAULT 'regular' CHECK (assessment_type IN ('regular', 'revision')),
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed')),
  adaptive_score DECIMAL(5,2)
);

CREATE INDEX idx_assessments_user ON assessments(user_id);
CREATE INDEX idx_assessments_topic ON assessments(topic_id);
```

**Fields:**
- `id`: Unique assessment identifier
- `user_id`: Who took the assessment
- `topic_id`: Which topic
- `content_id`: Which content (if regular assessment)
- `assessment_type`: regular or revision
- `start_time`: When started
- `end_time`: When completed
- `status`: in_progress or completed
- `adaptive_score`: Final calculated score (0-100)

---

## 6. answer_records
Individual question answers

```sql
CREATE TABLE answer_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  user_answer TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL,
  attempt_number INTEGER DEFAULT 1,
  time_spent INTEGER NOT NULL,
  answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answers_assessment ON answer_records(assessment_id);
CREATE INDEX idx_answers_user ON answer_records(user_id);
CREATE INDEX idx_answers_question ON answer_records(question_id);
CREATE INDEX idx_answers_correct ON answer_records(is_correct);
```

**Fields:**
- `id`: Unique answer identifier
- `assessment_id`: Which assessment session
- `question_id`: Which question
- `user_id`: Who answered
- `user_answer`: What they answered
- `is_correct`: True/False
- `attempt_number`: 1st attempt, 2nd attempt, etc.
- `time_spent`: Seconds spent on this question
- `answered_at`: Timestamp

---

## 7. performance_metrics
Aggregated performance per concept

```sql
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  total_attempts INTEGER DEFAULT 0,
  correct_attempts INTEGER DEFAULT 0,
  total_time INTEGER DEFAULT 0,
  first_attempt_correct INTEGER DEFAULT 0,
  first_attempt_total INTEGER DEFAULT 0,
  mastery_level DECIMAL(3,2) DEFAULT 0.00 CHECK (mastery_level BETWEEN 0 AND 1),
  last_assessed TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_perf_user_concept ON performance_metrics(user_id, concept_id);
CREATE INDEX idx_perf_topic ON performance_metrics(topic_id);
```

**Fields:**
- `id`: Unique metric identifier
- `user_id`: Who this is for
- `topic_id`: Which topic
- `concept_id`: Which concept
- `total_attempts`: Total questions attempted for this concept
- `correct_attempts`: How many correct
- `total_time`: Total seconds spent
- `first_attempt_correct`: Correct on first try
- `first_attempt_total`: Total first attempts
- `mastery_level`: Calculated mastery (0.0 to 1.0)
- `last_assessed`: Last time assessed
- `updated_at`: Last update timestamp

---

## 8. revision_schedule
Spaced repetition tracking

```sql
CREATE TABLE revision_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  last_reviewed TIMESTAMP,
  next_review_date TIMESTAMP NOT NULL,
  repetition_interval INTEGER DEFAULT 1,
  consecutive_correct INTEGER DEFAULT 0
);

CREATE INDEX idx_revision_user ON revision_schedule(user_id);
CREATE INDEX idx_revision_next_date ON revision_schedule(next_review_date);
```

**Fields:**
- `id`: Unique schedule identifier
- `user_id`: Who this is for
- `question_id`: Which question to review
- `concept_id`: Which concept
- `last_reviewed`: Last review timestamp
- `next_review_date`: When to review next
- `repetition_interval`: Days until next review
- `consecutive_correct`: How many times answered correctly in a row

---

## Relationships Summary

```
topics (1) ──→ (N) content_items
topics (1) ──→ (N) concepts
topics (1) ──→ (N) assessments
topics (1) ──→ (N) performance_metrics

content_items (1) ──→ (N) concepts
content_items (1) ──→ (N) questions
content_items (1) ──→ (N) assessments

concepts (1) ──→ (N) questions
concepts (1) ──→ (N) performance_metrics
concepts (1) ──→ (N) revision_schedule

questions (1) ──→ (N) answer_records
questions (1) ──→ (N) revision_schedule

assessments (1) ──→ (N) answer_records
```

---

## Key Queries You'll Need

### Get topic progress
```sql
SELECT t.name, t.mastery_level, t.difficulty_level, 
       COUNT(DISTINCT c.id) as total_concepts,
       COUNT(DISTINCT ci.id) as total_content
FROM topics t
LEFT JOIN concepts c ON c.topic_id = t.id
LEFT JOIN content_items ci ON ci.topic_id = t.id
WHERE t.user_id = ?
GROUP BY t.id;
```

### Get weak concepts for a topic
```sql
SELECT c.name, pm.mastery_level, pm.correct_attempts, pm.total_attempts
FROM performance_metrics pm
JOIN concepts c ON c.id = pm.concept_id
WHERE pm.topic_id = ? AND pm.user_id = ?
ORDER BY pm.mastery_level ASC
LIMIT 5;
```

### Get questions for revision
```sql
SELECT q.*, rs.next_review_date
FROM revision_schedule rs
JOIN questions q ON q.id = rs.question_id
WHERE rs.user_id = ? AND rs.next_review_date <= NOW()
ORDER BY rs.next_review_date ASC;
```

### Calculate adaptive score inputs
```sql
SELECT 
  COUNT(*) as total_questions,
  SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
  AVG(time_spent) as avg_time,
  SUM(CASE WHEN is_correct AND attempt_number = 1 THEN 1 ELSE 0 END) as first_attempt_correct
FROM answer_records
WHERE assessment_id = ?;
```

---

## Notes

- All tables use UUID for primary keys
- Foreign keys have ON DELETE CASCADE for cleanup
- Indexes on frequently queried columns
- JSONB for flexible data (question options)
- Timestamps for tracking and analytics
- Check constraints for data validation
