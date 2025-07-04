# start_server.py
import os
import sys
from django.core.management import execute_from_command_line

# Add your project's root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_image_resizer.settings') # Replace 'your_project_name'
    execute_from_command_line(['manage.py', 'runserver', '--noreload']) # Use --noreload to prevent issues with PyInstaller