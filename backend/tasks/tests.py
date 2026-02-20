"""
Tests for the tasks app models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Task, Course, OAuthToken, NotificationPreference


class CourseModelTest(TestCase):
    """Test the Course model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_course(self):
        """Test creating a course."""
        course = Course.objects.create(
            user=self.user,
            name='Introduction to Computer Science',
            code='CS101',
            is_core=True
        )
        self.assertEqual(course.name, 'Introduction to Computer Science')
        self.assertEqual(course.code, 'CS101')
        self.assertTrue(course.is_core)
        self.assertEqual(str(course), 'CS101: Introduction to Computer Science')


class TaskModelTest(TestCase):
    """Test the Task model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            user=self.user,
            name='Data Structures',
            code='CS201',
            is_core=True
        )

    def test_create_task(self):
        """Test creating a task with all fields."""
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Complete homework assignment',
            description='Implement binary search tree',
            deadline=deadline,
            estimated_time_hours=Decimal('5.5'),
            course=self.course,
            is_graded=True,
            is_exam_related=False,
            user_priority='high'
        )
        
        self.assertEqual(task.title, 'Complete homework assignment')
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.course, self.course)
        self.assertTrue(task.is_graded)
        self.assertEqual(task.user_priority, 'high')
        self.assertFalse(task.is_completed)
        self.assertFalse(task.is_deleted)
        self.assertEqual(str(task), 'Complete homework assignment')

    def test_task_default_values(self):
        """Test task default values."""
        deadline = timezone.now() + timedelta(days=1)
        task = Task.objects.create(
            user=self.user,
            title='Simple task',
            deadline=deadline,
            estimated_time_hours=Decimal('1.0')
        )
        
        self.assertEqual(task.urgency_score, Decimal('0.00'))
        self.assertEqual(task.importance_score, Decimal('0.00'))
        self.assertEqual(task.quadrant, 'neither')
        self.assertFalse(task.is_manually_categorized)
        self.assertEqual(task.user_priority, 'medium')
        self.assertFalse(task.is_graded)
        self.assertFalse(task.is_exam_related)

    def test_task_quadrant_choices(self):
        """Test all quadrant choices are valid."""
        deadline = timezone.now() + timedelta(days=1)
        quadrants = [
            'urgent_important',
            'important_not_urgent',
            'urgent_not_important',
            'neither'
        ]
        
        for quadrant in quadrants:
            task = Task.objects.create(
                user=self.user,
                title=f'Task for {quadrant}',
                deadline=deadline,
                estimated_time_hours=Decimal('1.0'),
                quadrant=quadrant
            )
            self.assertEqual(task.quadrant, quadrant)


class OAuthTokenModelTest(TestCase):
    """Test the OAuthToken model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_oauth_token(self):
        """Test creating an OAuth token."""
        expiry = timezone.now() + timedelta(hours=1)
        token = OAuthToken.objects.create(
            user=self.user,
            encrypted_access_token=b'encrypted_access',
            encrypted_refresh_token=b'encrypted_refresh',
            token_expiry=expiry,
            scope='https://www.googleapis.com/auth/calendar'
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.encrypted_access_token, b'encrypted_access')
        self.assertEqual(token.scope, 'https://www.googleapis.com/auth/calendar')
        self.assertEqual(str(token), 'OAuth Token for testuser')


