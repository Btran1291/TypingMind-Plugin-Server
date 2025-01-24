from flask import Flask
from brave_search import brave_search_bp
from vectorize_query import vectorize_query_bp
from generate_docx import generate_docx_bp

app = Flask(__name__)

app.register_blueprint(brave_search_bp, url_prefix='/')
app.register_blueprint(vectorize_query_bp, url_prefix='/')
app.register_blueprint(generate_docx_bp, url_prefix='/')
