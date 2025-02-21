from flask import Blueprint
from flask_marshmallow import Marshmallow
from datetime import datetime
from apifairy import response, other_responses, arguments
from api.services.otp import getStations, getPaths
from api.services.osm import getAdresses

search_bp = Blueprint("search", __name__, url_prefix='/search')
ma = Marshmallow(search_bp)

class FindLocationQuery(ma.Schema):
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

class FindLocationResponse(ma.Schema):
    otp: list = ma.List(ma.Nested(OTPStation), description="OTP locations")
    osm: list = ma.List(ma.Dict, description="OSM locations")

@search_bp.route('/findLocation', strict_slashes=False, methods=['GET'])
@arguments(FindLocationQuery)
@response(FindLocationResponse)
@other_responses({404: 'No data found', 400: 'No name provided'})
def findLocation(data: str):
    """
    Endpoint to find location by name, returns OTP and OSM locations.
    """

    name = data.get('name')

    # Check if the name is present
    if name:
        main_data = {
            "otp": [],
            "osm": []
        }

        # Get the stations from OTP
        otp = getStations(name)
        if 'error' in otp:
            return otp, 404
        
        main_data['otp'] = otp

        # Get the adresses from OSM
        osm = getAdresses(name)
        main_data['osm'] = osm

        return main_data
    
    return {"error": "No name provided"}, 400

class SearchPathsQuery(ma.Schema):
    departure_lat: float = ma.Float(required=True, description="Departure Latitude")
    departure_lon: float = ma.Float(required=True, description="Departure Longitude")
    arrival_lat: float = ma.Float(required=True, description="Arrival Latitude")
    arrival_lon: float = ma.Float(required=True, description="Arrival Longitude")
    start: datetime = ma.DateTime(description="Departure time or arrival time (if set)", load_default=datetime.today())
    arrival: bool = ma.Boolean(description="If true, the start time is the arrival time", load_default=False)
    numTrips: int = ma.Integer(description="Number of trips to return", load_default=5)

class Authority(ma.Schema):
    id = ma.String(description="Authority ID")
    name = ma.String(description="Authority name")

class DestinationDisplay(ma.Schema):
    frontText = ma.String(description="Final destination text display")

class Quay(ma.Schema):
    id = ma.String(description="Quay ID")
    name = ma.String(description="Quay name")

class Place(ma.Schema):
    name = ma.String(description="Place name")
    quay = ma.Nested(Quay, allow_none=True, description="Quay information")

class LinePresentation(ma.Schema):
    colour = ma.String(description="Line color")
    textColour = ma.String(description="Text color")

class Line(ma.Schema):
    name = ma.String(description="Line name")
    publicCode = ma.String(description="Public code")
    transportMode = ma.String(description="Transport mode")
    presentation = ma.Nested(LinePresentation, description="Presentation details")

class IntermediateCall(ma.Schema):
    aimedDepartureTime = ma.DateTime(description="Scheduled departure time")
    expectedDepartureTime = ma.DateTime(description="Expected departure time")
    quay = ma.Nested(Quay, description="Quay information")
    cancellation = ma.Boolean(description="Indicates if the trip is cancelled")
    realtime = ma.Boolean(description="Indicates if the data is real-time")

class PointsOnLink(ma.Schema):
    points = ma.String(description="Encoded polyline points")

class Leg(ma.Schema):
    aimedStartTime = ma.DateTime(description="Scheduled start time")
    aimedEndTime = ma.DateTime(description="Scheduled end time")
    expectedStartTime = ma.DateTime(description="Expected start time")
    expectedEndTime = ma.DateTime(description="Expected end time")
    duration = ma.Integer(description="Duration in seconds")
    distance = ma.Float(description="Distance in meters")
    mode = ma.String(description="Transport mode")
    authority = ma.Nested(Authority, allow_none=True, description="Transport authority")
    fromPlace = ma.Nested(Place, description="Starting place")
    toPlace = ma.Nested(Place, description="Destination place")
    intermediateEstimatedCalls = ma.List(ma.Nested(IntermediateCall), description="Intermediate stops")
    line = ma.Nested(Line, allow_none=True, description="Line information")
    pointsOnLink = ma.Nested(PointsOnLink, description="Encoded path coordinates (look in https://developers.google.com/maps/documentation/utilities/polylineutility for decoding)")
    realtime = ma.Boolean(description="Indicates if the data is real-time")
    toEstimatedCall = ma.Nested(DestinationDisplay, allow_none=True, description="Destination display text")

class TripPattern(ma.Schema):
    aimedStartTime = ma.DateTime(description="Trip planned start time")
    aimedEndTime = ma.DateTime(description="Trip planned end time")
    expectedStartTime = ma.DateTime(description="Trip expected start time")
    expectedEndTime = ma.DateTime(description="Trip expected end time")
    duration = ma.Integer(description="Trip duration in seconds")
    distance = ma.Float(description="Total trip distance in meters")
    legs = ma.List(ma.Nested(Leg), description="Trip segments")

class SearchPathsResponse(ma.Schema):
    nextPageCursor = ma.String(description="Cursor for next page of results")
    previousPageCursor = ma.String(description="Cursor for previous page of results")
    tripPatterns = ma.List(ma.Nested(TripPattern), description="List of possible trip paths")

@search_bp.route('/searchPaths', strict_slashes=False, methods=['GET'])
@arguments(SearchPathsQuery)
@response(SearchPathsResponse)
@other_responses({404: 'No data found', 400: 'Missing required parameters'})
def searchPaths(data):
    """
    Endpoint to search for paths between two points.
    """

    # Check if the required parameters are present
    if data.get('departure_lat') and data.get('departure_lon') and data.get('arrival_lat') and data.get('arrival_lon'):
        # Get the paths
        paths = getPaths(data['departure_lat'], data['departure_lon'], data['arrival_lat'], data['arrival_lon'], data['start'], data['arrival'], data['numTrips'])

        if "error" in paths:
            return paths, 404
        
        return paths
    else:
        return {"error": "Missing required parameters"}, 400