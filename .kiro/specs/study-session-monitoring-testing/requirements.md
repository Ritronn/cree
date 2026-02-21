# Requirements Document: Study Session Monitoring and Testing System

## Introduction

This document specifies the requirements for a comprehensive backend system that monitors study sessions and generates adaptive tests. The system integrates with an existing Django backend and React frontend to provide intelligent learning experiences through two study session modes, real-time monitoring, automatic test generation, and ML-powered adaptive difficulty adjustment.

## Glossary

- **System**: The Study Session Monitoring and Testing System
- **User**: A student using the learning platform
- **Study_Session**: A timed learning period where users consume educational content
- **Recommended_Session**: A 2-hour study session with a flexible 20-minute break
- **Standard_Session**: A 50-minute study session with a mandatory 10-minute break (Pomodoro-style)
- **Content**: Educational material loaded from YouTube, PDF, DOCX, or PPT sources
- **Test**: An automatically generated assessment created after a study session ends
- **MCQ**: Multiple Choice Question requiring recognition and basic understanding
- **Short_Answer**: Question requiring recall and comprehension
- **Problem_Solving**: Question requiring application of learned concepts
- **Monitoring_Data**: Engagement metrics collected during study sessions (speed, habits, patterns)
- **Model_1**: The Adaptive Difficulty Predictor ML model (already trained)
- **Model_2**: The Question Generation and Assessment ML model (to be determined)
- **Proctoring**: AMCAT-level rule enforcement preventing tab switching, copy-paste, and screenshots
- **RAG_Chat**: Retrieval-Augmented Generation chat interface for content-based questions
- **Whiteboard**: Digital drawing interface with screenshot and download capabilities
- **Weak_Area**: A topic or concept where the user scored below 70% accuracy
- **Difficulty_Level**: A numeric value (1-3) representing question complexity
- **Engagement_Score**: A calculated metric (0-100) representing user focus and participation

## Requirements

### Requirement 1: Study Session Management

**User Story:** As a user, I want to start study sessions with different time configurations, so that I can learn according to my preferred study method.

#### Acceptance Criteria

1. WHEN a user selects Recommended Session mode, THE System SHALL create a 2-hour study session with a flexible 20-minute break available anytime
2. WHEN a user selects Standard Session mode, THE System SHALL create a 50-minute study session with a mandatory 10-minute break
3. WHEN a Recommended Session reaches the 70-minute mark, THE System SHALL display a gentle reminder about the available break
4. WHEN a Recommended Session reaches the 90-minute mark, THE System SHALL display a second gentle reminder about the available break
5. WHEN a user takes a break during a Recommended Session, THE System SHALL pause the study timer and start a 20-minute break timer
6. WHEN a Recommended Session ends without the break being used, THE System SHALL mark the break as expired
7. WHEN a Standard Session completes 50 minutes, THE System SHALL automatically start a 10-minute break timer
8. WHEN a break timer completes, THE System SHALL resume the study session or end the session if study time is complete

### Requirement 2: Content Loading and Display

**User Story:** As a user, I want to load educational content from various sources, so that I can study from my preferred materials.

#### Acceptance Criteria

1. WHEN a user provides a YouTube URL, THE System SHALL extract and display the video with available captions
2. WHEN a user provides a YouTube playlist URL, THE System SHALL extract all videos in the playlist
3. WHEN a user uploads a PDF file, THE System SHALL display the document in a readable format
4. WHEN a user uploads a DOCX file, THE System SHALL display the document content
5. WHEN a user uploads a PPT file, THE System SHALL display the presentation slides
6. WHEN content is loaded, THE System SHALL display a timer showing elapsed study time
7. WHEN content is loaded, THE System SHALL request camera permission for proctoring
8. WHEN content is loaded, THE System SHALL display the RAG-based chat interface
9. WHEN content is loaded, THE System SHALL display the whiteboard interface

### Requirement 3: Content Processing and Storage

**User Story:** As a system, I want to extract and store content from various sources, so that I can generate relevant tests later.

#### Acceptance Criteria

