# Design Document: Adaptive Learning System

## Overview

The Adaptive Learning System is a personalized digital learning platform that processes multiple content types (YouTube videos, PDFs, PowerPoint presentations), generates relevant assessments, tracks detailed performance metrics, and adapts content difficulty based on individual learning patterns. The system employs content extraction techniques, natural language processing for question generation, and adaptive algorithms to create personalized learning paths.

### Key Design Decisions

1. **Content Processing Architecture**: Modular pipeline design with separate processors for each content type (YouTube, PDF, PPT)
2. **Question Generation**: LLM-based approach using RAG for context-aware question generation
3. **Adaptive Algorithm**: Hybrid approach combining rule-based heuristics with statistical learning velocity tracking
4. **Data Storage**: Relational database for structured data with vector store for RAG embeddings
5. **YouTube API**: Use YouTube Data API v3 for caption/transcript extraction

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Content Window│  │Assessment UI │  │Progress View │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Content Mgmt  │  │Assessment    │  │Adaptive      │      │
│  │Service       │  │Service       │  │Engine        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Revision      │  │Metrics       │  │User          │      │
│  │Service       │  │Tracker       │  │Service       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Processing Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │YouTube       │  │PDF           │  │PowerPoint    │      │
│  │Processor     │  │Processor     │  │Processor     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │Question      │  │RAG           │                        │
│  │Generator     │  │Engine        │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Relational DB │  │Vector Store  │  │File Storage  │      │
│  │(PostgreSQL)  │  │(Pinecone/    │  │(S3/Local)    │      │
│  │              │  │ Chroma)      │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │YouTube API   │  │LLM API       │                        │
│  │              │  │(OpenAI/etc)  │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Content Ingestion**: User adds content → Content processor extracts text/metadata → Store in database and vector store
2. **Question Generation**: Content embeddings → RAG retrieval → LLM generates questions → Store questions with associations
3. **Assessment**: User takes assessment → Record responses with timestamps → Calculate metrics → Update performance data
4. **Adaptation**: Aggregate metrics → Calculate adaptive score → Determine next content difficulty → Update user learning path
5. **Revision**: Schedule revision → Query incorrect answers → Generate spaced repetition assessment → Present to user

## Components and Interfaces

### 1. Content Processors

#### YouTube Processor

**Responsibilities:**
- Extract video metadata (title, duration, thumbnail)
- Retrieve captions/transcripts via YouTube Data API v3
- Parse and clean transcript text
- Extract key timestamps for concept segmentation

**Interface:**
```typescript
interface YouTubeProcessor {
  extractMetadata(videoUrl: string): Promise<VideoMetadata>
  extractTranscript(videoId: string): Promise<Transcript>
  extractConcepts(transcript: Transcript): Promise<Concept[]>
}

interface VideoMetadata {
  videoId: string
  title: string
  duration: number
  thumbnailUrl: string
  channelName: string
}

interface Transcript {
  text: string
  segments: TranscriptSegment[]
}

interface TranscriptSegment {
  text: string
  startTime: number
  endTime: number
}
```

**Implementation Notes:**
- Use YouTube Data API v3 `captions.download` endpoint
- Fallback to `videoTranscript` library if API captions unavailable
- Clean transcript: remove filler words, normalize punctuation
- Segment by topic using sentence embeddings and clustering

#### PDF Processor

**Responsibilities:**
- Extract text from PDF documents
- Preserve document structure (headings, paragraphs, lists)
- Handle multi-column layouts and tables
- Extract images and perform OCR if needed

**Interface:**
```typescript
interface PDFProcessor {
  extractText(pdfFile: File): Promise<DocumentContent>
  extractStructure(pdfFile: File): Promise<DocumentStructure>
  extractConcepts(content: DocumentContent): Promise<Concept[]>
}

interface DocumentContent {
  fullText: string
  pages: PageContent[]
}

interface PageContent {
  pageNumber: number
  text: string
  images: ImageData[]
}

interface DocumentStructure {
  headings: Heading[]
  sections: Section[]
}
```

**Implementation Notes:**
- Use `pdf-parse` or `pdfjs-dist` for text extraction
- Use `tesseract.js` for OCR on images if needed
- Preserve heading hierarchy for concept organization
- Chunk text into semantic units for RAG

