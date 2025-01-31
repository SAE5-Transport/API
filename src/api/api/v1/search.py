from flask import Blueprint
from flask_marshmallow import Marshmallow
from apifairy import response, other_responses, arguments
from api.services.otp import getStations
from api.services.photon import getAdresses

search_bp = Blueprint("search", __name__, url_prefix='/search')
ma = Marshmallow(search_bp)

class LocationQuery(ma.Schema):
    name: str = ma.String(required=True, description="Location name")

class Line(ma.Schema):
    color: str = ma.String(description="Line color")
    textColor: str = ma.String(description="Text color")
    gtfsId: str = ma.String(description="Line ID from the GTFS")
    longName: str = ma.String(description="Line name (Long)")
    shortName: str = ma.String(description="Line name (Short)")
    mode: str = ma.String(description="Line transport mode")

class Stops(ma.Schema):
    gtfsId: str = ma.String(description="Stop ID from the GTFS")
    routes: list = ma.List(ma.Nested(Line), description="Lines passing through the stop")

class OTPStation(ma.Schema):
    gtfsId: str = ma.String(description="Station ID from the GTFS")
    lat: float = ma.Float(description="Latitude")
    lon: float = ma.Float(description="Longitude")
    name: str = ma.String(description="Station name")
    stops: list = ma.List(ma.Nested(Stops), description="Child stops")

class LocationResponse(ma.Schema):
    otp: list = ma.List(ma.Nested(OTPStation), description="OTP locations")
    photon: list = ma.List(ma.Dict, description="Photon locations")

@search_bp.route('/findLocation', strict_slashes=False, methods=['GET'])
@arguments(LocationQuery)
@response(LocationResponse)
@other_responses({404: 'No data found', 400: 'No name provided'})
def findLocation(data: str):
    """
    Endpoint to find location by name, returns OTP and Photon locations.
    """

    name = data.get('name')

    if name:
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

        return main_data
    
    return {"error": "No name provided"}, 400