from flask import Flask
from brave_search import brave_search_bp
from vectorize_query import vectorize_query_bp

app = Flask(__name__)

# Register the brave_search app blueprint
app.register_blueprint(brave_search_bp, url_prefix='/')

# Register the vectorize_query app blueprint
app.register_blueprint(vectorize_query_bp, url_prefix='/')
