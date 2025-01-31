'''
    ENDPOINTS
'''
from flask import Blueprint
from .search import search_bp

v1_bp = Blueprint("v1", __name__, url_prefix='/v1')
v1_bp.register_blueprint(search_bp)
