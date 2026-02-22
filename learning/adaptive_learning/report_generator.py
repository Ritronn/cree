"""
Report Generator - AMCAT/SHL-style comprehensive test report with Gemini AI behavioral analysis

Generates a detailed report after test completion including:
- Score summary with color-coded indicators
- Concept-wise breakdown with progress data
- Behavioral analysis (thinking style, cognitive limits, learning rhythms)
- Response pattern analysis (timing, guessing detection, fatigue)
- Personalized recommendations
"""
import os
import json
import statistics
from django.utils import timezone
from django.db.models import Avg, Count, Q, F


class ReportGenerator:
    """Generate AMCAT-style test reports with behavioral analysis"""

    # Color thresholds (like AMCAT: green ≥67, amber 33-66, red <33)
    COLOR_THRESHOLDS = {
        'green': 67,
        'amber': 33,
    }

    @classmethod
    def generate_report(cls, test_result_id):
        """
        Main entry point: generate a full report for a completed test.

        Args:
            test_result_id: TestResult ID

        Returns:
            TestReport instance
        """
        from .models import TestResult, TestReport

        try:
            test_result = TestResult.objects.select_related(
                'test', 'user', 'session', 'session__content', 'session__content__topic'
            ).get(id=test_result_id)
        except TestResult.DoesNotExist:
            raise ValueError("TestResult not found")

        # Gather all data
        score_summary = cls._build_score_summary(test_result)
        concept_breakdown = cls._build_concept_breakdown(test_result)
        response_patterns = cls._analyze_response_patterns(test_result)

        # Generate behavioral analysis using Gemini AI
        behavioral_analysis = cls._generate_behavioral_analysis(
            test_result, score_summary, concept_breakdown, response_patterns
        )

        # Generate recommendations
        recommendations = cls._generate_recommendations(
            test_result, score_summary, concept_breakdown, behavioral_analysis
        )

        # Persist report
        report, created = TestReport.objects.update_or_create(
            test_result=test_result,
            defaults={
                'user': test_result.user,
                'score_summary': score_summary,
                'concept_breakdown': concept_breakdown,
                'behavioral_analysis': behavioral_analysis,
                'response_patterns': response_patterns,
                'recommendations': recommendations,
            }
        )

        return report

    @classmethod
    def generate_assessment_report(cls, assessment_id):
        """
        Generate a report for a completed Assessment (Gemini MCQ test).
        Works with Assessment + UserAnswer models instead of TestResult.
        
        Returns a simple report object with the same interface as TestReport.
        """
        from .models import Assessment, UserAnswer
        
        assessment = Assessment.objects.select_related(
            'user', 'content', 'content__topic'
        ).get(id=assessment_id, is_completed=True)
        
        answers = UserAnswer.objects.filter(
            question__assessment=assessment,
            user=assessment.user
        ).select_related('question')
        
        total = answers.count()
        correct = answers.filter(is_correct=True).count()
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Build concept breakdown
        concept_stats = {}
        for ans in answers:
            concept = ans.question.concept or 'General'
            if concept not in concept_stats:
                concept_stats[concept] = {'total': 0, 'correct': 0}
            concept_stats[concept]['total'] += 1
            if ans.is_correct:
                concept_stats[concept]['correct'] += 1
        
        concept_breakdown = []
        for concept, stats in concept_stats.items():
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            concept_breakdown.append({
                'concept': concept,
                'questions_count': stats['total'],
                'correct_count': stats['correct'],
                'accuracy': round(acc, 1),
                'color': 'green' if acc >= 67 else 'amber' if acc >= 33 else 'red',
            })
        
        topic_name = assessment.content.topic.name if assessment.content and assessment.content.topic else 'General'
        total_time = sum(a.time_taken_seconds or 0 for a in answers)
        
        # Build a report-like object
        class SimpleReport:
            pass
        
        report = SimpleReport()
        report.score_summary = {
            'overall_score': round(accuracy, 1),
            'total_questions': total,
            'correct_answers': correct,
            'topic_name': topic_name,
            'test_date': assessment.completed_at.strftime('%Y-%m-%d %H:%M') if assessment.completed_at else '',
            'time_taken_formatted': f"{total_time // 60}m {total_time % 60}s",
            'difficulty_name': f"Level {assessment.difficulty_level}",
            'test_number': assessment.test_number,
            'sections': [
                {'name': 'MCQ', 'score': round(accuracy), 'color': 'green' if accuracy >= 67 else 'amber' if accuracy >= 33 else 'red'}
            ],
        }
        report.concept_breakdown = concept_breakdown
        report.behavioral_analysis = {
            'personality_insights': f'Score: {accuracy:.0f}% on {total} questions.',
            'thinking_style': {'type': 'analytical', 'description': '', 'strengths': []},
            'cognitive_profile': {'processing_speed': {'level': 'moderate', 'description': ''}},
            'learning_rhythms': {
                'focus_consistency': {'level': 'moderate', 'description': ''},
                'stamina': {'level': 'moderate', 'description': ''},
            },
            'behavioral_flags': {},
        }
        report.response_patterns = {
            'time_analysis': {'average_seconds': round(total_time / total, 1) if total > 0 else 0, 'fastest_seconds': 0, 'slowest_seconds': 0},
            'fatigue_analysis': {'first_half_accuracy': 0, 'second_half_accuracy': 0, 'fatigue_detected': False},
            'guessing_analysis': {'suspected_guesses': 0},
        }
        
        # Build recommendations
        weak_concepts = [c for c in concept_breakdown if c['accuracy'] < 67]
        recs = []
        for wc in weak_concepts:
            recs.append({
                'message': f"Review '{wc['concept']}' — you scored {wc['accuracy']}%",
                'action': f"Focus on understanding the fundamentals of {wc['concept']}",
            })
        if accuracy < 50:
            recs.append({'message': 'Consider re-watching the content and taking notes', 'action': 'Try active recall techniques'})
        elif accuracy < 70:
            recs.append({'message': 'Good progress! Focus on your weak areas to improve', 'action': 'Your Test 2 will focus on these concepts'})
        else:
            recs.append({'message': 'Great performance! Keep up the excellent work', 'action': 'Challenge yourself with harder content next time'})
        report.recommendations = recs
        
        return report

    # =========================================================================
    # SCORE SUMMARY
    # =========================================================================

    @classmethod
    def _build_score_summary(cls, test_result):
        """Build the top-level score summary like AMCAT's first page"""
        sections = []

        # MCQ Section
        if test_result.test.mcq_count > 0:
            sections.append({
                'name': 'Multiple Choice',
                'short_name': 'MCQ',
                'score': round(test_result.mcq_score, 1),
                'max_score': 100,
                'color': cls._get_color(test_result.mcq_score),
                'question_count': test_result.test.mcq_count,
            })

        # Short Answer Section
        if test_result.test.short_answer_count > 0:
            sections.append({
                'name': 'Short Answer',
                'short_name': 'SA',
                'score': round(test_result.short_answer_score, 1),
                'max_score': 100,
                'color': cls._get_color(test_result.short_answer_score),
                'question_count': test_result.test.short_answer_count,
            })

        # Problem Solving Section
        if test_result.test.problem_solving_count > 0:
            sections.append({
                'name': 'Problem Solving',
                'short_name': 'PS',
                'score': round(test_result.problem_solving_score, 1),
                'max_score': 100,
                'color': cls._get_color(test_result.problem_solving_score),
                'question_count': test_result.test.problem_solving_count,
            })

        return {
            'overall_score': round(test_result.total_score, 1),
            'overall_color': cls._get_color(test_result.total_score),
            'total_questions': test_result.total_questions,
            'correct_answers': test_result.correct_answers,
            'time_taken_seconds': test_result.time_taken_seconds,
            'time_taken_formatted': cls._format_time(test_result.time_taken_seconds),
            'difficulty_level': test_result.test.difficulty_level,
            'difficulty_name': {1: 'Easy', 2: 'Medium', 3: 'Hard'}.get(
                test_result.test.difficulty_level, 'Unknown'
            ),
            'test_date': test_result.completed_at.strftime('%B %d, %Y') if test_result.completed_at else '',
            'sections': sections,
            'topic_name': (
                test_result.session.content.topic.name
                if test_result.session and test_result.session.content
                and test_result.session.content.topic
                else 'General'
            ),
        }

    # =========================================================================
    # CONCEPT BREAKDOWN
    # =========================================================================

    @classmethod
    def _build_concept_breakdown(cls, test_result):
        """Build per-concept scores like AMCAT's Logical/Quant/English sections"""
        from .models import TestSubmission

        submissions = TestSubmission.objects.filter(
            question__test=test_result.test,
            user=test_result.user
        ).select_related('question')

        concept_data = {}
        for sub in submissions:
            concept = sub.question.concept
            if concept not in concept_data:
                concept_data[concept] = {
                    'correct': 0,
                    'total': 0,
                    'scores': [],
                    'times': [],
                    'difficulty_levels': [],
                }
            concept_data[concept]['total'] += 1
            concept_data[concept]['scores'].append(sub.score or 0)
            concept_data[concept]['times'].append(sub.time_taken_seconds or 0)
            concept_data[concept]['difficulty_levels'].append(sub.question.difficulty)
            if sub.is_correct or (sub.score and sub.score >= 70):
                concept_data[concept]['correct'] += 1

        breakdown = []
        for concept, data in concept_data.items():
            accuracy = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0

            breakdown.append({
                'concept': concept,
                'accuracy': round(accuracy, 1),
                'average_score': round(avg_score, 1),
                'color': cls._get_color(accuracy),
                'questions_count': data['total'],
                'correct_count': data['correct'],
                'avg_time_seconds': round(avg_time, 1),
                'avg_difficulty': round(
                    sum(data['difficulty_levels']) / len(data['difficulty_levels']), 1
                ) if data['difficulty_levels'] else 1,
            })

        # Sort by accuracy (weakest first)
        breakdown.sort(key=lambda x: x['accuracy'])
        return breakdown

    # =========================================================================
    # RESPONSE PATTERN ANALYSIS
    # =========================================================================

    @classmethod
    def _analyze_response_patterns(cls, test_result):
        """Analyze timing patterns, guessing, fatigue, etc."""
        from .models import TestSubmission

        submissions = list(
            TestSubmission.objects.filter(
                question__test=test_result.test,
                user=test_result.user
            ).select_related('question').order_by('question__order')
        )

        if not submissions:
            return cls._empty_response_patterns()

        times = [s.time_taken_seconds or 0 for s in submissions]
        scores = [s.score or 0 for s in submissions]
        correctness = [1 if s.is_correct else 0 for s in submissions]

        # Time statistics
        avg_time = statistics.mean(times) if times else 0
        median_time = statistics.median(times) if times else 0
        time_std = statistics.stdev(times) if len(times) > 1 else 0

        # Split into halves for fatigue detection
        mid = len(submissions) // 2
        first_half_correct = sum(correctness[:mid]) / mid if mid > 0 else 0
        second_half_correct = sum(correctness[mid:]) / (len(correctness) - mid) if (len(correctness) - mid) > 0 else 0
        first_half_avg_time = statistics.mean(times[:mid]) if mid > 0 else 0
        second_half_avg_time = statistics.mean(times[mid:]) if (len(times) - mid) > 0 else 0

        # Guessing detection: very fast answers that are wrong
        fast_threshold = max(avg_time * 0.3, 5)  # 30% of avg or 5 seconds
        guessed_count = sum(
            1 for s in submissions
            if (s.time_taken_seconds or 0) < fast_threshold and not s.is_correct
        )

        # Overtime answers: significantly more time than average
        slow_threshold = avg_time * 2.0
        overtime_count = sum(
            1 for s in submissions
            if (s.time_taken_seconds or 0) > slow_threshold
        )

        # Time quartile analysis
        total_q = len(submissions)
        quartile_size = max(total_q // 4, 1)
        q1_acc = sum(correctness[:quartile_size]) / quartile_size if quartile_size else 0
        q4_acc = sum(correctness[-quartile_size:]) / quartile_size if quartile_size else 0

        return {
            'total_questions_attempted': len(submissions),
            'total_questions_in_test': test_result.total_questions,
            'unanswered': test_result.total_questions - len(submissions),
            'time_analysis': {
                'average_seconds': round(avg_time, 1),
                'median_seconds': round(median_time, 1),
                'std_deviation': round(time_std, 1),
                'fastest_seconds': min(times) if times else 0,
                'slowest_seconds': max(times) if times else 0,
                'total_seconds': sum(times),
            },
            'fatigue_analysis': {
                'first_half_accuracy': round(first_half_correct * 100, 1),
                'second_half_accuracy': round(second_half_correct * 100, 1),
                'accuracy_drop': round((first_half_correct - second_half_correct) * 100, 1),
                'first_half_avg_time': round(first_half_avg_time, 1),
                'second_half_avg_time': round(second_half_avg_time, 1),
                'time_increase': round(second_half_avg_time - first_half_avg_time, 1),
                'fatigue_detected': (first_half_correct - second_half_correct) > 0.15,
            },
            'guessing_analysis': {
                'suspected_guesses': guessed_count,
                'guess_rate': round(guessed_count / len(submissions) * 100, 1) if submissions else 0,
                'fast_threshold_seconds': round(fast_threshold, 1),
            },
            'overtime_analysis': {
                'overtime_count': overtime_count,
                'overtime_rate': round(overtime_count / len(submissions) * 100, 1) if submissions else 0,
                'slow_threshold_seconds': round(slow_threshold, 1),
            },
            'accuracy_progression': {
                'q1_accuracy': round(q1_acc * 100, 1),
                'q4_accuracy': round(q4_acc * 100, 1),
                'trend': 'improving' if q4_acc > q1_acc else ('declining' if q4_acc < q1_acc else 'stable'),
            },
            'per_question_times': [
                {
                    'question_order': s.question.order,
                    'time_seconds': s.time_taken_seconds or 0,
                    'correct': s.is_correct,
                    'concept': s.question.concept,
                }
                for s in submissions
            ],
        }

    @classmethod
    def _empty_response_patterns(cls):
        return {
            'total_questions_attempted': 0,
            'total_questions_in_test': 0,
            'unanswered': 0,
            'time_analysis': {},
            'fatigue_analysis': {},
            'guessing_analysis': {},
            'overtime_analysis': {},
            'accuracy_progression': {},
            'per_question_times': [],
        }

    # =========================================================================
    # BEHAVIORAL ANALYSIS (GEMINI AI)
    # =========================================================================

    @classmethod
    def _generate_behavioral_analysis(cls, test_result, score_summary, concept_breakdown, response_patterns):
        """Use Gemini AI to generate deep behavioral analysis"""

        # Gather session metrics if available
        session_metrics = cls._get_session_metrics(test_result)

        # Build the prompt for Gemini
        prompt = cls._build_analysis_prompt(
            test_result, score_summary, concept_breakdown,
            response_patterns, session_metrics
        )

        # Call Gemini
        try:
            analysis = cls._call_gemini(prompt)
            return analysis
        except Exception as e:
            print(f"[ReportGenerator] Gemini analysis failed: {e}")
            return cls._fallback_behavioral_analysis(
                score_summary, concept_breakdown, response_patterns
            )

    @classmethod
    def _get_session_metrics(cls, test_result):
        """Get session metrics and proctoring data"""
        from .models import SessionMetrics, ProctoringEvent

        metrics_data = {}
        try:
            metrics = SessionMetrics.objects.get(session=test_result.session)
            metrics_data = {
                'engagement_score': metrics.engagement_score,
                'study_speed': metrics.study_speed,
                'tab_switches': metrics.total_tab_switches,
                'focus_losses': metrics.total_focus_losses,
                'avg_focus_duration': metrics.average_focus_duration_seconds,
                'active_time_ratio': metrics.active_time_ratio,
                'chat_queries': metrics.chat_queries_count,
                'whiteboard_usage': metrics.whiteboard_snapshots_count,
            }
        except SessionMetrics.DoesNotExist:
            pass

        # Proctoring events summary
        proctoring = ProctoringEvent.objects.filter(
            session=test_result.session
        ).values('event_type').annotate(count=Count('id'))

        metrics_data['proctoring_events'] = {
            item['event_type']: item['count'] for item in proctoring
        }

        return metrics_data

    @classmethod
    def _build_analysis_prompt(cls, test_result, score_summary, concept_breakdown, response_patterns, session_metrics):
        """Build the Gemini prompt for behavioral analysis"""

        user_name = test_result.user.first_name or test_result.user.username
        topic = score_summary.get('topic_name', 'General')

        prompt = f"""You are an educational psychologist and cognitive assessment expert. Analyze this student's test performance data and produce a detailed behavioral analysis report.

STUDENT: {user_name}
TOPIC: {topic}
DIFFICULTY: {score_summary.get('difficulty_name', 'Unknown')}
OVERALL SCORE: {score_summary['overall_score']}%

SECTION SCORES:
{json.dumps(score_summary['sections'], indent=2)}

CONCEPT BREAKDOWN (weakest first):
{json.dumps(concept_breakdown, indent=2)}

RESPONSE PATTERNS:
- Average time per question: {response_patterns.get('time_analysis', {}).get('average_seconds', 0)} seconds
- Median time: {response_patterns.get('time_analysis', {}).get('median_seconds', 0)} seconds
- Fastest answer: {response_patterns.get('time_analysis', {}).get('fastest_seconds', 0)}s
- Slowest answer: {response_patterns.get('time_analysis', {}).get('slowest_seconds', 0)}s
- First half accuracy: {response_patterns.get('fatigue_analysis', {}).get('first_half_accuracy', 0)}%
- Second half accuracy: {response_patterns.get('fatigue_analysis', {}).get('second_half_accuracy', 0)}%
- Suspected guesses: {response_patterns.get('guessing_analysis', {}).get('suspected_guesses', 0)} ({response_patterns.get('guessing_analysis', {}).get('guess_rate', 0)}%)
- Overtime questions: {response_patterns.get('overtime_analysis', {}).get('overtime_count', 0)}
- Accuracy trend: {response_patterns.get('accuracy_progression', {}).get('trend', 'unknown')}

SESSION METRICS:
{json.dumps(session_metrics, indent=2)}

Produce a JSON response with EXACTLY this structure (no markdown, no code fences, only valid JSON):
{{
    "thinking_style": {{
        "type": "analytical|intuitive|balanced|methodical|creative",
        "description": "2-3 sentence description of their dominant thinking approach",
        "strengths": ["strength1", "strength2", "strength3"],
        "areas_to_develop": ["area1", "area2"]
    }},
    "cognitive_profile": {{
        "processing_speed": {{
            "level": "fast|moderate|slow",
            "description": "1-2 sentences about their processing speed"
        }},
        "accuracy_tendency": {{
            "level": "high|moderate|low",
            "description": "1-2 sentences about their accuracy patterns"
        }},
        "conceptual_understanding": {{
            "level": "deep|surface|mixed",
            "description": "1-2 sentences based on concept breakdown"
        }},
        "problem_solving_approach": {{
            "level": "systematic|trial-and-error|mixed",
            "description": "1-2 sentences about problem-solving"
        }}
    }},
    "learning_rhythms": {{
        "stamina": {{
            "level": "high|moderate|low",
            "description": "Based on fatigue analysis and accuracy progression"
        }},
        "focus_consistency": {{
            "level": "consistent|variable|declining",
            "description": "Based on session metrics and time patterns"
        }},
        "optimal_session_length": "Recommended study session duration based on data",
        "peak_performance_window": "When during the test they performed best"
    }},
    "behavioral_flags": {{
        "guessing_tendency": "none|mild|moderate|high",
        "time_pressure_sensitivity": "low|moderate|high",
        "fatigue_impact": "minimal|noticeable|significant",
        "engagement_level": "high|moderate|low"
    }},
    "personality_insights": "A 3-4 sentence paragraph describing the learner's overall cognitive personality, written in second person (you/your), in an encouraging but honest tone. Include specific observations from the data."
}}"""

        return prompt

    @classmethod
    def _call_gemini(cls, prompt):
        """Call Gemini API for behavioral analysis"""
        import google.generativeai as genai

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            from django.conf import settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)

        if not api_key:
            raise ValueError("No Gemini API key configured")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=2000,
            )
        )

        # Parse JSON from response
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith('```'):
            text = text.split('\n', 1)[1] if '\n' in text else text[3:]
        if text.endswith('```'):
            text = text.rsplit('```', 1)[0]
        if text.startswith('json'):
            text = text[4:].strip()

        return json.loads(text)

    @classmethod
    def _fallback_behavioral_analysis(cls, score_summary, concept_breakdown, response_patterns):
        """Fallback analysis when Gemini is unavailable"""
        overall = score_summary['overall_score']
        fatigue = response_patterns.get('fatigue_analysis', {})
        guessing = response_patterns.get('guessing_analysis', {})
        time_data = response_patterns.get('time_analysis', {})

        # Determine thinking style
        avg_time = time_data.get('average_seconds', 30)
        if avg_time > 60:
            thinking_type = 'methodical'
            speed_level = 'slow'
        elif avg_time > 30:
            thinking_type = 'analytical'
            speed_level = 'moderate'
        else:
            thinking_type = 'intuitive'
            speed_level = 'fast'

        # Accuracy tendency
        if overall >= 70:
            acc_level = 'high'
        elif overall >= 40:
            acc_level = 'moderate'
        else:
            acc_level = 'low'

        # Fatigue
        acc_drop = fatigue.get('accuracy_drop', 0)
        if acc_drop > 20:
            fatigue_level = 'significant'
            stamina = 'low'
        elif acc_drop > 10:
            fatigue_level = 'noticeable'
            stamina = 'moderate'
        else:
            fatigue_level = 'minimal'
            stamina = 'high'

        # Guessing
        guess_rate = guessing.get('guess_rate', 0)
        if guess_rate > 30:
            guess_level = 'high'
        elif guess_rate > 15:
            guess_level = 'moderate'
        elif guess_rate > 5:
            guess_level = 'mild'
        else:
            guess_level = 'none'

        # Strong and weak concepts
        strong_concepts = [c['concept'] for c in concept_breakdown if c['accuracy'] >= 70]
        weak_concepts = [c['concept'] for c in concept_breakdown if c['accuracy'] < 50]

        return {
            'thinking_style': {
                'type': thinking_type,
                'description': f'Based on your response patterns, you tend toward a {thinking_type} thinking style. '
                               f'You spend an average of {avg_time:.0f} seconds per question.',
                'strengths': strong_concepts[:3] if strong_concepts else ['Consistent effort'],
                'areas_to_develop': weak_concepts[:3] if weak_concepts else ['Continue practicing'],
            },
            'cognitive_profile': {
                'processing_speed': {
                    'level': speed_level,
                    'description': f'Average response time of {avg_time:.0f}s per question.',
                },
                'accuracy_tendency': {
                    'level': acc_level,
                    'description': f'Overall accuracy of {overall}%.',
                },
                'conceptual_understanding': {
                    'level': 'deep' if overall >= 70 else 'surface' if overall < 40 else 'mixed',
                    'description': f'{len(strong_concepts)} concepts mastered, {len(weak_concepts)} need work.',
                },
                'problem_solving_approach': {
                    'level': 'systematic' if avg_time > 40 else 'mixed',
                    'description': 'Based on time distribution across questions.',
                },
            },
            'learning_rhythms': {
                'stamina': {
                    'level': stamina,
                    'description': f'Accuracy dropped {acc_drop:.0f}% from first to second half.',
                },
                'focus_consistency': {
                    'level': 'consistent' if abs(acc_drop) < 10 else 'declining',
                    'description': 'Based on performance across the test duration.',
                },
                'optimal_session_length': '25-30 minutes' if stamina == 'low' else '45-50 minutes',
                'peak_performance_window': 'First half of the test' if acc_drop > 0 else 'Consistent throughout',
            },
            'behavioral_flags': {
                'guessing_tendency': guess_level,
                'time_pressure_sensitivity': 'high' if guess_rate > 20 else 'moderate' if guess_rate > 10 else 'low',
                'fatigue_impact': fatigue_level,
                'engagement_level': 'high' if overall >= 60 else 'moderate' if overall >= 30 else 'low',
            },
            'personality_insights': (
                f'You demonstrate a {thinking_type} approach to problem-solving with {acc_level} accuracy. '
                f'Your stamina during tests is {stamina}, and you {"show signs of fatigue toward the end" if acc_drop > 10 else "maintain consistent performance throughout"}. '
                f'{"Be careful of rushing through questions — " if guess_level in ("moderate", "high") else ""}'
                f'Focus on strengthening your understanding in weaker areas to boost your overall performance.'
            ),
        }

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    @classmethod
    def _generate_recommendations(cls, test_result, score_summary, concept_breakdown, behavioral_analysis):
        """Generate personalized study recommendations"""
        recommendations = []

        # Weak concept recommendations
        for concept in concept_breakdown:
            if concept['accuracy'] < 70:
                priority = 'high' if concept['accuracy'] < 33 else 'medium'
                recommendations.append({
                    'type': 'concept_review',
                    'priority': priority,
                    'concept': concept['concept'],
                    'current_accuracy': concept['accuracy'],
                    'message': f"Review '{concept['concept']}' — currently at {concept['accuracy']}% accuracy.",
                    'action': f"Practice more questions on {concept['concept']} at the current difficulty level.",
                })

        # Behavioral recommendations
        behavioral_flags = behavioral_analysis.get('behavioral_flags', {})

        if behavioral_flags.get('guessing_tendency') in ('moderate', 'high'):
            recommendations.append({
                'type': 'behavioral',
                'priority': 'high',
                'concept': 'Test Strategy',
                'message': 'You appear to be guessing on some questions. Slow down and read carefully.',
                'action': 'Try eliminating obviously wrong options before selecting your answer.',
            })

        if behavioral_flags.get('fatigue_impact') in ('noticeable', 'significant'):
            recommendations.append({
                'type': 'behavioral',
                'priority': 'medium',
                'concept': 'Stamina',
                'message': 'Your performance drops toward the end of the test, suggesting fatigue.',
                'action': 'Practice with timed sessions to build test endurance. Take short breaks during study.',
            })

        if behavioral_flags.get('time_pressure_sensitivity') == 'high':
            recommendations.append({
                'type': 'behavioral',
                'priority': 'medium',
                'concept': 'Time Management',
                'message': 'You seem sensitive to time pressure.',
                'action': 'Practice timed quizzes to improve speed without sacrificing accuracy.',
            })

        # Overall performance encouragement
        overall = score_summary['overall_score']
        if overall >= 80:
            recommendations.append({
                'type': 'encouragement',
                'priority': 'low',
                'concept': 'Overall',
                'message': '🌟 Excellent performance! You\'re mastering this material.',
                'action': 'Consider moving to a higher difficulty level for a greater challenge.',
            })
        elif overall >= 60:
            recommendations.append({
                'type': 'encouragement',
                'priority': 'low',
                'concept': 'Overall',
                'message': '👍 Good progress! You have a solid foundation.',
                'action': 'Focus on the weak areas above and you\'ll see significant improvement.',
            })
        else:
            recommendations.append({
                'type': 'encouragement',
                'priority': 'low',
                'concept': 'Overall',
                'message': '💪 Keep going! Every test is a learning opportunity.',
                'action': 'Review the study materials again and practice with easier questions first.',
            })

        return recommendations

    # =========================================================================
    # HELPERS
    # =========================================================================

    @classmethod
    def _get_color(cls, score):
        """Return color code based on AMCAT thresholds"""
        if score >= cls.COLOR_THRESHOLDS['green']:
            return 'green'
        elif score >= cls.COLOR_THRESHOLDS['amber']:
            return 'amber'
        else:
            return 'red'

    @classmethod
    def _format_time(cls, seconds):
        """Format seconds into human-readable time"""
        if not seconds:
            return '0 minutes'
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
