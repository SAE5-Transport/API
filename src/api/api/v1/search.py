from flask import Blueprint, Response, json
from flask_marshmallow import Marshmallow
import zstandard as zstd
from datetime import datetime
from apifairy import response, other_responses, arguments
from api.services.otp import getStations, getPaths, getIncidentsFromLines, getTickets, getNextDeparturesByStation
from api.services.osm import getAdresses, getAdressesByCoordinates

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
def findLocation(data: dict):
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

class FindLocationByCoordinatesQuery(ma.Schema):
    lat: float = ma.Float(required=True, description="Latitude")
    lon: float = ma.Float(required=True, description="Longitude")

class FindLocationByCoordinatesResponse(ma.Schema):
    osm: list = ma.List(ma.Dict, description="OSM locations")

@search_bp.route('/findLocationByCoordinates', strict_slashes=False, methods=['GET'])
@arguments(FindLocationByCoordinatesQuery)
@response(FindLocationByCoordinatesResponse)
@other_responses({400: 'No coordinates provided'})
def findLocationByCoordinates(data: dict):
    """
    Endpoint to find location by coordinates, returns OSM locations.
    """

    lat = data.get('lat')
    lon = data.get('lon')

    # Check if the lat and lon are present
    if lat and lon:
        main_data = {
            "osm": []
        }

        # Get the adresses from OSM
        osm = getAdressesByCoordinates(lat, lon)
        main_data['osm'] = osm

        return main_data
    
    return {"error": "No coordinates provided"}, 400

class SearchPathsQuery(ma.Schema):
    departure_lat: float = ma.Float(required=True, description="Departure Latitude")
    departure_lon: float = ma.Float(required=True, description="Departure Longitude")
    arrival_lat: float = ma.Float(required=True, description="Arrival Latitude")
    arrival_lon: float = ma.Float(required=True, description="Arrival Longitude")
    start: datetime = ma.DateTime(description="Departure time or arrival time (if set)", load_default=datetime.today())
    arrival: bool = ma.Boolean(description="If true, the start time is the arrival time", load_default=False)
    numTrips: int = ma.Integer(description="Number of trips to return", load_default=5)

@search_bp.route('/searchPaths', strict_slashes=False, methods=['GET'])
@arguments(SearchPathsQuery)
#@response(SearchPathsResponse) TODO DOCUMENTATION
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
    
class IncidentsOnLineQuery(ma.Schema):
    lineId: str = ma.String(required=True, description="Line ID")

class IncidentValueString(ma.Schema):
    value = ma.String(description="Value of the type")

class IncidentValidityPeriod(ma.Schema):
    startTime = ma.String(description="Start time of the incident")
    endTime = ma.String(description="End time of the incident")

class AffectedLinePresentation(ma.Schema):
    colour = ma.String(description="Line color")
    textColour = ma.String(description="Text color")

class AffectedLine(ma.Schema):
    id = ma.String(description="Line ID")
    publicCode = ma.String(description="Public code")
    name = ma.String(description="Line name")
    presentation = ma.Nested(AffectedLinePresentation, description="Line presentation")

class AffectedStopPlace(ma.Schema):
    name = ma.String(description="Stop place name")
    id = ma.String(description="Stop place ID")
    latitude = ma.Float(description="Latitude")
    longitude = ma.Float(description="Longitude")

class AffectedQuay(ma.Schema):
    name = ma.String(description="Quay name")
    id = ma.String(description="Quay ID")
    latitude = ma.Float(description="Latitude")
    longitude = ma.Float(description="Longitude")

class Affected(ma.Schema):
    line = ma.Nested(AffectedLine, description="Line information")
    stopPlace = ma.Nested(AffectedStopPlace, description="Stop place information")
    quay = ma.Nested(AffectedQuay, description="Quay information")

