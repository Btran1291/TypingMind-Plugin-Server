import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from flask_cors import CORS

project_home = '.'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from brave_search import app as brave_search_app
from vectorize_query import app as vectorize_rag_app

CORS(brave_search_app, resources={r"/*": {"origins": "*"}})
CORS(vectorize_rag_app, resources={r"/*": {"origins": "*"}})

application = DispatcherMiddleware(Response('Not Found', status=404), {
    '/brave_search': brave_search_app,
    '/vectorize-rag-retrieve': vectorize_rag_app
})
