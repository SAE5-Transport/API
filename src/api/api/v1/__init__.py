'''
    ENDPOINTS
'''
from flask import Blueprint
from .test import test_bp

v1_bp = Blueprint("v1_bp", __name__, url_prefix='/v1')
v1_bp.register_blueprint(test_bp)
