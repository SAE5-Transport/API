'''
    ENDPOINTS
'''
from apifairy import response, other_responses, arguments
from flask import Blueprint
from flask_marshmallow import Marshmallow
from .search import search_bp
from .friend import friend_bp
from .user import user_bp
from .trajet import trajet_bp
from .company import company_bp
from .agent import agent_bp
from ...services.postgres import health as pghealth
from ...services.mongo import health as mongohealth

v1_bp = Blueprint("v1", __name__, url_prefix='/v1')
v1_bp.register_blueprint(search_bp)
v1_bp.register_blueprint(friend_bp)
v1_bp.register_blueprint(user_bp)
v1_bp.register_blueprint(company_bp)
v1_bp.register_blueprint(agent_bp)
v1_bp.register_blueprint(trajet_bp)

ma = Marshmallow(search_bp)


class HealthResponse(ma.Schema):
    postegresql = ma.Boolean(description="Connection to postgresql is ok?")
    mongodb = ma.Boolean(description="Connection to mongodb is ok?")


@v1_bp.route('/health', strict_slashes=False, methods=['GET'])
@response(HealthResponse)
def healthcheck():
    '''
        Check if all services are connected
    '''
    main_data = {
        "postegresql": pghealth(),
        "mongodb": mongohealth()
    }
    return main_data
