import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

# Add your project directory to the sys.path
project_home = '.'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import the brave_search app
from brave_search import app as brave_search_app

# Import the vectorize_rag app
from vectorize_query import app as vectorize_rag_app

# Create a dispatcher middleware to route requests
application = DispatcherMiddleware(Response('Not Found', status=404), {
    '/brave_search': brave_search_app,
    '/vectorize-rag-retrieve': vectorize_rag_app
})