#### PowerPoint Processor

**Responsibilities:**
- Extract text from slides
- Extract images and perform OCR
- Preserve slide order and structure
- Extract speaker notes if available

**Interface:**
```typescript
interface PowerPointProcessor {
  extractContent(pptFile: File): Promise<PresentationContent>
  extractConcepts(content: PresentationContent): Promise<Concept[]>
}

interface PresentationContent {
  title: string
  slides: SlideContent[]
}

interface SlideContent {
  slideNumber: number
  title: string
  text: string
  images: ImageData[]
  speakerNotes: string
}
```

**Implementation Notes:**
- Use `officegen` or `pptxgenjs` for parsing
- Extract text from shapes and text boxes
- Use OCR for text in images
- Combine slide content with speaker notes for comprehensive context

### 2. RAG Engine

**Responsibilities:**
- Generate embeddings for content chunks
- Store embeddings in vector database
- Retrieve relevant context for question generation
- Maintain content-to-embedding mappings

**Interface:**
```typescript
interface RAGEngine {
  embedContent(content: string, metadata: ContentMetadata): Promise<void>
  retrieveContext(query: string, topK: number): Promise<ContextChunk[]>
  deleteContent(contentId: string): Promise<void>
}

interface ContentMetadata {
  contentId: string
  contentType: 'youtube' | 'pdf' | 'ppt'
  sourceReference: string
  timestamp?: number
}

interface ContextChunk {
  text: string
  metadata: ContentMetadata
  similarityScore: number
}
```

**Implementation Notes:**
- Use OpenAI `text-embedding-3-small` or similar for embeddings
- Vector store options: Pinecone (cloud), Chroma (local), or pgvector (PostgreSQL extension)
- Chunk size: 500-1000 tokens with 100-token overlap
- Store metadata for traceability back to source content

### 3. Question Generator

**Responsibilities:**
- Generate diverse question types from content
- Assign difficulty levels to questions
- Create distractors for multiple-choice questions
- Ensure questions test key concepts

**Interface:**
```typescript
interface QuestionGenerator {
  generateQuestions(
    content: string,
    concepts: Concept[],
    count: number,
    difficulty: DifficultyLevel
  ): Promise<Question[]>
  
  assignDifficulty(question: Question, concept: Concept): DifficultyLevel
}

interface Question {
  id: string
  text: string
  type: QuestionType
  options?: string[]
  correctAnswer: string
  explanation: string
  conceptId: string
  difficulty: DifficultyLevel
  sourceContentId: string
}

enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  TRUE_FALSE = 'true_false',
  SHORT_ANSWER = 'short_answer',
  FILL_BLANK = 'fill_blank'
}

enum DifficultyLevel {
  BEGINNER = 1,
  INTERMEDIATE = 2,
  ADVANCED = 3,
  EXPERT = 4
}

interface Concept {
  id: string
  name: string
  description: string
  parentConceptId?: string
  bloomLevel: BloomLevel
}

enum BloomLevel {
  REMEMBER = 1,
  UNDERSTAND = 2,
  APPLY = 3,
  ANALYZE = 4,
  EVALUATE = 5,
  CREATE = 6
}
```

**Implementation Notes:**
- Use LLM (GPT-4, Claude) with structured prompts
- Prompt engineering: specify question type, difficulty, Bloom's taxonomy level
- Generate 3-5 questions per major concept
- Validate generated questions for clarity and correctness
- Difficulty assignment based on Bloom's taxonomy and concept complexity

### 4. Assessment Service

**Responsibilities:**
- Present questions to users
- Record user responses with timestamps
- Provide immediate feedback
- Calculate assessment scores

**Interface:**
```typescript
interface AssessmentService {
  createAssessment(contentId: string, userId: string): Promise<Assessment>
  submitAnswer(assessmentId: string, questionId: string, answer: Answer): Promise<AnswerResult>
  completeAssessment(assessmentId: string): Promise<AssessmentResult>
  getAssessment(assessmentId: string): Promise<Assessment>
}

interface Assessment {
  id: string
  userId: string
  contentId: string
  questions: Question[]
  startTime: Date
  status: 'in_progress' | 'completed'
}

interface Answer {
  questionId: string
  userAnswer: string
  attemptNumber: number
  timeSpent: number
}

interface AnswerResult {
  correct: boolean
  correctAnswer: string
  explanation: string
  pointsEarned: number
}

interface AssessmentResult {
  assessmentId: string
  totalQuestions: number
  correctAnswers: number
  totalTime: number
  adaptiveScore: number
  conceptMastery: Map<string, number>
}
```

