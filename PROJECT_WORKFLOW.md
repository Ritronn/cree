# Adaptive Learning System - User Workflow

## Overview
Students add learning content (YouTube videos, PDFs, PPTs), take assessments, and the system adapts difficulty based on their performance.

---

## Complete User Journey

### Step 1: Add Learning Content
**User Action:**
- Opens the app, sees "My Topics" dashboard
- Clicks "+ Add Content"
- Pastes YouTube link OR uploads PDF/PPT
- System auto-detects topic (e.g., "Python Programming")

**System Action:**
- Extracts content (YouTube transcript / PDF text / PPT slides)
- Identifies key concepts (e.g., "functions", "loops", "variables")
- Generates 10 assessment questions using Content Agent
- Stores everything in database

---

### Step 2: Take Assessment
**User Action:**
- Clicks on the topic to start learning
- Watches video / reads PDF in the content window
- Clicks "Take Assessment"
- Answers 10 questions one by one

**System Action:**
- Presents questions (starting with difficulty level 1 for new topics)
- Records each answer with timestamp
- Tracks: correct/incorrect, time taken, retry attempts
- Shows immediate feedback after each question

---

### Step 3: View Results & Adaptive Scoring
**User Action:**
- Completes assessment
- Sees results screen

**System Shows:**
- Score: 7/10 (70%)
- Time taken: 8 minutes
- Adaptive Score: 68/100
- Weak concepts: "Functions" (2/4 wrong), "Loops" (1/3 wrong)

**System Action (Behind the Scenes):**
- Learning Speed Agent analyzes performance
- Calculates: accuracy, first-attempt rate, time efficiency
- Updates mastery level for each concept
- Decides next difficulty level (stay at 1, move to 2, or drop back)

---

### Step 4: Continue Learning (Adaptive Difficulty Kicks In)
**User Action:**
- Adds another Python video next day
- Takes new assessment

**System Action:**
- Checks user's history: 70% accuracy, mastery 0.65
- Learning Speed Agent decides: "Keep difficulty 1, add more medium questions"
- Generates 10 new questions: 6 easy, 4 medium
- User scores 78% → improving!

---

### Step 5: Progress Over Time
**Session 3:**
- User scores 82%
- System increases difficulty: 4 easy, 6 medium questions

**Session 5:**
- User consistently scores 85%+
- System bumps to difficulty level 2: 3 medium, 7 hard questions

**Session 8:**
- User masters the topic (mastery 0.85)
- System suggests: "Ready for advanced Python topics!"

---

### Step 6: Weekend Revision
**System Action (Automatic):**
- Every weekend, system checks incorrect answers
- Generates revision assessment with only wrong questions
- Prioritizes: recent mistakes + low mastery concepts

**User Action:**
- Gets notification: "5 questions to review"
- Retakes those specific questions
- Gets 4/5 correct

**System Action:**
- Updates mastery levels
- Schedules next revision using spaced repetition
- Questions answered correctly: review in 3 days
- Questions still wrong: review tomorrow

---

### Step 7: Switch Topics (Multi-Topic Support)
**User Action:**
- Switches from Python to Math
- Adds a Calculus video

**System Action:**
- Recognizes new topic: "Math/Calculus"
- Starts fresh: difficulty level 1, mastery 0.0
- BUT uses general learning profile: "User is a fast learner overall"
- Adjusts faster than normal based on first assessment

---

## Example: Sarah's 2-Week Journey

### Day 1 - Python Basics
- Adds video: "Python Functions Tutorial"
- Takes assessment: 6/10 (60%)
- Adaptive Score: 65/100
- System: "Stay at difficulty 1"

### Day 3 - Python Loops
- Adds video: "Python Loops Explained"
- Takes assessment: 8/10 (80%)
- Adaptive Score: 75/100
- System: "Increase to difficulty 1.5 (mix of easy + medium)"

### Day 5 - Python Classes
- Adds PDF: "OOP in Python"
- Takes assessment: 9/10 (90%)
- Adaptive Score: 88/100
- System: "Move to difficulty 2"

### Weekend - Revision
- System shows 4 questions she got wrong
- Retakes: 3/4 correct
- Mastery updated: Functions 0.65 → 0.78

### Day 8 - Advanced Python
- Adds video: "Python Decorators"
- Takes assessment (difficulty 2): 7/10 (70%)
- System: "Good! You're being challenged. Stay at difficulty 2"

### Day 12 - Mastery Achieved
- Consistent 85%+ scores
- Mastery level: 0.87
- System: "You've mastered Python basics! Try advanced topics or switch to a new subject"

### Day 13 - New Topic
- Switches to "Data Structures"
- System starts fresh but adapts faster based on her learning pattern

---

## Key Features in Action

### 1. Adaptive Difficulty
- Starts easy for new topics
- Increases when user scores 85%+ consistently
- Decreases when user scores below 50%
- Never jumps more than 1 level at a time

### 2. Concept Tracking
- Identifies weak concepts from wrong answers
- Shows: "You're weak in Functions (40% accuracy)"
- Focuses revision on weak areas

### 3. Spaced Repetition
- Wrong answers come back quickly (1 day)
- Correct answers come back slower (3 days → 7 days → 14 days)
- Prevents forgetting

### 4. Multi-Topic Support
- Each topic has independent difficulty tracking
- Can switch between topics anytime
- System maintains separate progress for each

### 5. Learning Speed Detection
- Fast learners: Progress faster, get harder content sooner
- Slow learners: More repetition, slower progression
- Adapts in real-time based on performance

---

## System Intelligence Summary

**Content Agent:**
- Extracts content from videos/PDFs/PPTs
- Generates relevant questions
- Creates explanations for answers

**Learning Speed Agent:**
- Monitors performance metrics
- Calculates adaptive score
- Adjusts difficulty level
- Determines question count and pacing

**Concept Diagnoser:**
- Tracks performance per concept
- Identifies weak areas
- Prioritizes revision topics


