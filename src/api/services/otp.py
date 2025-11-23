import requests
from datetime import datetime
from api.utils.functions import checkDistanceBetweenPoints
import pytz
from google.transit import gtfs_realtime_pb2

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
                                "routeId": nextDeparture.get("routeId"),
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
    """
    Fetch GTFS-RT alerts (protobuf format) and filter by requested lines.
    
    Args:
        lines: List of line/route IDs to filter alerts for
    
    Returns:
        List of formatted alerts matching the requested lines
    """
    try:
        # GTFS-RT alerts endpoint - adjust URL to your GTFS-RT provider
        url = "http://gtfsidfm.clarifygdps.com/gtfs-rt-alerts-idfm"
        
        # Send the request to get protobuf data
        response = requests.get(url, timeout=10)
        
        # Check if the request was successful
        if response.status_code != 200:
            return {"error": "Failed to fetch alerts"}
        
        # Parse the protobuf response
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        # Parse GTFS-RT alerts and filter by lines
        formatted_alerts = []
        
        # Group alerts by base ID (without timestamp suffix)
        alert_groups = {}
        
        for entity in feed.entity:
            # Check if entity has alert
            if not entity.HasField('alert'):
                continue
            
            alert = entity.alert
            
            # Check if alert affects any of the requested lines
            matching_lines = []
            
            for informed_entity in alert.informed_entity:
                if informed_entity.HasField('route_id'):
                    route_id = informed_entity.route_id
                    if route_id in lines:
                        matching_lines.append(route_id)
            
            # Skip if alert doesn't affect requested lines
            if not matching_lines:
                continue
            
            # Extract base alert ID (remove timestamp suffix if present)
            # Format: "disruption_id:start_time:end_time"
            alert_id = entity.id if entity.id else f"alert-{len(formatted_alerts)}"
            base_id = alert_id.split(':')[0] if ':' in alert_id else alert_id
            
            # Group by base ID to merge multiple time periods
            if base_id not in alert_groups:
                alert_groups[base_id] = {
                    'alert': alert,
                    'entity_id': alert_id,
                    'matching_lines': set(matching_lines)
                }
            else:
                # Merge matching lines
                alert_groups[base_id]['matching_lines'].update(matching_lines)
        
        # Process grouped alerts
        for base_id, alert_data in alert_groups.items():
            alert = alert_data['alert']
            alert_id = alert_data['entity_id']
            matching_lines = alert_data['matching_lines']
            
            # Get severity level from effect
            severity_effect_enum = alert.effect if alert.HasField('effect') else gtfs_realtime_pb2.Alert.UNKNOWN_EFFECT
            
            # Map GTFS-RT Effect to severity string
            effect_to_severity = {
                gtfs_realtime_pb2.Alert.NO_SERVICE: "severe",
                gtfs_realtime_pb2.Alert.REDUCED_SERVICE: "severe",
                gtfs_realtime_pb2.Alert.SIGNIFICANT_DELAYS: "severe",
                gtfs_realtime_pb2.Alert.DETOUR: "normal",
                gtfs_realtime_pb2.Alert.ADDITIONAL_SERVICE: "normal",
                gtfs_realtime_pb2.Alert.MODIFIED_SERVICE: "normal",
                gtfs_realtime_pb2.Alert.OTHER_EFFECT: "normal",
                gtfs_realtime_pb2.Alert.UNKNOWN_EFFECT: "unknown",
                gtfs_realtime_pb2.Alert.STOP_MOVED: "normal"
            }
            severity = effect_to_severity.get(severity_effect_enum, "unknown")
            
            # Use severity_level if available for more precise mapping
            if alert.HasField('severity_level'):
                severity_level_enum = alert.severity_level
                if severity_level_enum == gtfs_realtime_pb2.Alert.SEVERE:
                    severity = "severe"
                elif severity_level_enum == gtfs_realtime_pb2.Alert.WARNING:
                    severity = "normal"
            
            # Extract header text (summary)
            summary_value = "Alerte"
            if alert.HasField('header_text'):
                for translation in alert.header_text.translation:
                    if translation.text:
                        summary_value = translation.text
                        break
            
            # Extract description text
            description_value = ""
            if alert.HasField('description_text'):
                for translation in alert.description_text.translation:
                    if translation.text:
                        desc_text = translation.text
                        # Wrap in HTML paragraph if not already HTML
                        if desc_text and not desc_text.strip().startswith("<"):
                            description_value = f"<p>{desc_text}</p>"
                        else:
                            description_value = desc_text
                        break
            
            # Extract validity period (use first active period)
            validity_period = {}
            if len(alert.active_period) > 0:
                first_period = alert.active_period[0]
                if first_period.HasField('start'):
                    validity_period["startTime"] = datetime.fromtimestamp(
                        first_period.start, pytz.UTC
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                if first_period.HasField('end'):
                    validity_period["endTime"] = datetime.fromtimestamp(
                        first_period.end, pytz.UTC
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Build situations list from informed entities (only for matching lines)
            situations = []
            for informed_entity in alert.informed_entity:
                situation = {}
                
                if informed_entity.HasField('route_id'):
                    route_id = informed_entity.route_id
                    # Only include if it's one of the matching lines
                    if route_id in matching_lines:
                        situation["routeId"] = route_id
                
                if informed_entity.HasField('stop_id'):
                    situation["stopId"] = informed_entity.stop_id
                
                if informed_entity.HasField('trip'):
                    situation["tripId"] = informed_entity.trip.trip_id
                
                if situation:
                    situations.append(situation)
            
            # Create an alert for each matching line
            for line_id in matching_lines:
                # Try to get line name and color from your data
                # You can fetch this from the nextDepartures data or from a separate API
                line_name = line_id
                line_color = "#000000"  # Default color
                
                # Format the alert
                formatted_alert = {
                    "id": f"{alert_id}-{line_id}",
                    "severity": severity,
                    "summary": [
                        {
                            "value": summary_value
                        }
                    ],
                    "description": [
                        {
                            "value": description_value
                        }
                    ],
                    "validityPeriod": validity_period,
                    "situations": [s for s in situations if s.get("routeId") == line_id or "routeId" not in s],
                    "name": line_name,
                    "presentation": {
                        "colour": line_color
                    }
                }
                
                formatted_alerts.append(formatted_alert)
        
        return formatted_alerts if formatted_alerts else {"error": "No alerts found for specified lines"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Error processing alerts: {str(e)}"}

def getNextDeparturesByStation(id, startTime, numOfDepartures, includeCancelled):
    # If startTime is a datetime object, format it; otherwise use as-is
    if isinstance(startTime, datetime):
        formatted_date = startTime.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        formatted_date = startTime
    
    url = f"http://motis.clarifygdps.com/api/v5/stoptimes?stopId={id}&time={formatted_date}&arriveBy=false&n={numOfDepartures}&exactRadius=false&radius=200&language=fr&withScheduledSkippedStops={includeCancelled}"
    
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if len(response.json()["stopTimes"]) > 0:
            return response.json()["stopTimes"]
    
    return {"error": "No data found"}