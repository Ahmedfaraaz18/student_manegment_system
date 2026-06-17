import os
import sys
import shutil

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'c:/Users/ahmed/OneDrive/Desktop/student_management_system')

import django
django.setup()

# Delete migrations folders
migrations_dirs = [
    'accounts/migrations',
    'students/migrations',
    'teachers/migrations',
    'subjects/migrations',
    'results/migrations',
    'attendance/migrations',
    'institutions/migrations',
    'departments/migrations',
    'dashboard/migrations',
]

base = 'c:/Users/ahmed/OneDrive/Desktop/student_management_system'

for d in migrations_dirs:
    path = os.path.join(base, d)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted {d}")

# Recreate migrations folders with __init__.py
for d in migrations_dirs:
    path = os.path.join(base, d)
    os.makedirs(path, exist_ok=True)

    init_file = os.path.join(path, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('')

    print(f"Created {d}/__init__.py")

# Run makemigrations
from django.core.management import call_command
call_command('makemigrations')

# Run migrate
call_command('migrate')

print("\nMigration completed successfully!")