import requests
from datetime import datetime, timedelta
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
                            # Change name to place name
                            place = nextDeparture.get("place")
                            if place:
                                if place.get("parentId") == station.get("id"):
                                    # Extract agencyId from the "source" field if present and matches pattern
                                    agency_id = None
                                    source = nextDeparture.get("source")
                                    if source and "gtfs/" in source:
                                        agency_id = source.split("gtfs/")[-1].split(".zip")[0]
                                    linesDataSet[nextDeparture["routeId"]] = {
                                        "mode": nextDeparture.get("mode", "OTHER"),
                                        "color": nextDeparture.get("routeColor", "#000000"),
                                        "textColor": nextDeparture.get("routeTextColor", "#FFFFFF"),
                                        "shortName": nextDeparture.get("displayName", ""),
                                        "longName": nextDeparture.get("routeLongName", ""),
                                        "routeId": nextDeparture.get("routeId"),
                                        "agencyId": agency_id
                                    }
                                    # Add route to station's routes
                                    station["routes"].append(linesDataSet[nextDeparture["routeId"]])
                                    
                                    # Update station name and parentId
                                    station["name"] = place.get("name", "---")
                                    station['parentId'] = place.get("parentId", None)

            # Order the stations
            # GTFS route type ordering provided by user (higher value = higher priority)
            gtfs_route_type_order = {
                "HIGHSPEED_RAIL": 28,
                "LONG_DISTANCE": 27,
                "NIGHT_RAIL": 26,
                "RAIL": 25,
                "REGIONAL_FAST_RAIL": 24,
                "REGIONAL_RAIL": 23,
                "SUBURBAN": 22,
                "METRO": 21,
                "SUBWAY": 20,
                "TRAM": 19,
                "COACH": 18,
                "BUS": 17,
                "AIRPLANE": 16,
                "FERRY": 15,
                "AERIAL_LIFT": 14,
                "AREAL_LIFT": 13,
                "FUNICULAR": 12,
                "CABLE_CAR": 11,
                "ODM": 10,
                "RIDE_SHARING": 9,
                "CAR_DROPOFF": 8,
                "CAR_PARKING": 7,
                "CAR": 6,
                "RENTAL": 5,
                "BIKE": 4,
                "WALK": 3,
                "TRANSIT": 2,
                "FLEX": 1,
                "OTHER": 0,
            }

            # Our sorting expects lower numbers = higher priority, so invert the map
            max_val = max(gtfs_route_type_order.values()) if gtfs_route_type_order else 0
            orders = {k: (max_val - v) for k, v in gtfs_route_type_order.items()}

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
                
                # Consider both route-level modes and station-level `modes` list (may be empty)
                route_modes = [orders[line["mode"]] for line in station.get("routes", []) if "mode" in line and line["mode"] in orders]
                station_modes_field = [orders[m] for m in station.get("modes", []) if m in orders]
                combined_modes = route_modes + station_modes_field
                if combined_modes:
                    station["mode"] = min(combined_modes)
                else:
                    station["mode"] = max(orders.values()) + 1  # Assign a default mode if none found

            # Sort stations by mode (priority), then exact-name-match to query, then by station name
            query_lower = (name or "").strip().lower()
            def station_sort_key(s):
                mode_key = s.get("mode", max(orders.values()) + 1)
                # exact match priority: 0 for exact match, 1 otherwise
                exact_match = 0 if (s.get("name") or "").strip().lower() == query_lower else 1
                name_key = (s.get("name") or "").lower()
                return (mode_key, exact_match, name_key)

            data.sort(key=station_sort_key)

            # Group stations by their name and proximity
            for station in data:
                found = False
                for x in finalData:
                    # Check if same name and within 1km radius
                    if x.get("id") == station.get("parentId") and station.get("parentId") is not None:
                        # Merge routes from duplicate stations, avoiding duplicates by routeId
                        existing_route_ids = {route.get("routeId") for route in x.get("routes", []) if "routeId" in route}
                        
                        for route in station.get("routes", []):
                            route_id = route.get("routeId")
                            # Only add if routeId is not already present
                            if route_id and route_id not in existing_route_ids:
                                x.setdefault("routes", []).append(route)
                                existing_route_ids.add(route_id)
                        
                        # Re-sort routes after merging by mode priority, then by short name
                        x["routes"] = sorted(
                            x.get("routes", []), 
                            key=lambda route: (
                                orders.get(route.get("mode", "OTHER"), max(orders.values()) + 1),
                                route.get("shortName", "").lower()
                            )
                        )
                        # Recompute the station mode after merging routes so ordering remains correct
                        # Recompute the station mode after merging routes so ordering remains correct
                        x_route_modes = [orders[line["mode"]] for line in x.get("routes", []) if "mode" in line and line["mode"] in orders]
                        x_station_modes_field = [orders[m] for m in x.get("modes", []) if m in orders]
                        x_combined = x_route_modes + x_station_modes_field
                        if x_combined:
                            x["mode"] = min(x_combined)
                        else:
                            x["mode"] = max(orders.values()) + 1
                        found = True
                        break
                if not found:
                    finalData.append(station)


            # Ensure final grouped list is also sorted by mode, exact match to query, then name
            finalData.sort(key=station_sort_key)

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

