import sys
# add your project directory to the sys.path
project_home = '.'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
from main_app import app as application
