"""
Email Service - Send test results and notifications
"""
import os
import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


class EmailService:
    """Handle email notifications using SendGrid or Mailgun"""
    
    @staticmethod
    def send_test_results(user, test_result):
        """
        Send test results email to user
        
        Args:
            user: User instance
            test_result: TestResult instance
        
        Returns:
            dict with success status
        """
        # Prepare email data
        subject = f"Test Results - {test_result.total_score:.1f}%"
        
        # Format weak topics
        weak_topics_text = ""
        if test_result.weak_topics:
            weak_topics_text = "\n".join([
                f"  • {topic['name']}: {topic['accuracy']:.1f}% accuracy"
                for topic in test_result.weak_topics
            ])
        else:
            weak_topics_text = "  None - Great job!"
        
        # Email body
        body = f"""
Hello {user.first_name or user.username},

Your test has been completed! Here are your results:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Score: {test_result.total_score:.1f}%
Questions: {test_result.correct_answers}/{test_result.total_questions} correct
Time Taken: {test_result.time_taken_seconds // 60} minutes

BREAKDOWN BY TYPE:
  • Multiple Choice: {test_result.mcq_score:.1f}%
  • Short Answer: {test_result.short_answer_score:.1f}%
  • Problem Solving: {test_result.problem_solving_score:.1f}%

WEAK AREAS (< 70% accuracy):
{weak_topics_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EmailService._get_encouragement_message(test_result.total_score)}

View detailed results and recommendations:
http://localhost:3000/test-results/{test_result.id}

Keep learning!
The Adaptive Learning Team
"""
        
        # Send email based on configured service
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        mailgun_key = os.getenv('MAILGUN_API_KEY')
        
        if sendgrid_key:
            return EmailService._send_via_sendgrid(
                to_email=user.email,
                subject=subject,
                body=body
            )
        elif mailgun_key:
            return EmailService._send_via_mailgun(
                to_email=user.email,
                subject=subject,
                body=body
            )
        else:
            # Fallback: Log to console
            print(f"\n{'='*60}")
            print(f"EMAIL TO: {user.email}")
            print(f"SUBJECT: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'message': 'Email logged to console (no email service configured)',
                'method': 'console'
            }
    
    @staticmethod
    def _send_via_sendgrid(to_email, subject, body):
        """Send email via SendGrid API"""
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('FROM_EMAIL', 'noreply@adaptivelearning.com')
        
        url = "https://api.sendgrid.com/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": from_email},
            "content": [{
                "type": "text/plain",
                "value": body
            }]
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'message': 'Email sent via SendGrid',
                    'method': 'sendgrid'
                }
            else:
                return {
                    'success': False,
                    'error': f'SendGrid error: {response.status_code}',
                    'method': 'sendgrid'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'sendgrid'
            }
    
    @staticmethod
    def _send_via_mailgun(to_email, subject, body):
        """Send email via Mailgun API"""
        api_key = os.getenv('MAILGUN_API_KEY')
        domain = os.getenv('MAILGUN_DOMAIN')
        from_email = os.getenv('FROM_EMAIL', f'noreply@{domain}')
        
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        
        auth = ("api", api_key)
        
        data = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "text": body
        }
        
        try:
            response = requests.post(url, auth=auth, data=data)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Email sent via Mailgun',
                    'method': 'mailgun'
                }
            else:
                return {
                    'success': False,
                    'error': f'Mailgun error: {response.status_code}',
                    'method': 'mailgun'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'mailgun'
            }
    
    @staticmethod
    def _get_encouragement_message(score):
        """Get encouraging message based on score"""
        if score >= 90:
            return "🌟 Outstanding performance! You're mastering this topic!"
        elif score >= 80:
            return "🎯 Great work! You're on the right track!"
        elif score >= 70:
            return "👍 Good job! Keep practicing to improve further."
        elif score >= 60:
            return "💪 You're making progress! Review the weak areas and try again."
        else:
            return "📚 Don't give up! Review the material and practice more."
    
    @staticmethod
    def send_session_reminder(user, session):
        """Send reminder about pending test"""
        subject = "Reminder: Complete Your Test"
        
        body = f"""
Hello {user.first_name or user.username},

You have a pending test from your study session "{session.workspace_name}".

Test expires in: {EmailService._format_time_remaining(session.test_available_until)}

Complete it now: http://localhost:3000/test/{session.generated_test.id}

Best regards,
The Adaptive Learning Team
"""
        
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        mailgun_key = os.getenv('MAILGUN_API_KEY')
        
        if sendgrid_key:
            return EmailService._send_via_sendgrid(user.email, subject, body)
        elif mailgun_key:
            return EmailService._send_via_mailgun(user.email, subject, body)
        else:
            print(f"\nREMINDER EMAIL TO: {user.email}")
            print(body)
            return {'success': True, 'method': 'console'}
    
    @staticmethod
    def _format_time_remaining(expiry_time):
        """Format time remaining until expiry"""
        if not expiry_time:
            return "Unknown"
        
        now = timezone.now()
        if expiry_time < now:
            return "Expired"
        
        delta = expiry_time - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours} hour(s) {minutes} minute(s)"
        else:
            return f"{minutes} minute(s)"
