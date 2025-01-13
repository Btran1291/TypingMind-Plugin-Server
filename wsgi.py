import sys

# add your project directory to the sys.path
project_home = '.'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import the brave_search app
from brave_search import app as brave_search_app

# For WSGI to work, we need an 'application' variable
application = brave_search_app