1. WHEN a YouTube URL is provided, THE System SHALL extract captions or transcripts from the video
2. WHEN a YouTube playlist URL is provided, THE System SHALL extract captions from all videos in the playlist
3. WHEN a PDF file is uploaded, THE System SHALL extract all text content
4. WHEN a DOCX file is uploaded, THE System SHALL extract all text content
5. WHEN a PPT file is uploaded, THE System SHALL extract text and slide content
6. WHEN content extraction completes, THE System SHALL store the processed content in the database
7. WHEN content extraction fails, THE System SHALL return a descriptive error message to the user

### Requirement 4: Proctoring and Rule Enforcement

**User Story:** As a system administrator, I want to enforce AMCAT-level proctoring rules, so that study sessions maintain academic integrity.

#### Acceptance Criteria

1. WHEN a user switches tabs during a study session, THE System SHALL record the tab switch event and increment the violation counter
2. WHEN a user attempts to copy text from the content, THE System SHALL prevent the copy operation
3. WHEN a user attempts to paste text into the content area, THE System SHALL prevent the paste operation
4. WHEN a user attempts to take a screenshot of the content, THE System SHALL prevent the screenshot operation
5. WHEN a user takes a screenshot of the whiteboard, THE System SHALL allow the operation
6. WHEN a user takes a screenshot of the chat interface, THE System SHALL allow the operation
7. WHEN the camera permission is granted, THE System SHALL activate proctoring monitoring
8. WHEN the camera permission is denied, THE System SHALL display a warning but allow the session to continue

### Requirement 5: Monitoring Data Collection

**User Story:** As a system, I want to collect engagement metrics during study sessions, so that I can feed accurate data to the ML model for difficulty prediction.

#### Acceptance Criteria

1. WHEN a study session is active, THE System SHALL track the user's study speed by measuring content consumption rate
2. WHEN a study session is active, THE System SHALL track study habits by recording interaction patterns
3. WHEN a study session is active, THE System SHALL track engagement metrics including active time and focus duration
4. WHEN a study session is active, THE System SHALL track content interaction patterns including scrolling, pausing, and replaying
5. WHEN a user interacts with the content, THE System SHALL record the interaction event with timestamp
6. WHEN a user loses focus, THE System SHALL record the focus loss event and duration
7. WHEN a study session ends, THE System SHALL calculate aggregate monitoring metrics
8. WHEN monitoring metrics are calculated, THE System SHALL store them for Model_1 input

### Requirement 6: Automatic Test Generation

**User Story:** As a user, I want tests to be automatically generated after my study session, so that I can immediately assess my understanding.

#### Acceptance Criteria

1. WHEN a study session ends, THE System SHALL automatically trigger test generation
2. WHEN test generation begins, THE System SHALL use only the content from the completed study session
3. WHEN generating questions, THE System SHALL create MCQ questions for recognition and basic understanding
4. WHEN generating questions, THE System SHALL create Short Answer questions for recall and comprehension
5. WHEN generating questions, THE System SHALL create Problem Solving questions for application
6. WHEN generating questions from YouTube content, THE System SHALL use the extracted captions and transcripts
7. WHEN generating questions from PDF content, THE System SHALL use the extracted text
8. WHEN generating questions from DOCX content, THE System SHALL use the extracted text
9. WHEN generating questions from PPT content, THE System SHALL use the extracted slide content
10. WHEN test generation completes, THE System SHALL present the test to the user
11. WHEN test generation fails, THE System SHALL display an error message and allow the user to retry

### Requirement 7: Test Assessment and Scoring

**User Story:** As a user, I want my test answers to be evaluated accurately, so that I receive meaningful feedback on my understanding.

#### Acceptance Criteria

1. WHEN a user submits an MCQ answer, THE System SHALL automatically score it as correct or incorrect
2. WHEN a user submits a Short Answer response, THE System SHALL use Model_2 to evaluate the answer
3. WHEN a user submits a Problem Solving response, THE System SHALL use Model_2 to evaluate the answer
4. WHEN Model_2 evaluates an answer, THE System SHALL provide a correctness score between 0 and 100
5. WHEN all answers are evaluated, THE System SHALL calculate the overall test score as a percentage
6. WHEN the test score is calculated, THE System SHALL identify weak areas where accuracy is below 70%
7. WHEN weak areas are identified, THE System SHALL list the specific topics or concepts
8. WHEN assessment completes, THE System SHALL display the score and weak areas to the user

