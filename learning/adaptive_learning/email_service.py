"""
Email Service - Send AMCAT-style HTML test reports via Resend / Gmail SMTP / SendGrid / Mailgun

Provider priority:
  1. Resend  (RESEND_API_KEY)     — Free 3,000 emails/month, modern API
  2. Gmail SMTP (GMAIL_APP_PASSWORD) — Free, zero dependencies, uses Django email
  3. SendGrid (SENDGRID_API_KEY)   — Backup
  4. Mailgun  (MAILGUN_API_KEY)    — Backup
  5. Console fallback              — Prints to terminal
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from django.template.loader import render_to_string
from django.utils import timezone


class EmailService:
    """Handle email notifications via Resend, Gmail SMTP, SendGrid, or Mailgun"""

    @staticmethod
    def send_test_report(user, test_result, report):
        """
        Send comprehensive AMCAT-style HTML test report email.

        Args:
            user: User instance
            test_result: TestResult instance
            report: TestReport instance (with behavioral analysis)

        Returns:
            dict with success status
        """
        subject = (
            f"📊 Your Test Report — {report.score_summary.get('overall_score', 0)}% "
            f"| {report.score_summary.get('topic_name', 'Test')}"
        )

        # Build template context
        behavioral = report.behavioral_analysis or {}
        thinking_style = behavioral.get('thinking_style', {})
        cognitive = behavioral.get('cognitive_profile', {})
        rhythms = behavioral.get('learning_rhythms', {})
        flags = behavioral.get('behavioral_flags', {})
        time_analysis = (report.response_patterns or {}).get('time_analysis', {})
        fatigue = (report.response_patterns or {}).get('fatigue_analysis', {})
        guessing = (report.response_patterns or {}).get('guessing_analysis', {})

        context = {
            'user_name': user.first_name or user.username,
            'overall_score': report.score_summary.get('overall_score', 0),
            'test_date': report.score_summary.get('test_date', ''),
            'topic_name': report.score_summary.get('topic_name', 'General'),
            'total_questions': report.score_summary.get('total_questions', 0),
            'correct_answers': report.score_summary.get('correct_answers', 0),
            'time_taken': report.score_summary.get('time_taken_formatted', ''),
            'sections': report.score_summary.get('sections', []),
            'concepts': report.concept_breakdown or [],

            # Behavioral
            'personality_insights': behavioral.get('personality_insights', ''),
            'thinking_style_type': thinking_style.get('type', ''),
            'thinking_style_desc': thinking_style.get('description', ''),
            'processing_speed': cognitive.get('processing_speed', {}).get('level', ''),
            'processing_speed_desc': cognitive.get('processing_speed', {}).get('description', ''),
            'focus_consistency': rhythms.get('focus_consistency', {}).get('level', ''),
            'focus_desc': rhythms.get('focus_consistency', {}).get('description', ''),
            'stamina_level': rhythms.get('stamina', {}).get('level', ''),
            'stamina_desc': rhythms.get('stamina', {}).get('description', ''),

            # Response patterns
            'avg_time': time_analysis.get('average_seconds', 0),
            'fastest_time': time_analysis.get('fastest_seconds', 0),
            'slowest_time': time_analysis.get('slowest_seconds', 0),
            'guess_count': guessing.get('suspected_guesses', 0),
            'first_half_acc': fatigue.get('first_half_accuracy', 0),
            'second_half_acc': fatigue.get('second_half_accuracy', 0),
            'fatigue_detected': fatigue.get('fatigue_detected', False),

            # Recommendations & strengths
            'recommendations': report.recommendations or [],
            'strengths': thinking_style.get('strengths', []),
        }

        # Render HTML template
        try:
            html_body = render_to_string('email/test_report.html', context)
        except Exception as e:
            print(f"[EmailService] Template render failed: {e}")
            # Fallback to plain text
            return EmailService._send_plain_text_fallback(user, test_result, report)

        # Also build a plain-text version for email clients that don't support HTML
        plain_body = EmailService._build_plain_text(user, report)

        # Send via configured service (priority: Resend > Gmail SMTP > SendGrid > Mailgun > console)
        return EmailService._dispatch_email(
            to_email=user.email,
            subject=subject,
            html_body=html_body,
            plain_body=plain_body,
        )

    @staticmethod
    def _dispatch_email(to_email, subject, html_body, plain_body):
        """Route email through the first available provider"""
        resend_key = os.getenv('RESEND_API_KEY')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        mailgun_key = os.getenv('MAILGUN_API_KEY')

        if resend_key:
            return EmailService._send_via_resend(to_email, subject, html_body, plain_body)
        elif gmail_password:
            return EmailService._send_via_gmail_smtp(to_email, subject, html_body, plain_body)
        elif sendgrid_key:
            return EmailService._send_via_sendgrid(to_email, subject, html_body, plain_body)
        elif mailgun_key:
            return EmailService._send_via_mailgun(to_email, subject, html_body, plain_body)
        else:
            # Console fallback
            print(f"\n{'=' * 70}")
            print(f"📧 EMAIL TO: {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"{'=' * 70}")
            print(plain_body)
            print(f"{'=' * 70}")
            print(f"(Configure RESEND_API_KEY or GMAIL_APP_PASSWORD in .env to send emails)")
            print(f"{'=' * 70}\n")
            return {
                'success': True,
                'message': 'Report email logged to console (no email service configured)',
                'method': 'console'
            }

    # =====================================================================
    # EMAIL PROVIDERS
    # =====================================================================

    @staticmethod
    def _send_via_resend(to_email, subject, html_body, plain_body):
        """Send HTML email via Resend API (https://resend.com) — Free 3,000/month"""
        api_key = os.getenv('RESEND_API_KEY')
        from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')

        url = "https://api.resend.com/emails"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": plain_body,
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return {'success': True, 'message': 'Report email sent via Resend', 'method': 'resend'}
            else:
                return {'success': False, 'error': f'Resend error: {response.status_code} - {response.text}', 'method': 'resend'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'resend'}

    @staticmethod
    def _send_via_gmail_smtp(to_email, subject, html_body, plain_body):
        """Send HTML email via Gmail SMTP — Free, zero extra dependencies"""
        gmail_user = os.getenv('GMAIL_EMAIL')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')  # App password, NOT regular password
        from_name = os.getenv('FROM_NAME', 'Velocity Learning')

        if not gmail_user or not gmail_password:
            return {'success': False, 'error': 'GMAIL_EMAIL and GMAIL_APP_PASSWORD required', 'method': 'gmail_smtp'}

        # Build MIME message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{gmail_user}>"
        msg['To'] = to_email

        msg.attach(MIMEText(plain_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, to_email, msg.as_string())
            return {'success': True, 'message': 'Report email sent via Gmail SMTP', 'method': 'gmail_smtp'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'gmail_smtp'}

    @staticmethod
    def _send_via_sendgrid(to_email, subject, html_body, plain_body):
        """Send HTML email via SendGrid API"""
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('FROM_EMAIL', 'noreply@velocity-learning.com')
        from_name = os.getenv('FROM_NAME', 'Velocity Learning')

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
            "from": {"email": from_email, "name": from_name},
            "content": [
                {"type": "text/plain", "value": plain_body},
                {"type": "text/html", "value": html_body},
            ]
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 202:
                return {'success': True, 'message': 'Report email sent via SendGrid', 'method': 'sendgrid'}
            else:
                return {'success': False, 'error': f'SendGrid error: {response.status_code} - {response.text}', 'method': 'sendgrid'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'sendgrid'}

    @staticmethod
    def _send_via_mailgun(to_email, subject, html_body, plain_body):
        """Send HTML email via Mailgun API"""
        api_key = os.getenv('MAILGUN_API_KEY')
        domain = os.getenv('MAILGUN_DOMAIN')
        from_email = os.getenv('FROM_EMAIL', f'noreply@{domain}')

        url = f"https://api.mailgun.net/v3/{domain}/messages"

        try:
            response = requests.post(
                url,
                auth=("api", api_key),
                data={
                    "from": from_email,
                    "to": to_email,
                    "subject": subject,
                    "text": plain_body,
                    "html": html_body,
                },
                timeout=30
            )
            if response.status_code == 200:
                return {'success': True, 'message': 'Report email sent via Mailgun', 'method': 'mailgun'}
            else:
                return {'success': False, 'error': f'Mailgun error: {response.status_code}', 'method': 'mailgun'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'mailgun'}

    @staticmethod
    def _build_plain_text(user, report):
        """Build plain-text version of the report"""
        ss = report.score_summary or {}
        ba = report.behavioral_analysis or {}
        rp = report.response_patterns or {}
        thinking = ba.get('thinking_style', {})
        rhythms = ba.get('learning_rhythms', {})
        time_data = rp.get('time_analysis', {})
        fatigue = rp.get('fatigue_analysis', {})

        lines = [
            f"Hello {user.first_name or user.username},",
            "",
            "Your test has been completed! Here is your comprehensive report:",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  TEST REPORT",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"  Topic: {ss.get('topic_name', 'General')}",
            f"  Overall Score: {ss.get('overall_score', 0)}%",
            f"  Questions: {ss.get('correct_answers', 0)}/{ss.get('total_questions', 0)} correct",
            f"  Time Taken: {ss.get('time_taken_formatted', '')}",
            f"  Difficulty: {ss.get('difficulty_name', '')}",
            "",
        ]

        # Section scores
        for section in ss.get('sections', []):
            icon = '🟢' if section['color'] == 'green' else '🟡' if section['color'] == 'amber' else '🔴'
            lines.append(f"  {icon} {section['name']}: {section['score']}/100")
        lines.append("")

        # Concept breakdown
        lines.append("──── CONCEPT BREAKDOWN ────")
        for concept in (report.concept_breakdown or []):
            icon = '🟢' if concept['color'] == 'green' else '🟡' if concept['color'] == 'amber' else '🔴'
            lines.append(f"  {icon} {concept['concept']}: {concept['accuracy']}% ({concept['correct_count']}/{concept['questions_count']})")
        lines.append("")

        # Behavioral analysis
        lines.append("──── BEHAVIORAL ANALYSIS ────")
        if ba.get('personality_insights'):
            lines.append(f"  {ba['personality_insights']}")
            lines.append("")
        lines.append(f"  Thinking Style: {thinking.get('type', 'N/A').title()}")
        lines.append(f"  Stamina: {rhythms.get('stamina', {}).get('level', 'N/A').title()}")
        lines.append(f"  Focus: {rhythms.get('focus_consistency', {}).get('level', 'N/A').title()}")
        lines.append("")

        # Response patterns
        lines.append("──── RESPONSE PATTERNS ────")
        lines.append(f"  Avg time/question: {time_data.get('average_seconds', 0)}s")
        lines.append(f"  First half accuracy: {fatigue.get('first_half_accuracy', 0)}%")
        lines.append(f"  Second half accuracy: {fatigue.get('second_half_accuracy', 0)}%")
        if fatigue.get('fatigue_detected'):
            lines.append("  ⚠ Fatigue detected — performance dropped in later questions")
        lines.append("")

        # Recommendations
        lines.append("──── RECOMMENDATIONS ────")
        for rec in (report.recommendations or []):
            lines.append(f"  • {rec.get('message', '')}")
            if rec.get('action'):
                lines.append(f"    → {rec['action']}")
        lines.append("")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "Keep learning!",
            "The Velocity Learning Team",
        ])

        return "\n".join(lines)

    @staticmethod
    def _send_plain_text_fallback(user, test_result, report):
        """Fallback if HTML template rendering fails"""
        plain_body = EmailService._build_plain_text(user, report)
        subject = f"Test Report — {test_result.total_score:.1f}%"

        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        mailgun_key = os.getenv('MAILGUN_API_KEY')

        if sendgrid_key:
            return EmailService._send_via_sendgrid(user.email, subject, plain_body, plain_body)
        elif mailgun_key:
            return EmailService._send_via_mailgun(user.email, subject, plain_body, plain_body)
        else:
            print(f"\n{'=' * 70}")
            print(f"📧 EMAIL TO: {user.email}")
            print(f"SUBJECT: {subject}")
            print(f"{'=' * 70}")
            print(plain_body)
            print(f"{'=' * 70}\n")
            return {'success': True, 'method': 'console'}

    # =====================================================================
    # LEGACY: Basic test result email (kept for backward compatibility)
    # =====================================================================

    @staticmethod
    def send_test_results(user, test_result):
        """
        Legacy method — sends basic text email.
        New code should use send_test_report() with a TestReport.
        """
        from .report_generator import ReportGenerator
        try:
            report = ReportGenerator.generate_report(test_result.id)
            return EmailService.send_test_report(user, test_result, report)
        except Exception as e:
            print(f"[EmailService] Report generation failed, sending basic email: {e}")
            return EmailService._send_basic_email(user, test_result)

    @staticmethod
    def _send_basic_email(user, test_result):
        """Bare-bones email when report generation fails"""
        subject = f"Test Results — {test_result.total_score:.1f}%"
        body = (
            f"Hello {user.first_name or user.username},\n\n"
            f"Your test is complete. Score: {test_result.total_score:.1f}%\n"
            f"Questions: {test_result.correct_answers}/{test_result.total_questions}\n"
            f"Time: {test_result.time_taken_seconds // 60} min\n\n"
            f"Log in to view your detailed report.\n\n"
            f"— Velocity Learning Team"
        )

        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        if sendgrid_key:
            return EmailService._send_via_sendgrid(user.email, subject, body, body)

        print(f"\n📧 TO: {user.email}\nSUBJECT: {subject}\n{body}\n")
        return {'success': True, 'method': 'console'}

    @staticmethod
    def send_session_reminder(user, session):
        """Send reminder about pending test"""
        subject = "Reminder: Complete Your Test"
        body = (
            f"Hello {user.first_name or user.username},\n\n"
            f"You have a pending test from your study session \"{session.workspace_name}\".\n\n"
            f"Complete it now to get your detailed report!\n\n"
            f"— Velocity Learning Team"
        )

        return EmailService._dispatch_email(user.email, subject, body, body)
