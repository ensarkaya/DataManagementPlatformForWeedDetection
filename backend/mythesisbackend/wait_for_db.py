import os
import sys
import django
from django.core.management import call_command
from io import StringIO
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mythesisbackend.settings")
django.setup()

def check_migrations():
    output = StringIO()
    call_command('showmigrations', format='plan', stdout=output)
    output.seek(0)
    content = output.read()
    # Look for migrations that aren't applied
    return '[ ]' not in content

def wait_for_migrations(timeout=300, check_interval=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_migrations():
            print("All migrations have been applied.")
            return True
        else:
            print("Waiting for migrations to be applied...")
            time.sleep(check_interval)
    print("Timeout waiting for migrations to be applied.")
    return False

if __name__ == "__main__":
    if not wait_for_migrations():
        sys.exit(1)