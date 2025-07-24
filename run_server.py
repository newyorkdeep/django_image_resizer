import os
import sys
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_image_resizer.settings') # Replace 'your_project_name'
    try:
        execute_from_command_line(sys.argv + ['runserver', '--noreload']) # --noreload is crucial for PyInstaller
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc