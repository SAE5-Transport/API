import requests
from datetime import datetime
from api.utils.functions import checkDistanceBetweenPoints
import pytz

def getStations(name):
    url = f"http://motis.clarifygdps.com/api/v1/geocode?text={name}&language=fr&type=STOP"
    
    print(url)

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
            
            # Get all the lines based on the lines passing through the stops
            linesDataSet = {}
            
            # Fetch next departures for each station and enrich station data
            for station in data:
                # Initialize routes list for this station if not present
                if "routes" not in station:
                    station["routes"] = []
                
                # Get next departures for this station
                nextDeparturesData = getNextDeparturesByStation(
                    station["id"], 
                    datetime.now(pytz.timezone('Europe/Paris')).astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), 
                    255, 
                    True
                )
                
                # Process departures if valid response
                if isinstance(nextDeparturesData, list):
                    for nextDeparture in nextDeparturesData:
                        if nextDeparture.get("routeId") and nextDeparture["routeId"] not in linesDataSet:
                            linesDataSet[nextDeparture["routeId"]] = {
                                "mode": nextDeparture.get("mode", "OTHER"),
                                "color": nextDeparture.get("routeColor", "#000000"),
                                "textColor": nextDeparture.get("routeTextColor", "#FFFFFF"),
                                "shortName": nextDeparture.get("routeShortName", ""),
                                "longName": nextDeparture.get("routeLongName", ""),
                            }
                            # Add route to station's routes
                            station["routes"].append(linesDataSet[nextDeparture["routeId"]])
                            
                            # Change name to place name
                            place = nextDeparture.get("place")
                            if place:
                                station["name"] = place.get("name", "---")

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

            # Get highest mode for each station and sort routes
            for station in data:
                # Sort routes by mode priority, then by short name
                station["routes"] = sorted(
                    station.get("routes", []), 
                    key=lambda route: (
                        orders.get(route.get("mode", "OTHER"), max(orders.values()) + 1),
                        route.get("shortName", "").lower()
                    )
                )
                
                station_modes = [orders[line["mode"]] for line in station.get("routes", []) if "mode" in line and line["mode"] in orders]
                if station_modes:
                    station["mode"] = min(station_modes)
                else:
                    station["mode"] = max(orders.values()) + 1  # Assign a default mode if none found

            # Sort stations by mode
            data.sort(key=lambda x: x.get("mode", max(orders.values()) + 1))

            # Group stations by their name
            for station in data:
                found = False
                for x in finalData:
                    if x["name"] == station["name"] and checkDistanceBetweenPoints(x["lat"], x["lon"], station["lat"], station["lon"], 1):
                        # Merge routes from duplicate stations
                        for route in station.get("routes", []):
                            if route not in x.get("routes", []):
                                x.setdefault("routes", []).append(route)
                        # Re-sort routes after merging by mode priority, then by short name
                        x["routes"] = sorted(
                            x.get("routes", []), 
                            key=lambda route: (
                                orders.get(route.get("mode", "OTHER"), max(orders.values()) + 1),
                                route.get("shortName", "").lower()
                            )
                        )
                        found = True
                        break
                if not found:
                    finalData.append(station)


            return finalData
        
    return {"error": "No data found"}

def getPaths(departure_lat, departure_lon, arrival_lat, arrival_lon, date: datetime, arrival=False, numTrips=5):
    # Format the date to ISO 8601 format with Z suffix
    formatted_date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = f"http://motis.clarifygdps.com/api/v5/plan?time={formatted_date}&fromPlace={departure_lat},{departure_lon}&toPlace={arrival_lat},{arrival_lon}&withFares=true&fastestDirectFactor=1.5&joinInterlinedLegs=false&maxMatchingDistance=250&arriveBy={arrival}&numItineraries={numTrips}"

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
    # Format the date to ISO 8601 format with Z suffix
    formatted_date = startTime.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = f"http://motis.clarifygdps.com/api/v5/stoptimes?stopId={id}&time={formatted_date}&arriveBy=false&n={numOfDepartures}&exactRadius=false&radius=200&language=fr&withScheduledSkippedStops={includeCancelled}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print(url)

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if len(response.json()["stopTimes"]) > 0:
            return response.json()["stopTimes"]
    
    return {"error": "No data found"}