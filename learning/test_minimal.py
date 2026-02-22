import os
import sys
import django

print("Step 1: Starting...")
sys.stdout.flush()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
print("Step 2: Django settings set")
sys.stdout.flush()

django.setup()
print("Step 3: Django setup complete")
sys.stdout.flush()

from django.contrib.auth.models import User
print("Step 4: Imported User model")
sys.stdout.flush()

user, created = User.objects.get_or_create(username='test_minimal')
print(f"Step 5: User created/retrieved: {user.username}")
sys.stdout.flush()

print("✅ Test complete!")
