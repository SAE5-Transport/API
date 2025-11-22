import requests
from datetime import datetime
from api.utils.functions import checkDistanceBetweenPoints
import pytz

def getStations(name):
    url = f"http://motis.clarifygdps.com/api/v1/geocode?text={name}&language=fr&type=STOP"

    # Prepare the request
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Check if the data is present
        if len(response.json()) > 0:
            data = response.json()

            finalData = []

            modes = []
            
            nextDeparturesData = getNextDeparturesByStation(data["id"], datetime.now(pytz.timezone('Europe/Paris')).astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), 255, True)

            # Get all the lines based on the lines passing through the stops
            linesDataSet = {}
            for nextDeparture in nextDeparturesData:
                if nextDeparture["routeId"] not in linesDataSet:
                    linesDataSet[nextDeparture["routeId"]] = {
                        "mode": nextDeparture["mode"],
                        "color": nextDeparture["routeColor"],
                        "textColor": nextDeparture["routeTextColor"],
                        "shortName": nextDeparture["routeShortName"],
                        "longName": nextDeparture["routeLongName"],
                    }

            for line in linesDataSet.values():
                modes.append(line["mode"])

            # Order the stations
            orders = {
                "WALK": 0,
                "BIKE": 1,
                "RENTAL": 2,
                "CAR": 3,
                "CAR_PARKING": 4,
                "CAR_DROPOFF": 5,
                "ODM": 6,
                "RIDE_SHARING": 7,
                "FLEX": 8,
                "TRANSIT": 9,
                "TRAM": 10,
                "SUBWAY": 11,
                "FERRY": 12,
                "AIRPLANE": 13,
                "SUBURBAN": 14,
                "BUS": 15,
                "COACH": 16,
                "RAIL": 17,
                "HIGHSPEED_RAIL": 18,
                "LONG_DISTANCE": 19,
                "NIGHT_RAIL": 20,
                "REGIONAL_FAST_RAIL": 21,
                "REGIONAL_RAIL": 22,
                "CABLE_CAR": 23,
                "FUNICULAR": 24,
                "AERIAL_LIFT": 25,
                "OTHER": 26,
                "AREAL_LIFT": 27,
                "METRO": 28,
            }

            # Build a priority map from stopId -> best mode (lowest order value) using nextDeparturesData
            stop_priority = {}
            if isinstance(nextDeparturesData, list):
                default_priority = max(orders.values()) + 1
                for nd in nextDeparturesData:
                    place = nd.get("place", {}) if isinstance(nd, dict) else {}
                    stop_id = place.get("stopId") or place.get("id") or nd.get("stopId")
                    mode = nd.get("mode")
                    if not stop_id or not mode:
                        continue
                    pr = orders.get(mode, default_priority)
                    prev = stop_priority.get(stop_id)
                    if prev is None or pr < prev:
                        stop_priority[stop_id] = pr

            # Assign a mode to each station using the stop_priority map (fallback to routes in stops if needed)
            default_priority = max(orders.values()) + 1
            for station in data:
                station_stop_ids = []
                for stop in station.get("stops", []):
                    sid = stop.get("stopId") or stop.get("id")
                    if sid:
                        station_stop_ids.append(sid)

                # collect priorities from nextDeparturesData
                station_modes = [stop_priority[sid] for sid in station_stop_ids if sid in stop_priority]

                # fallback: derive from stop.routes if no nextDepartures info found
                if not station_modes:
                    station_modes = [
                        orders[line["mode"]]
                        for stop in station.get("stops", [])
                        for line in stop.get("routes", [])
                        if "mode" in line and line["mode"] in orders
                    ]

                if station_modes:
                    station["mode"] = min(station_modes)
                else:
                    station["mode"] = default_priority

            # Sort stations by computed mode
            data.sort(key=lambda x: x.get("mode", default_priority))

            # Group stations by their name
            for station in data:
                found = False
                for x in finalData:
                    if x.get("name") == station.get("name") and checkDistanceBetweenPoints(x.get("lat"), x.get("lon"), station.get("lat"), station.get("lon"), 1):
                        # Merge modes if present
                        if "modes" in station:
                            if "modes" not in x:
                                x["modes"] = []
                            x["modes"] = list(set(x["modes"] + station["modes"]))
                        found = True
                        break

                if not found:
                    finalData.append(station)


            return finalData
        
    return {"error": "No data found"}

def getPaths(departure_lat, departure_lon, arrival_lat, arrival_lon, date: datetime, arrival=False, numTrips=5):
    url = f"http://motis.clarifygdps.com/api/v5/plan?time={date.isoformat()}&fromPlace={departure_lat},{departure_lon}&toPlace={arrival_lat},{arrival_lon}&withFares=true&fastestDirectFactor=1.5&joinInterlinedLegs=false&maxMatchingDistance=250&arriveBy={arrival}&numItineraries={numTrips}"

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if len(response.json()["itineraries"]) > 0:
            return response.json()["itineraries"]
    
    return {"error": "No data found"}

def getIncidentsFromLines(lines):
    # Send the request
    
    # TODO: Implement incident fetching logic using GTFS-RT Alerts
    
    return {"error": "No data found"}

def getNextDeparturesByStation(id, startTime, numOfDepartures, includeCancelled):
    url = f"http://motis.clarifygdps.com/api/v5/stoptimes?stopId={id}&time={startTime}&arriveBy=false&n={numOfDepartures}&exactRadius=false&radius=200&language=fr&withScheduledSkippedStops={includeCancelled}"
    
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if response.json()["stopTimes"] > 0:
            return response.json()["stopTimes"]
    
    return {"error": "No data found"}