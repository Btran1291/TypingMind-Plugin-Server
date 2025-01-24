import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from flask import make_response

# Add your project directory to the sys.path
project_home = '.'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from brave_search import app as brave_search_app

from vectorize_query import app as vectorize_rag_app

def cors_middleware(app):
    def middleware(environ, start_response):
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response(environ, start_response)
        return app(environ, start_response)
    return middleware

application = DispatcherMiddleware(Response('Not Found', status=404), {
    '/brave_search': cors_middleware(brave_search_app),
    '/vectorize-rag-retrieve': cors_middleware(vectorize_rag_app)
})
