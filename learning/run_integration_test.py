#!/usr/bin/env python
"""
Integration Test Runner
Runs the complete workflow test with proper output
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')

# Setup Django
import django
django.setup()

# Now run the test
from test_complete_workflow import test_complete_workflow

if __name__ == '__main__':
    print("Starting integration test...")
    print("=" * 80)
    try:
        result = test_complete_workflow()
        print("\n" + "=" * 80)
        if result:
            print("✅ INTEGRATION TEST PASSED")
            sys.exit(0)
        else:
            print("❌ INTEGRATION TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