### Requirement 8: Adaptive Difficulty Prediction

**User Story:** As a system, I want to predict the next difficulty level using ML, so that users receive appropriately challenging content.

#### Acceptance Criteria

1. WHEN a test is completed, THE System SHALL collect monitoring data including study speed, habits, and engagement
2. WHEN a test is completed, THE System SHALL collect test results including scores and weak areas
3. WHEN Model_1 receives input data, THE System SHALL provide accuracy, avg_time_per_question, sessions_completed, first_attempt_correct, mastery_level, and is_new_topic parameters
4. WHEN Model_1 processes the input, THE System SHALL output the next_difficulty value (1, 2, or 3)
5. WHEN the next_difficulty is predicted, THE System SHALL update the user's difficulty level for the topic
6. WHEN the difficulty level changes, THE System SHALL notify the user of the change
7. WHEN the difficulty level remains the same, THE System SHALL provide feedback on current performance

### Requirement 9: ML Model Integration

**User Story:** As a system, I want to integrate two ML models seamlessly, so that question generation and difficulty prediction work together.

#### Acceptance Criteria

1. WHEN Model_1 is initialized, THE System SHALL load the random_forest_classifier_model.joblib file
2. WHEN Model_1 fails to load, THE System SHALL use rule-based fallback logic for difficulty prediction
3. WHEN Model_2 is initialized, THE System SHALL load the question generation model
4. WHEN Model_2 generates questions, THE System SHALL create questions from the processed content
5. WHEN Model_2 assesses answers, THE System SHALL provide correctness scores for Short Answer and Problem Solving questions
6. WHEN Model_2 identifies weak areas, THE System SHALL send the data to Model_1
7. WHEN both models are operational, THE System SHALL coordinate data flow between them

### Requirement 10: Whiteboard Functionality

**User Story:** As a user, I want to use a whiteboard during study sessions, so that I can take notes and work through problems visually.

#### Acceptance Criteria

1. WHEN a study session is active, THE System SHALL display a whiteboard interface
2. WHEN a user draws on the whiteboard, THE System SHALL render the drawing in real-time
3. WHEN a user clicks the screenshot button, THE System SHALL capture the whiteboard content as an image
4. WHEN a user clicks the download button, THE System SHALL download the whiteboard content as a file
5. WHEN a user clears the whiteboard, THE System SHALL remove all drawings
6. WHEN a whiteboard screenshot is taken, THE System SHALL not trigger proctoring violations

### Requirement 11: RAG Chat Integration

**User Story:** As a user, I want to ask questions about the content during study sessions, so that I can clarify my understanding immediately.

#### Acceptance Criteria

1. WHEN a study session is active, THE System SHALL display the RAG chat interface
2. WHEN a user submits a question in the chat, THE System SHALL send the question to the existing RAG backend
3. WHEN the RAG backend responds, THE System SHALL display the response in the chat interface
4. WHEN the chat is used, THE System SHALL record the interaction as an engagement event
5. WHEN the chat is used, THE System SHALL not trigger proctoring violations

### Requirement 12: Data Persistence and Retrieval

**User Story:** As a system, I want to persist all session data and results, so that users can track their progress over time.

#### Acceptance Criteria

1. WHEN a study session starts, THE System SHALL create a session record in the database
2. WHEN monitoring events occur, THE System SHALL append them to the session record
3. WHEN a study session ends, THE System SHALL update the session record with final metrics
4. WHEN a test is generated, THE System SHALL create a test record linked to the session
5. WHEN test answers are submitted, THE System SHALL store them in the database
6. WHEN test results are calculated, THE System SHALL update the test record
7. WHEN a user requests their history, THE System SHALL retrieve all past sessions and test results
8. WHEN a user requests progress analytics, THE System SHALL calculate aggregate statistics from stored data

