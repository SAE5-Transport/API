from flask import Blueprint, request
from api.services.otp import getStations
from api.services.photon import getAdresses

search_bp = Blueprint("search_bp", __name__, url_prefix='/search')

@search_bp.route('/findLocation', strict_slashes=False, methods=['GET'])
def findLocation():
    if 'name' in request.args:
        name = request.args['name']

        main_data = {
            "otp": [],
            "photon": []
        }
        limit = 5

        otp = getStations(name, limit)
        if 'error' in otp:
            return otp, 404
        
        main_data['otp'] = otp

        if len(otp) < limit:
            limit = limit - len(otp)
            
            photon = getAdresses(name, limit)
            main_data['photon'] = photon

        return main_data, 200
    
    return {"error": "No name provided"}, 400