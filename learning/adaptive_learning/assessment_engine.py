"""
Assessment Engine - Evaluate test answers and calculate scores
"""
from .models import GeneratedTest, TestQuestion, TestSubmission
from django.db.models import Avg, Count, Q


class AssessmentEngine:
    """Evaluate test answers and calculate scores"""
    
    @classmethod
    def evaluate_mcq(cls, question_id, user, selected_index, time_taken):
        """
        Evaluate MCQ answer
        
        Args:
            question_id: TestQuestion ID
            user: User instance
            selected_index: int (0-3)
            time_taken: seconds
            
        Returns:
            TestSubmission instance
        """
        try:
            question = TestQuestion.objects.get(id=question_id, question_type='mcq')
        except TestQuestion.DoesNotExist:
            raise ValueError("MCQ question not found")
        
        # Check if correct
        is_correct = (selected_index == question.correct_answer_index)
        score = 100.0 if is_correct else 0.0
        
        # Create or update submission
        submission, created = TestSubmission.objects.update_or_create(
            question=question,
            user=user,
            defaults={
                'selected_index': selected_index,
                'answer_text': question.options[selected_index] if question.options else '',
                'is_correct': is_correct,
                'score': score,
                'time_taken_seconds': time_taken,
                'evaluated_by_ml': False
            }
        )
        
        return submission
    
    @classmethod
    def evaluate_short_answer(cls, question_id, user, answer_text, time_taken):
        """
        Evaluate Short Answer using ML
        
        Args:
            question_id: TestQuestion ID
            user: User instance
            answer_text: str
            time_taken: seconds
            
        Returns:
            TestSubmission instance
        """
        try:
            question = TestQuestion.objects.get(id=question_id, question_type='short_answer')
        except TestQuestion.DoesNotExist:
            raise ValueError("Short answer question not found")
        
        # Use ML model to evaluate
        try:
            from .question_generator import QuestionGenerator
            qg = QuestionGenerator()
            
            evaluation = qg.assess_answer(
                question.question_text,
                question.expected_answer,
                answer_text,
                'short_answer'
            )
            
            score = evaluation.get('score', 0)
            is_correct = evaluation.get('is_correct', False)
            feedback = evaluation.get('feedback', '')
            ml_confidence = evaluation.get('confidence', 0.5)
            
        except Exception as e:
            # Fallback: simple keyword matching
            score, is_correct, feedback = cls._fallback_evaluate(
                answer_text, question.expected_answer
            )
            ml_confidence = 0.3
        
        # Create or update submission
        submission, created = TestSubmission.objects.update_or_create(
            question=question,
            user=user,
            defaults={
                'answer_text': answer_text,
                'is_correct': is_correct,
                'score': score,
                'feedback': feedback,
                'time_taken_seconds': time_taken,
                'evaluated_by_ml': True,
                'ml_confidence': ml_confidence
            }
        )
        
        return submission
    
    @classmethod
    def evaluate_problem_solving(cls, question_id, user, answer_text, time_taken):
        """
        Evaluate Problem Solving using ML
        
        Args:
            question_id: TestQuestion ID
            user: User instance
            answer_text: str
            time_taken: seconds
            
        Returns:
            TestSubmission instance
        """
        try:
            question = TestQuestion.objects.get(id=question_id, question_type='problem_solving')
        except TestQuestion.DoesNotExist:
            raise ValueError("Problem solving question not found")
        
        # Use ML model to evaluate
        try:
            from .question_generator import QuestionGenerator
            qg = QuestionGenerator()
            
            evaluation = qg.assess_answer(
                question.question_text,
                question.expected_answer,
                answer_text,
                'problem_solving'
            )
            
            score = evaluation.get('score', 0)
            is_correct = evaluation.get('is_correct', False)
            feedback = evaluation.get('feedback', '')
            ml_confidence = evaluation.get('confidence', 0.5)
            
        except Exception as e:
            # Fallback: simple keyword matching
            score, is_correct, feedback = cls._fallback_evaluate(
                answer_text, question.expected_answer
            )
            ml_confidence = 0.3
        
        # Create or update submission
        submission, created = TestSubmission.objects.update_or_create(
            question=question,
            user=user,
            defaults={
                'answer_text': answer_text,
                'is_correct': is_correct,
                'score': score,
                'feedback': feedback,
                'time_taken_seconds': time_taken,
                'evaluated_by_ml': True,
                'ml_confidence': ml_confidence
            }
        )
        
        return submission
    
    @classmethod
    def _fallback_evaluate(cls, answer, expected):
        """Fallback evaluation using keyword matching. NEVER gives free marks."""
        if not answer or not answer.strip():
            return 0.0, False, "No answer provided."
        if not expected or not expected.strip():
            # No reference answer — can't evaluate, give 0
            return 0.0, False, "Could not evaluate answer (no reference provided)."

        # Extract meaningful keywords (>4 chars) from expected answer
        keywords = [w for w in expected.lower().split() if len(w) > 4]

        if not keywords:
            # Reference answer is too short to evaluate properly — partial credit only if they wrote something
            if len(answer.strip()) > 20:
                return 30.0, False, "Answer too short to evaluate accurately. Partial credit given."
            return 0.0, False, "Answer could not be evaluated — too brief."

        # Count matching keywords  
        matches = sum(1 for kw in keywords if kw in answer.lower())
        score = round((matches / len(keywords)) * 100, 1)
        is_correct = score >= 70
        feedback = f"Your answer matched {matches} out of {len(keywords)} key concepts."

        return score, is_correct, feedback
    
    @classmethod
    def calculate_test_score(cls, test_id):
        """
        Calculate overall test score.
        
        Score = (earned points from answered questions) / (total possible points for ALL questions)
        Unanswered questions count as 0 — no free marks.
        """
        try:
            test = GeneratedTest.objects.get(id=test_id)
        except GeneratedTest.DoesNotExist:
            raise ValueError("Test not found")

        # Total possible points = sum of ALL question points in the test
        all_questions = TestQuestion.objects.filter(test=test)
        total_possible_points = sum(q.points for q in all_questions)
        total_questions = all_questions.count()

        if total_questions == 0:
            return {'error': 'No questions in this test'}

        # Only submissions that were actually answered count
        submissions = TestSubmission.objects.filter(
            question__test=test,
            user=test.user
        )
        answered_count = submissions.count()

        # Earned points from answered questions only
        earned_points = 0
        for submission in submissions:
            if submission.score is not None:
                earned_points += (submission.score / 100.0) * submission.question.points

        # Score % = earned / total_possible (not earned / answered_points)
        # This means skipping a question is the same as getting it wrong
        overall_score = round((earned_points / total_possible_points * 100), 1) if total_possible_points > 0 else 0

        correct_answers = submissions.filter(is_correct=True).count()

        # Update test record
        test.score = overall_score
        test.is_completed = True
        test.save()

        return {
            'test_id': test_id,
            'overall_score': overall_score,
            'total_questions': total_questions,
            'answered_questions': answered_count,
            'unanswered_questions': total_questions - answered_count,
            'correct_answers': correct_answers,
            'total_possible_points': total_possible_points,
            'earned_points': round(earned_points, 2),
        }
    
    @classmethod
    def identify_weak_areas(cls, test_id):
        """
        Identify concepts with <70% accuracy
        
        Args:
            test_id: GeneratedTest ID
            
        Returns:
            list of weak concepts
        """
        try:
            test = GeneratedTest.objects.get(id=test_id)
        except GeneratedTest.DoesNotExist:
            raise ValueError("Test not found")
        
        # Group submissions by concept
        submissions = TestSubmission.objects.filter(
            question__test=test,
            user=test.user
        )
        
        concept_stats = {}
        
        for submission in submissions:
            concept = submission.question.concept
            
            if concept not in concept_stats:
                concept_stats[concept] = {'total': 0, 'correct': 0, 'scores': []}
            
            concept_stats[concept]['total'] += 1
            if submission.is_correct:
                concept_stats[concept]['correct'] += 1
            if submission.score is not None:
                concept_stats[concept]['scores'].append(submission.score)
        
        # Identify weak areas
        weak_areas = []
        
        for concept, stats in concept_stats.items():
            avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            if avg_score < 70 or accuracy < 70:
                weak_areas.append({
                    'concept': concept,
                    'accuracy': accuracy,
                    'average_score': avg_score,
                    'questions_count': stats['total']
                })
        
        # Update test weak concepts
        test.weak_concepts = [area['concept'] for area in weak_areas]
        test.save()
        
        return weak_areas
    
    @classmethod
    def prepare_ml_input(cls, test_id, session_id):
        """
        Prepare data for ML difficulty predictor
        
        Args:
            test_id: GeneratedTest ID
            session_id: StudySession ID
            
        Returns:
            dict with ML input data
        """
        from .monitoring_collector import MonitoringCollector
        
        try:
            test = GeneratedTest.objects.get(id=test_id)
        except GeneratedTest.DoesNotExist:
            raise ValueError("Test not found")
        
        # Get test metrics
        submissions = TestSubmission.objects.filter(
            question__test=test,
            user=test.user
        )
        
        total_questions = submissions.count()
        correct_answers = submissions.filter(is_correct=True).count()
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate average time per question
        avg_time = submissions.aggregate(Avg('time_taken_seconds'))['time_taken_seconds__avg'] or 0
        
        # First attempt correct rate (assuming single attempt per question)
        first_attempt_correct = accuracy
        
        # Get session monitoring metrics
        session_metrics = MonitoringCollector.aggregate_metrics(session_id)
        
        # Get user's session count
        from .models import StudySession
        sessions_completed = StudySession.objects.filter(
            user=test.user,
            is_completed=True
        ).count()
        
        # Prepare ML input
        ml_input = {
            'accuracy': accuracy,
            'avg_time_per_question': avg_time,
            'sessions_completed': sessions_completed,
            'first_attempt_correct': first_attempt_correct,
            'mastery_level': min(accuracy / 100, 1.0),
            'is_new_topic': 1 if sessions_completed <= 1 else 0,
            'score_trend': 0,  # Will be calculated from previous sessions
            'current_difficulty': test.difficulty_level,
            'engagement_score': session_metrics.get('engagement_score', 50),
            'study_speed': session_metrics.get('study_speed', 0),
            'weak_concepts': test.weak_concepts
        }
        
        return ml_input

    
    @classmethod
    def generate_difficulty_feedback(cls, current_difficulty, next_difficulty):
        """
        Generate feedback message for difficulty level change
        
        Args:
            current_difficulty: int (1-3)
            next_difficulty: int (1-3)
            
        Returns:
            dict with feedback message
        """
        difficulty_names = {
            1: 'Easy',
            2: 'Medium',
            3: 'Hard'
        }
        
        if next_difficulty > current_difficulty:
            message = f"Great progress! Moving from {difficulty_names[current_difficulty]} to {difficulty_names[next_difficulty]} difficulty."
        elif next_difficulty < current_difficulty:
            message = f"Let's review the basics. Moving from {difficulty_names[current_difficulty]} to {difficulty_names[next_difficulty]} difficulty."
        else:
            message = f"Staying at {difficulty_names[current_difficulty]} difficulty. Keep practicing!"
        
        return {
            'message': message,
            'current_difficulty': current_difficulty,
            'next_difficulty': next_difficulty,
            'change': next_difficulty - current_difficulty
        }