### Requirement 13: Frontend Integration

**User Story:** As a developer, I want the backend to integrate seamlessly with the existing React frontend, so that the user experience is cohesive.

#### Acceptance Criteria

1. WHEN the frontend calls the session start API, THE System SHALL return a session ID and configuration
2. WHEN the frontend sends monitoring events, THE System SHALL acknowledge receipt and store the data
3. WHEN the frontend requests test questions, THE System SHALL return questions in the expected format
4. WHEN the frontend submits test answers, THE System SHALL return evaluation results
5. WHEN the frontend requests user progress, THE System SHALL return formatted progress data
6. WHEN API errors occur, THE System SHALL return descriptive error messages with appropriate HTTP status codes
7. WHEN the frontend uses existing monitoring.js functions, THE System SHALL support the expected event types

### Requirement 14: Real-Time Monitoring Capabilities

**User Story:** As a system, I want to monitor user engagement in real-time, so that I can provide immediate feedback and accurate data to the ML model.

#### Acceptance Criteria

1. WHEN a user is actively studying, THE System SHALL update engagement metrics every 10 seconds
2. WHEN a user's engagement drops below 50%, THE System SHALL record the low engagement event
3. WHEN a user returns to active engagement, THE System SHALL record the engagement recovery event
4. WHEN monitoring data is updated, THE System SHALL calculate the current engagement score
5. WHEN the engagement score changes significantly, THE System SHALL update the session record

### Requirement 15: Camera and Proctoring Integration

**User Story:** As a system, I want to integrate camera-based proctoring, so that study sessions maintain integrity.

#### Acceptance Criteria

1. WHEN a study session starts, THE System SHALL request camera permission from the user
2. WHEN camera permission is granted, THE System SHALL activate the camera feed
3. WHEN the camera feed is active, THE System SHALL monitor for suspicious behavior
4. WHEN suspicious behavior is detected, THE System SHALL record the event
5. WHEN camera permission is denied, THE System SHALL allow the session to continue with a warning
6. WHEN the camera feed fails, THE System SHALL log the error and continue the session

### Requirement 16: Session Type Configuration

**User Story:** As a user, I want to choose between different session types, so that I can study according to my preferences and schedule.

#### Acceptance Criteria

1. WHEN a user starts a session, THE System SHALL present options for Recommended Session and Standard Session
2. WHEN a user selects a session type, THE System SHALL configure the timer according to the selected type
3. WHEN a session type is configured, THE System SHALL display the session duration and break schedule
4. WHEN a session is in progress, THE System SHALL enforce the rules of the selected session type
5. WHEN a session completes, THE System SHALL record the session type in the database

### Requirement 17: Test Question Distribution

**User Story:** As a system, I want to generate a balanced distribution of question types, so that tests comprehensively assess understanding.

#### Acceptance Criteria

1. WHEN generating a test, THE System SHALL include at least 40% MCQ questions
2. WHEN generating a test, THE System SHALL include at least 30% Short Answer questions
3. WHEN generating a test, THE System SHALL include at least 30% Problem Solving questions
4. WHEN the difficulty level is 1 (Easy), THE System SHALL generate 10 total questions
5. WHEN the difficulty level is 2 (Medium), THE System SHALL generate 12 total questions
6. WHEN the difficulty level is 3 (Hard), THE System SHALL generate 15 total questions
7. WHEN questions are generated, THE System SHALL ensure they cover different concepts from the content

### Requirement 18: Performance and Scalability

**User Story:** As a system administrator, I want the system to handle multiple concurrent sessions, so that many users can study simultaneously.

#### Acceptance Criteria

1. WHEN multiple users start sessions simultaneously, THE System SHALL create separate session records for each user
2. WHEN processing content for multiple users, THE System SHALL queue processing tasks
3. WHEN generating tests for multiple users, THE System SHALL handle requests concurrently
4. WHEN the database is under load, THE System SHALL maintain response times under 2 seconds for API calls
5. WHEN monitoring data is collected from multiple sessions, THE System SHALL batch database writes every 10 seconds
