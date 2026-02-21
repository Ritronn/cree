#!/usr/bin/env python
"""
Run all 40 property-based tests for Study Session Monitoring and Testing System

Usage:
    python run_property_tests.py
    python run_property_tests.py --verbose
    python run_property_tests.py --property 1  # Run specific property
"""
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning.settings')
django.setup()

import pytest


def main():
    """Run property-based tests"""
    args = [
        'adaptive_learning/tests/test_properties.py',
        'adaptive_learning/tests/test_properties_advanced.py',
        '-v',
        '--tb=short',
        '-m', 'django_db'
    ]
    
    # Add any command line arguments
    if len(sys.argv) > 1:
        if '--verbose' in sys.argv:
            args.append('-vv')
        if '--property' in sys.argv:
            prop_num = sys.argv[sys.argv.index('--property') + 1]
            args.append(f'-k property_{prop_num}')
    
    print("=" * 80)
    print("Running 40 Property-Based Tests")
    print("Feature: study-session-monitoring-testing")
    print("=" * 80)
    print()
    
    # Run tests
    exit_code = pytest.main(args)
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ All property tests passed!")
    else:
        print("❌ Some property tests failed. See output above.")
    print("=" * 80)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