def getIncidentsFromLines(lines, gtfsRtUrl="http://gtfsidfm.clarifygdps.com/gtfs-rt-alerts-idfm"):
    """
    Fetch GTFS-RT alerts (protobuf format) and filter by requested lines.
    
    Args:
        lines: List of line/route IDs to filter alerts for
    
    Returns:
        List of lines with their associated alerts grouped by line ID
        Format: [{"id": "IDFM:C01730", "name": "IDFM:C01730", "situations": [...]}, ...]
    """
    try:
        # Send the request to get protobuf data
        response = requests.get(gtfsRtUrl, timeout=10)
        
        # Check if the request was successful
        if response.status_code != 200:
            return {"error": "Failed to fetch alerts"}
        
        # Parse the protobuf response
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
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
            # Some alert ids use ':' for namespace (e.g. 'RTA:3135-6-0073')
            # while others append timestamps like 'disruption_id:start:end'.
            # We should only strip trailing numeric timestamp suffixes (one or two)
            # and otherwise keep the full id to avoid grouping unrelated alerts.
            alert_id = entity.id if entity.id else f"alert-{len(alert_groups)}"
            tokens = alert_id.split(':')
            # If the id ends with two numeric tokens (start and end timestamps),
            # remove those to get the base disruption id. Otherwise keep the id.
            if len(tokens) >= 3 and tokens[-1].isdigit() and tokens[-2].isdigit():
                base_id = ':'.join(tokens[:-2])
            else:
                base_id = alert_id
            
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
        
        # Group alerts by line ID
        lines_with_alerts = {}
        
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
            situations_data = []
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
                    situations_data.append(situation)
            
            # Create alert structure for each matching line
            for line_id in matching_lines:
                # Initialize line entry if not exists
                if line_id not in lines_with_alerts:
                    lines_with_alerts[line_id] = {
                        "id": line_id,
                        "name": line_id,
                        "presentation": {
                            "colour": "#000000"  # Default color, can be enriched later
                        },
                        "situations": []
                    }
                
                # Format the alert situation
                situation = {
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
                    "routeId": line_id
                }
                
                # Add the situation to the line's situations list
                lines_with_alerts[line_id]["situations"].append(situation)
        
        # Convert dictionary to list
        result = list(lines_with_alerts.values())
        
        return result if result else {"error": "No alerts found for specified lines"}
    
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

def getTrip(tripId, withScheduledSkippedStops, joinInterlinedLegs):
    url = f"http://motis.clarifygdps.com/api/v5/trip?tripId={tripId}&withScheduledSkippedStops={withScheduledSkippedStops}&joinInterlinedLegs={joinInterlinedLegs}"

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if len(response.json()) > 0:
            return response.json()
    
    return {"error": "No data found"}

def getTripsOnMap(zoomLevel, minLat, minLon, maxLat, maxLon, startTimeInterval=datetime.now(), endTimeInterval=datetime.now() + timedelta(hours=1)):
    # Format the dates to ISO 8601 format with Z suffix
    formatted_start = startTimeInterval.strftime("%Y-%m-%dT%H:%M:%SZ")
    formatted_end = endTimeInterval.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = f"http://motis.clarifygdps.com/api/v5/map/trips?min={minLat},+{minLon}&max={maxLat},+{maxLon}&zoom={zoomLevel}&startTime={formatted_start}&endTime={formatted_end}"

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("GET", url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        if len(response.json()) > 0:
            return response.json()
    
    return {"error": "No data found"}