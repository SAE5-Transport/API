from apifairy import response, other_responses, arguments
from flask import Blueprint, jsonify
from flask_marshmallow import Marshmallow
from api.services.coord import obtenir_coordonnees_pieton


walk_bp = Blueprint("walk", __name__, url_prefix='/walk')

ma = Marshmallow(walk_bp)


class WalkCoordQuery(ma.Schema):
    origin = ma.String(
        required=True, description="Origin coordinates (lat,lng)")
    destination = ma.String(
        required=True, description="Destination coordinates (lat,lng)")


class Coordinate(ma.Schema):
    latitude = ma.Float()
    longitude = ma.Float()


class WalkCoordResponse(ma.Schema):
    coordinates = ma.List(ma.Nested(Coordinate))


@walk_bp.route('/walkcoord', strict_slashes=False, methods=['GET'])
@arguments(WalkCoordQuery)
@response(WalkCoordResponse, 200)
@other_responses({400: 'Bad request parameters', 500: 'Internal server error'})
def get_walk_coordinates(args):
    """
    Get detailed walking coordinates between two points.
    """
    try:
        origin = args["origin"]
        destination = args["destination"]
        api_key = "AIzaSyBOV-iFF7J6IHW4sUlHhXpm5jQ9Q4oGsu0"

        decoded_coordinates = obtenir_coordonnees_pieton(
            origin, destination, api_key)

        coords_list = [{"latitude": lat, "longitude": lng}
                       for lat, lng in decoded_coordinates]

        return {"coordinates": coords_list}, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
