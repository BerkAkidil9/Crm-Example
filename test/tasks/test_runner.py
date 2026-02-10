"""
Tasks Test Runner
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()


def run_tasks_tests():
    """Run all tasks tests"""
    print("Starting Tasks Tests...")
    print("=" * 60)
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    test_modules = [
        'test.tasks.working_tests.test_models',
        'test.tasks.working_tests.test_forms',
        'test.tasks.working_tests.test_views',
    ]
    failures = test_runner.run_tests(test_modules, verbosity=2)
    if failures:
        print(f"\n{failures} tests failed!")
        return False
    else:
        print("\nAll tests passed!")
        return True


if __name__ == "__main__":
    run_tasks_tests()
