import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_pos.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