class Incident(ma.Schema):
    id = ma.String(description="Incident ID")
    severity = ma.String(description="Incident severity")
    summary = ma.List(ma.Nested(IncidentValueString), description="Incident summary")
    description = ma.List(ma.Nested(IncidentValueString), description="Incident description")
    validityPeriod = ma.Nested(IncidentValidityPeriod, description="Incident validity period")
    affects = ma.List(ma.Nested(Affected), description="Affected locations")

class LineOnIncident(ma.Schema):
    id = ma.String(description="Line ID")
    publicCode = ma.String(description="Public code")
    name = ma.String(description="Line name")
    presentation = ma.Nested(AffectedLinePresentation, description="Line presentation")
    situations = ma.List(ma.Nested(Incident), description="Incidents")

class IncidentsOnLineResponse(ma.Schema):
    line: str = ma.Nested(LineOnIncident, description="Line information")

@search_bp.route('/incidentsOnLine', strict_slashes=False, methods=['GET'])
@arguments(IncidentsOnLineQuery)
@response(IncidentsOnLineResponse)
@other_responses({404: 'No data found', 400: 'Missing required parameters'})
def incidentsOnLine(data):
    """
    Endpoint to get incidents on a line.
    """

    # Check if the required parameters are present
    if data.get('lineId'):
        # Get the incidents
        incidents = getIncidentsFromLines(data['lineId'])

        if "error" in incidents:
            return incidents, 404
        
        return incidents
    else:
        return {"error": "Missing required parameters"}, 400

class IncidentsOnLinesQuery(ma.Schema):
    lineIds: list = ma.List(ma.String, required=True, description="List of line IDs")
    zstd: bool = ma.Boolean(description="If true, the response will be compressed with Zstandard", load_default=False)

@search_bp.route('/incidentsOnLines', strict_slashes=False, methods=['GET'])
@arguments(IncidentsOnLinesQuery)
@other_responses({404: 'No data found', 400: 'Missing required parameters'})
def incidentsOnLines(data):
    """
    Endpoint to get incidents on multiple lines.
    """

    # Check if the required parameters are present
    if data.get('lineIds'):
        # Get the incidents
        incidents = getIncidentsFromLines(data['lineIds'])

        if "error" in incidents:
            return incidents, 404
        
        # Check if zstd is requested
        if data.get('zstd'):
            # Compress the response with Zstandard
            cctx = zstd.ZstdCompressor()
            incidents = cctx.compress(json.dumps(incidents).encode('utf-8'))

            return Response(incidents, mimetype='application/zstd')
        else:
            return incidents
    else:
        return {"error": "Missing required parameters"}, 400
    
class nextDepartureByStationQuery(ma.Schema):
    id: str = ma.String(required=True, description="Station ID")
    startTime: datetime = ma.DateTime(description="Start time for the next departure", load_default=datetime.now())
    numOfDepartures: int = ma.Integer(description="Number of departures to return", load_default=5)
    numberOfDeparturesPerLineAndDestinationDisplay: int = ma.Integer(description="Number of departures per line and destination display", load_default=1)
    includeCancelled: bool = ma.Boolean(description="If true, include cancelled departures", load_default=False)

@search_bp.route('/nextDepartureByStation', strict_slashes=False, methods=['GET'])
@arguments(nextDepartureByStationQuery)
@other_responses({404: 'No data found', 400: 'Missing required parameters'})
def nextDepartureByStation(data):
    """
    Endpoint to get the next departures from a station.
    """

    # Check if the required parameters are present
    if data.get('id'):
        # Get the next departures
        departures = getNextDeparturesByStation(
            data['id'],
            data['startTime'],
            data['numOfDepartures'],
            data['numberOfDeparturesPerLineAndDestinationDisplay'],
            data['includeCancelled']
        )

        if "error" in departures:
            return departures, 404
        
        return departures
    else:
        return {"error": "Missing required parameters"}, 400

@search_bp.route('/tickets', strict_slashes=False, methods=['GET'])
@other_responses({404: 'No data found'})
def tickets():
    """
    Endpoint to get ticket information.
    """

    tickets = getTickets()

    if "error" in tickets:
        return tickets, 404

    return tickets