"""
Test Generator - Automatically generate tests from study session content
"""
from .models import StudySession, GeneratedTest, TestQuestion, Content
import json
import random


class TestGenerator:
    """Generate tests automatically after study sessions"""
    
    # Question distribution by difficulty - Updated to 20-25 questions
    QUESTION_DISTRIBUTION = {
        1: {'total': 20, 'mcq': 8, 'short_answer': 6, 'problem_solving': 6},
        2: {'total': 23, 'mcq': 9, 'short_answer': 7, 'problem_solving': 7},
        3: {'total': 25, 'mcq': 10, 'short_answer': 8, 'problem_solving': 7},
    }
    
    @classmethod
    def generate_test(cls, session_id, difficulty=1):
        """
        Generate complete test from session content
        
        Args:
            session_id: StudySession ID
            difficulty: 1 (Easy), 2 (Medium), 3 (Hard)
            
        Returns:
            GeneratedTest instance
        """
        try:
            session = StudySession.objects.get(id=session_id, is_completed=True)
        except StudySession.DoesNotExist:
            raise ValueError("Session not found or not completed")
        
        # Return existing test if it has questions already
        if hasattr(session, 'generated_test'):
            old_test = session.generated_test
            questions = old_test.questions.all()
            if questions.exists():
                print(f"[TestGen] Returning existing test {old_test.id} with {questions.count()} questions.")
                return old_test
            # Only delete if truly empty (0 questions)
            print(f"[TestGen] Deleting empty test {old_test.id} (0 questions) to regenerate...")
            old_test.delete()

        # Get question distribution
        dist = cls.QUESTION_DISTRIBUTION.get(difficulty, cls.QUESTION_DISTRIBUTION[1])
        
        # Create test
        test = GeneratedTest.objects.create(
            session=session,
            user=session.user,
            difficulty_level=difficulty,
            total_questions=dist['total'],
            mcq_count=dist['mcq'],
            short_answer_count=dist['short_answer'],
            problem_solving_count=dist['problem_solving']
        )

        
        # Get content
        content = session.content
        transcript = content.transcript
        concepts = content.key_concepts
        
        if not transcript or transcript.startswith('Error:'):
            raise ValueError(f"Content transcript unavailable: {transcript[:100] if transcript else 'empty'}")
        
        # Generate questions
        try:
            print(f"[TestGen] Generating MCQ questions via Grok AI...")
            mcq_questions = cls.generate_mcq_questions(
                transcript, concepts, difficulty, dist['mcq']
            )
            
            print(f"[TestGen] Generating Short Answer questions via Grok AI...")
            short_answer_questions = cls.generate_short_answer_questions(
                transcript, concepts, difficulty, dist['short_answer']
            )
            
            print(f"[TestGen] Generating Problem Solving questions via Grok AI...")
            problem_solving_questions = cls.generate_problem_solving_questions(
                transcript, concepts, difficulty, dist['problem_solving']
            )

            all_questions = mcq_questions + short_answer_questions + problem_solving_questions

            # Accept partial question sets — only fail if truly 0 questions generated
            if not all_questions:
                test.delete()
                raise ValueError(
                    "Question generation returned 0 questions. "
                    "Check that content has a valid transcript and concepts are extractable."
                )

            # Warn if we got fewer than expected
            expected = dist['total']
            if len(all_questions) < expected:
                print(f"[TestGen] Warning: Expected {expected} questions, got {len(all_questions)}. Saving partial set.")

            # Save all valid questions
            order = 0
            for q in all_questions:
                TestQuestion.objects.create(
                    test=test,
                    question_type=q['type'],
                    question_text=q['question'],
                    options=q.get('options'),
                    correct_answer_index=q.get('correct_index'),
                    expected_answer=q.get('expected_answer'),
                    explanation=q.get('explanation', ''),
                    concept=q.get('concept', 'General'),
                    difficulty=difficulty,
                    order=order,
                    points=q.get('points', 1)
                )
                order += 1

            # Update test with actual counts generated
            test.total_questions = len(all_questions)
            test.mcq_count = len(mcq_questions)
            test.short_answer_count = len(short_answer_questions)
            test.problem_solving_count = len(problem_solving_questions)
            test.save()

            print(f"[TestGen] Test {test.id} created with {len(all_questions)} questions.")
        
        except ValueError:
            raise
        except Exception as e:
            test.delete()
            raise ValueError(f"Question generation failed: {str(e)}")
        
        return test
    
    @classmethod
    def generate_mcq_questions(cls, content, concepts, difficulty, count):
        """Generate MCQ questions"""
        questions = []
        
        # Use OpenAI or fallback to template-based generation
        try:
            from .question_generator import QuestionGenerator
            qg = QuestionGenerator()
            questions = qg.generate_mcq_questions(content, concepts, difficulty, count)
        except:
            # Fallback: template-based questions
            questions = cls._generate_template_mcq(content, concepts, count)
        
        return questions
    
    @classmethod
    def generate_short_answer_questions(cls, content, concepts, difficulty, count):
        """Generate Short Answer questions"""
        questions = []
        
        try:
            from .question_generator import QuestionGenerator
            qg = QuestionGenerator()
            questions = qg.generate_short_answer_questions(content, concepts, difficulty, count)
        except:
            # Fallback: template-based questions
            questions = cls._generate_template_short_answer(content, concepts, count)
        
        return questions
    
    @classmethod
    def generate_problem_solving_questions(cls, content, concepts, difficulty, count):
        """Generate Problem Solving questions"""
        questions = []
        
        try:
            from .question_generator import QuestionGenerator
            qg = QuestionGenerator()
            questions = qg.generate_problem_solving_questions(content, concepts, difficulty, count)
        except:
            # Fallback: template-based questions
            questions = cls._generate_template_problem_solving(content, concepts, count)
        
        return questions
    
    @classmethod
    def _generate_template_mcq(cls, content, concepts, count):
        """Fallback template-based MCQ generation"""
        questions = []
        
        # Extract sentences from content
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        for i in range(min(count, len(sentences))):
            sentence = sentences[i]
            concept = concepts[i % len(concepts)] if concepts else "General"
            
            questions.append({
                'type': 'mcq',
                'question': f"What is the main idea of: '{sentence[:100]}...'?",
                'options': [
                    f"Option A related to {concept}",
                    f"Option B related to {concept}",
                    f"Option C related to {concept}",
                    f"Option D related to {concept}"
                ],
                'correct_index': 0,
                'explanation': f"This question tests understanding of {concept}.",
                'concept': concept,
                'points': 1
            })
        
        return questions
    
    @classmethod
    def _generate_template_short_answer(cls, content, concepts, count):
        """Fallback template-based Short Answer generation"""
        questions = []
        
        for i in range(count):
            concept = concepts[i % len(concepts)] if concepts else "General"
            
            questions.append({
                'type': 'short_answer',
                'question': f"Explain the concept of {concept} based on the content you studied.",
                'expected_answer': f"A comprehensive explanation of {concept} covering key points from the content.",
                'explanation': f"This question tests recall and comprehension of {concept}.",
                'concept': concept,
                'points': 2
            })
        
        return questions
    
    @classmethod
    def _generate_template_problem_solving(cls, content, concepts, count):
        """Fallback template-based Problem Solving generation"""
        questions = []
        
        for i in range(count):
            concept = concepts[i % len(concepts)] if concepts else "General"
            
            questions.append({
                'type': 'problem_solving',
                'question': f"Apply your knowledge of {concept} to solve a practical problem. Describe your approach and solution.",
                'expected_answer': f"A detailed solution demonstrating application of {concept} principles.",
                'explanation': f"This question tests application and problem-solving skills related to {concept}.",
                'concept': concept,
                'points': 3
            })
        
        return questions
