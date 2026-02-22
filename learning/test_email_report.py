"""
Quick test script for the email report system.
Run: python manage.py shell < test_email_report.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')

from adaptive_learning.email_service import EmailService

# Test Gmail SMTP connection
gmail_email = os.getenv('GMAIL_EMAIL')
gmail_pass = os.getenv('GMAIL_APP_PASSWORD')

print("=" * 60)
print("EMAIL CONFIGURATION CHECK")
print("=" * 60)
print(f"  GMAIL_EMAIL:        {'✅ ' + gmail_email if gmail_email else '❌ Not set'}")
print(f"  GMAIL_APP_PASSWORD: {'✅ Set (' + str(len(gmail_pass)) + ' chars)' if gmail_pass else '❌ Not set'}")
print(f"  RESEND_API_KEY:     {'✅ Set' if os.getenv('RESEND_API_KEY') else '⬜ Not set'}")
print(f"  SENDGRID_API_KEY:   {'✅ Set' if os.getenv('SENDGRID_API_KEY') else '⬜ Not set'}")
print()

if not gmail_email:
    print("❌ No email provider configured. Add GMAIL_EMAIL and GMAIL_APP_PASSWORD to .env")
    exit()

# Send a test email to yourself
print(f"📧 Sending test email to: {gmail_email}")
print()

test_html = """
<html><body style="font-family:Arial;padding:20px;">
<div style="background:linear-gradient(135deg,#0f4c75,#00b4d8);padding:30px;border-radius:12px;color:white;text-align:center;">
    <h1 style="margin:0;">✅ Email Works!</h1>
    <p style="margin:10px 0 0;">Your Velocity Learning report emails are configured correctly.</p>
</div>
<div style="padding:20px;background:#f8fafc;border-radius:12px;margin-top:16px;">
    <h3>What happens next?</h3>
    <p>When you complete a test, you'll receive a rich AMCAT-style report with:</p>
    <ul>
        <li>📊 Score summary with color-coded sections</li>
        <li>🧠 Behavioral analysis (thinking style, cognitive profile)</li>
        <li>⏱ Response pattern analysis (fatigue, guessing detection)</li>
        <li>💡 Personalized recommendations</li>
    </ul>
</div>
</body></html>
"""

test_plain = "✅ Email works! Your Velocity Learning report emails are configured correctly."

result = EmailService._dispatch_email(
    to_email=gmail_email,
    subject="✅ Velocity Learning — Email Test Successful!",
    html_body=test_html,
    plain_body=test_plain,
)

print()
if result.get('success'):
    print(f"✅ SUCCESS! Email sent via: {result.get('method')}")
    print(f"   Check your inbox at: {gmail_email}")
else:
    print(f"❌ FAILED: {result.get('error')}")
    print(f"   Method tried: {result.get('method')}")
    if 'gmail' in result.get('method', ''):
        print()
        print("   Common fixes:")
        print("   1. Make sure 2-Step Verification is ON in Google Account")
        print("   2. Generate an App Password at: https://myaccount.google.com/apppasswords")
        print("   3. Use the 16-character app password, NOT your Gmail password")
        print("   4. Remove spaces from the app password in .env")

print()