### 5. Metrics Tracker

**Responsibilities:**
- Record all performance metrics
- Calculate derived metrics (mastery, velocity)
- Aggregate metrics by concept and time period
- Provide analytics queries

**Interface:**
```typescript
interface MetricsTracker {
  recordAnswer(userId: string, answer: AnswerMetrics): Promise<void>
  calculateMasteryLevel(userId: string, conceptId: string): Promise<number>
  calculateLearningVelocity(userId: string, timeWindow: number): Promise<number>
  getPerformanceHistory(userId: string, conceptId?: string): Promise<PerformanceMetrics[]>
}

interface AnswerMetrics {
  userId: string
  questionId: string
  conceptId: string
  correct: boolean
  timeSpent: number
  attemptNumber: number
  difficulty: DifficultyLevel
  timestamp: Date
}

interface PerformanceMetrics {
  userId: string
  conceptId: string
  totalAttempts: number
  correctAttempts: number
  averageTime: number
  firstAttemptSuccessRate: number
  masteryLevel: number
  lastAssessed: Date
}
```

### 6. Adaptive Engine

**Responsibilities:**
- Calculate adaptive scores
- Determine next content difficulty
- Adjust learning paths
- Recommend content based on performance

**Interface:**
```typescript
interface AdaptiveEngine {
  calculateAdaptiveScore(assessmentResult: AssessmentResult, history: PerformanceMetrics[]): number
  determineNextDifficulty(userId: string, conceptId: string): Promise<DifficultyLevel>
  recommendContent(userId: string): Promise<ContentRecommendation[]>
  adjustPacing(userId: string, learningVelocity: number): Promise<PacingAdjustment>
}

interface ContentRecommendation {
  contentId: string
  conceptId: string
  difficulty: DifficultyLevel
  reason: string
  priority: number
}

interface PacingAdjustment {
  recommendedQuestionsPerSession: number
  recommendedSessionDuration: number
  difficultyProgression: DifficultyLevel[]
}
```

**Adaptive Score Calculation:**
```
AdaptiveScore = (
  0.30 * AccuracyScore +
  0.25 * FirstAttemptScore +
  0.20 * TimeEfficiencyScore +
  0.15 * DifficultyWeightedScore +
  0.10 * ConsistencyScore
)

Where:
- AccuracyScore = (CorrectAnswers / TotalQuestions) * 100
- FirstAttemptScore = (FirstAttemptCorrect / TotalQuestions) * 100
- TimeEfficiencyScore = 100 * (1 - (ActualTime - OptimalTime) / MaxTime)
- DifficultyWeightedScore = Σ(Correct * DifficultyWeight) / Σ(DifficultyWeight)
- ConsistencyScore = 100 * (1 - StandardDeviation(QuestionScores))
```

**Difficulty Adjustment Rules:**
- If AdaptiveScore >= 85 and MasteryLevel >= 0.8: Increase difficulty
- If AdaptiveScore <= 60 and MasteryLevel <= 0.5: Decrease difficulty
- If LearningVelocity > 1.5: Accelerate content progression
- If LearningVelocity < 0.5: Slow down and reinforce fundamentals

### 7. Revision Service

**Responsibilities:**
- Schedule revision sessions
- Select questions for spaced repetition
- Track revision performance
- Update mastery levels based on revision

**Interface:**
```typescript
interface RevisionService {
  scheduleRevision(userId: string): Promise<RevisionSchedule>
  generateRevisionAssessment(userId: string): Promise<Assessment>
  updateRevisionSchedule(userId: string, assessmentResult: AssessmentResult): Promise<void>
}

interface RevisionSchedule {
  userId: string
  nextRevisionDate: Date
  concepts: ConceptRevision[]
}

interface ConceptRevision {
  conceptId: string
  incorrectQuestions: string[]
  lastReviewed: Date
  nextReviewDate: Date
  repetitionInterval: number
}
```

