'''
    ENDPOINTS
'''
from flask import Blueprint
from .search import search_bp
from ...services.postgres import health as pghealth
from ...services.mongo import health as mongohealth

v1_bp = Blueprint("v1", __name__, url_prefix='/v1')
v1_bp.register_blueprint(search_bp)

@v1_bp.route('/health', strict_slashes=False, methods=['GET'])
def healthcheck():
    '''
        Check if all services health
    '''
    main_data = {
        "postegresql": pghealth(),
        "mongodb": mongohealth()
    }
    return main_data