class NotificationPreferenceModelTest(TestCase):
    """Test the NotificationPreference model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_notification_preference(self):
        """Test creating notification preferences."""
        pref = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            push_enabled=False,
            in_app_enabled=True
        )
        
        self.assertTrue(pref.email_enabled)
        self.assertFalse(pref.push_enabled)
        self.assertTrue(pref.in_app_enabled)
        self.assertEqual(str(pref), 'Notification Preferences for testuser')

    def test_notification_preference_defaults(self):
        """Test default values are set correctly."""
        pref = NotificationPreference.objects.create(user=self.user)
        
        # Check defaults are set on save
        self.assertEqual(pref.urgent_important_times, [24, 6, 1])
        self.assertEqual(pref.important_not_urgent_times, [72, 24])
        self.assertEqual(pref.work_days, [1, 2, 3, 4, 5])
        self.assertEqual(pref.work_start_hour, 9)
        self.assertEqual(pref.work_end_hour, 17)

    def test_custom_notification_times(self):
        """Test custom notification timing."""
        pref = NotificationPreference.objects.create(
            user=self.user,
            urgent_important_times=[48, 12, 2],
            important_not_urgent_times=[168, 48],
            work_start_hour=8,
            work_end_hour=18,
            work_days=[1, 2, 3, 4, 5, 6]  # Mon-Sat
        )
        
        self.assertEqual(pref.urgent_important_times, [48, 12, 2])
        self.assertEqual(pref.important_not_urgent_times, [168, 48])
        self.assertEqual(pref.work_start_hour, 8)
        self.assertEqual(pref.work_end_hour, 18)
        self.assertEqual(pref.work_days, [1, 2, 3, 4, 5, 6])


class CategorizationEngineTest(TestCase):
    """Test the categorization engine functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.course = Course.objects.create(
            user=self.user,
            name='Data Structures',
            code='CS201',
            is_core=True
        )

    def test_urgency_score_within_24_hours(self):
        """Test urgency score for deadline within 24 hours."""
        from .categorization import calculate_urgency_score
        
        # Test at various points within 24 hours
        deadline = timezone.now() + timedelta(hours=12)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 1.0)
        
        # Test at exactly 24 hours
        deadline = timezone.now() + timedelta(hours=24)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 1.0)
        
        # Test at 1 hour
        deadline = timezone.now() + timedelta(hours=1)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 1.0)

    def test_urgency_score_within_48_hours(self):
        """Test urgency score for deadline within 48 hours."""
        from .categorization import calculate_urgency_score
        
        # Test at 36 hours (between 24 and 48)
        deadline = timezone.now() + timedelta(hours=36)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.8)
        
        # Test at exactly 48 hours
        deadline = timezone.now() + timedelta(hours=48)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.8)
        
        # Test just over 24 hours
        deadline = timezone.now() + timedelta(hours=25)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.8)

    def test_urgency_score_within_1_week(self):
        """Test urgency score for deadline within 1 week."""
        from .categorization import calculate_urgency_score
        
        # Test at 3 days
        deadline = timezone.now() + timedelta(days=3)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.5)
        
        # Test at exactly 1 week (168 hours)
        deadline = timezone.now() + timedelta(hours=168)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.5)
        
        # Test just over 48 hours
        deadline = timezone.now() + timedelta(hours=72)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.5)

    def test_urgency_score_within_2_weeks(self):
        """Test urgency score for deadline within 2 weeks."""
        from .categorization import calculate_urgency_score
        
        # Test at 10 days
        deadline = timezone.now() + timedelta(days=10)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.3)
        
        # Test at exactly 2 weeks (336 hours)
        deadline = timezone.now() + timedelta(hours=336)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.3)
        
        # Test just over 1 week
        deadline = timezone.now() + timedelta(hours=200)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.3)

    def test_urgency_score_beyond_2_weeks(self):
        """Test urgency score for deadline beyond 2 weeks."""
        from .categorization import calculate_urgency_score
        
        # Test at 1 month
        deadline = timezone.now() + timedelta(days=30)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.1)
        
        # Test at 3 months
        deadline = timezone.now() + timedelta(days=90)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.1)
        
        # Test just over 2 weeks
        deadline = timezone.now() + timedelta(hours=337)
        score = calculate_urgency_score(deadline)
        self.assertEqual(score, 0.1)

    def test_urgency_score_edge_cases(self):
        """Test urgency score edge cases at boundaries."""
        from .categorization import calculate_urgency_score
        
        # Test at exact boundary points
        boundaries = [
            (timedelta(hours=24), 1.0),
            (timedelta(hours=24.1), 0.8),
            (timedelta(hours=48), 0.8),
            (timedelta(hours=48.1), 0.5),
            (timedelta(hours=168), 0.5),
            (timedelta(hours=168.1), 0.3),
            (timedelta(hours=336), 0.3),
            (timedelta(hours=336.1), 0.1),
        ]
        
        for delta, expected_score in boundaries:
            deadline = timezone.now() + delta
            score = calculate_urgency_score(deadline)
            self.assertEqual(
                score, 
                expected_score,
                f"Failed for deadline {delta.total_seconds()/3600} hours away"
            )


    def test_importance_score_graded_only(self):
        """Test importance score for graded assignment only."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Graded assignment',
            deadline=deadline,
            estimated_time_hours=Decimal('2.0'),
            is_graded=True
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.4)

    def test_importance_score_high_time_estimate(self):
        """Test importance score for high time estimate (>4 hours)."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Long task',
            deadline=deadline,
            estimated_time_hours=Decimal('5.0')
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.3)

    def test_importance_score_core_course(self):
        """Test importance score for core course."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Core course task',
            deadline=deadline,
            estimated_time_hours=Decimal('2.0'),
            course=self.course  # self.course is core
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.2)

    def test_importance_score_high_priority(self):
        """Test importance score for user high priority."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='High priority task',
            deadline=deadline,
            estimated_time_hours=Decimal('2.0'),
            user_priority='high'
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.3)

    def test_importance_score_exam_related(self):
        """Test importance score for exam related task."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Exam prep',
            deadline=deadline,
            estimated_time_hours=Decimal('2.0'),
            is_exam_related=True
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.2)

    def test_importance_score_all_factors(self):
        """Test importance score with all factors (should cap at 1.0)."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Maximum importance task',
            deadline=deadline,
            estimated_time_hours=Decimal('6.0'),
            course=self.course,
            is_graded=True,
            is_exam_related=True,
            user_priority='high'
        )
        
        score = calculate_importance_score(task)
        # 0.4 + 0.3 + 0.2 + 0.3 + 0.2 = 1.4, capped at 1.0
        self.assertEqual(score, 1.0)

    def test_importance_score_multiple_factors(self):
        """Test importance score with multiple factors."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Important task',
            deadline=deadline,
            estimated_time_hours=Decimal('5.0'),
            is_graded=True,
            user_priority='high'
        )
        
        score = calculate_importance_score(task)
        # 0.4 (graded) + 0.3 (time) + 0.3 (priority) = 1.0
        self.assertEqual(score, 1.0)

    def test_importance_score_no_factors(self):
        """Test importance score with no special factors."""
        from .categorization import calculate_importance_score
        
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            user=self.user,
            title='Basic task',
            deadline=deadline,
            estimated_time_hours=Decimal('2.0')
        )
        
        score = calculate_importance_score(task)
        self.assertEqual(score, 0.0)