**Spaced Repetition Algorithm:**
- Based on SuperMemo SM-2 algorithm
- Initial interval: 1 day
- If correct: interval *= 2.5
- If incorrect: interval = 1 day
- Maximum interval: 30 days
- Priority: Recent mistakes > Old mistakes > Low mastery concepts

## Data Models

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);
```

#### Content Items Table
```sql
CREATE TABLE content_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('youtube', 'pdf', 'ppt')),
  title VARCHAR(500) NOT NULL,
  source_url TEXT,
  file_path TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_content_user ON content_items(user_id);
CREATE INDEX idx_content_type ON content_items(content_type);
```

#### Concepts Table
```sql
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  parent_concept_id UUID REFERENCES concepts(id) ON DELETE SET NULL,
  bloom_level INTEGER CHECK (bloom_level BETWEEN 1 AND 6),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concept_content ON concepts(content_id);
CREATE INDEX idx_concept_parent ON concepts(parent_concept_id);
```

#### Questions Table
```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type VARCHAR(20) NOT NULL,
  options JSONB,
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 4),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_question_content ON questions(content_id);
CREATE INDEX idx_question_concept ON questions(concept_id);
CREATE INDEX idx_question_difficulty ON questions(difficulty);
```

#### Assessments Table
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  assessment_type VARCHAR(20) DEFAULT 'regular' CHECK (assessment_type IN ('regular', 'revision')),
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed')),
  adaptive_score DECIMAL(5,2)
);

CREATE INDEX idx_assessment_user ON assessments(user_id);
CREATE INDEX idx_assessment_content ON assessments(content_id);
CREATE INDEX idx_assessment_status ON assessments(status);
```

#### Answer Records Table
```sql
CREATE TABLE answer_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  user_answer TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL,
  attempt_number INTEGER DEFAULT 1,
  time_spent INTEGER NOT NULL, -- in seconds
  answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answer_assessment ON answer_records(assessment_id);
CREATE INDEX idx_answer_user ON answer_records(user_id);
CREATE INDEX idx_answer_question ON answer_records(question_id);
CREATE INDEX idx_answer_correct ON answer_records(is_correct);
```

#### Performance Metrics Table
```sql
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  total_attempts INTEGER DEFAULT 0,
  correct_attempts INTEGER DEFAULT 0,
  total_time INTEGER DEFAULT 0, -- in seconds
  first_attempt_correct INTEGER DEFAULT 0,
  first_attempt_total INTEGER DEFAULT 0,
  mastery_level DECIMAL(3,2) DEFAULT 0.00 CHECK (mastery_level BETWEEN 0 AND 1),
  learning_velocity DECIMAL(5,2) DEFAULT 1.00,
  last_assessed TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_perf_user_concept ON performance_metrics(user_id, concept_id);
CREATE INDEX idx_perf_mastery ON performance_metrics(mastery_level);
```

#### Revision Schedule Table
```sql
CREATE TABLE revision_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  last_reviewed TIMESTAMP,
  next_review_date TIMESTAMP NOT NULL,
  repetition_interval INTEGER DEFAULT 1, -- in days
  ease_factor DECIMAL(3,2) DEFAULT 2.50,
  consecutive_correct INTEGER DEFAULT 0
);

CREATE INDEX idx_revision_user ON revision_schedule(user_id);
CREATE INDEX idx_revision_next_date ON revision_schedule(next_review_date);
```

#### Content Embeddings Table (for RAG)
```sql
CREATE TABLE content_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content_items(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  embedding VECTOR(1536), -- Assuming OpenAI embeddings
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embedding_content ON content_embeddings(content_id);
-- For pgvector similarity search
CREATE INDEX idx_embedding_vector ON content_embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Key Relationships

- Users → Content Items (1:N)
- Content Items → Concepts (1:N)
- Content Items → Questions (1:N)
- Concepts → Questions (1:N)
- Users → Assessments (1:N)
- Assessments → Answer Records (1:N)
- Questions → Answer Records (1:N)
- Users + Concepts → Performance Metrics (N:M with aggregated data)
- Users + Questions → Revision Schedule (N:M)

