import requests
from datetime import datetime
from api.utils.functions import checkDistanceBetweenPoints
import pytz

def getStations(name):
    url = "http://otp.clarifygdps.com/otp/routers/default/index/graphql"

    # Prepare the request
    payload = {
        "query": "query getStations($name: String) { stations(name: $name) { name, lat, lon, gtfsId, stops { gtfsId, routes { gtfsId, longName, shortName, color, textColor, mode } } } }",
        "variables": {
            "name": name
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("POST", url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Check if the data is present
        if 'data' in response.json():
            data = response.json()['data']['stations']

            finalData = []

            modes = []

            # Get all the lines based on the lines passing through the stops
            linesDataSet = {}
            for station in data:
                for stop in station["stops"]:
                    for route in stop["routes"]:
                        if route["gtfsId"] not in linesDataSet:
                            linesDataSet[route["gtfsId"]] = route

            for line in linesDataSet.values():
                modes.append(line["mode"])

            # Order the stations
            orders = {
                'SUBWAY': 0,
                'RAIL': 1,
                'TRAM': 2,
                'FERRY': 3,
                'CABLE_CAR': 4,
                'BUS': 5,
            }

            # Get highest mode for each station
            for station in data:
                station_modes = [orders[line["mode"]] for stop in station["stops"] for line in stop["routes"] if "mode" in line and line["mode"] in orders]
                if station_modes:
                    station["mode"] = min(station_modes)
                else:
                    station["mode"] = max(orders.values()) + 1  # Assign a default mode if none found

            # Sort stations by mode
            data.sort(key=lambda x: x["mode"])

            # Group stations by their name
            for station in data:
                found = False
                for x in finalData:
                    if x["name"] == station["name"] and checkDistanceBetweenPoints(x["lat"], x["lon"], station["lat"], station["lon"], 1):
                        x["stops"] += station["stops"]
                        found = True
                        break

                if not found:
                    finalData.append(station)


            return finalData
        
    return {"error": "No data found"}

def getPaths(departure_lat, departure_lon, arrival_lat, arrival_lon, date: datetime, arrival=False, numTrips=5):
    url = "http://otp.clarifygdps.com/otp/routers/default/index/graphql"

    # Determine the current timezone offset (Europe/Paris)
    paris_tz = pytz.timezone("Europe/Paris")
    current_offset = datetime.now(paris_tz).utcoffset()
    offset_hours = int(current_offset.total_seconds() / 3600)
    offset_sign = "+" if offset_hours >= 0 else "-"
    offset_formatted = f"{offset_sign}{abs(offset_hours):02}:00"

    # Prepare the request
    payload = {
        "query": "query planConnection($origin: PlanLabeledLocationInput!, $destination: PlanLabeledLocationInput!, $dateTime: PlanDateTimeInput, $first: Int) {  planConnection(origin: $origin, destination: $destination, dateTime: $dateTime, first: $first) {    edges {      node {        duration        start        end        legs {          mode          duration          start {            scheduledTime            estimated {              time              delay            }          }          end {            scheduledTime            estimated {              time              delay            }          }          realTime          realtimeState          route {            color            textColor            gtfsId            mode            shortName            longName          }          legGeometry {            points          }          from {            arrival {              scheduledTime              estimated {                time                delay              }            }            departure{              scheduledTime              estimated {                time                delay              }            }            lat            lon            name            stop {              gtfsId            }          }          to {            arrival {              scheduledTime              estimated {                time                delay              }            }            departure{              scheduledTime              estimated {                time                delay              }            }            lat            lon            name            stop {              gtfsId            }          }          intermediateStops {            name            gtfsId            lat            lon          }          fareProducts {            product {              id              name            }          }        }      }    }  }}",
        "variables": {
            "origin": {
                "location": {
                    "coordinate": {
                        "latitude": departure_lat,
                        "longitude": departure_lon
                    }
                }
            },
            "destination": {
                "location": {
                    "coordinate": {
                        "latitude": arrival_lat,
                        "longitude": arrival_lon
                    }
                }
            },
            "dateTime": {
                "latestArrival" if arrival else "earliestDeparture": date.isoformat() + offset_formatted
            },
            "first": numTrips
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("POST", url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        if 'data' in response.json():
            return response.json()["data"]
    
    return {"error": "No data found"}

def getIncidentsFromLines(lines):
    url = "http://otp.clarifygdps.com/otp/transmodel/v3"

    # Prepare the request
    payload = {
        "query": "query line($ids: [ID]) {  lines(ids: $ids) {    id    publicCode    name    presentation {      colour      textColour    }    situations {      id      severity      summary {        value      }      description {        value      }      validityPeriod {        startTime        endTime      }      affects {        ... on AffectedLine {          line {            id            publicCode            name            presentation {              colour              textColour            }          }        }        ... on AffectedStopPlace {          quay {            name            id            latitude            longitude          }          stopPlace {            name            id            latitude            longitude          }        }      }    }  }}",
        "variables": {
            "ids": lines
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("POST", url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        if 'data' in response.json():
            return response.json()["data"]
    
    return {"error": "No data found"}

def getNextDeparturesByStation(id, startTime, numOfDepartures, numberOfDeparturesPerLineDestinationDisplay, includeCancelled):
    url = "http://otp.clarifygdps.com/otp/transmodel/v3"

    # Prepare the request
    payload = {
        "query": "query prochainPassageByStation($id: String!, $startTime: DateTime, $numOfDepartures: Int, $includeCancelled: Boolean, $numberOfDeparturesPerLineAndDestinationDisplay: Int) {  quay(id: $id) {    name    estimatedCalls(startTime: $startTime, numberOfDeparturesPerLineAndDestinationDisplay: $numberOfDeparturesPerLineAndDestinationDisplay, includeCancelledTrips: $includeCancelled, numberOfDepartures: $numOfDepartures) {      aimedDepartureTime      expectedDepartureTime      realtime      serviceJourney {        line {          name        }        journeyPattern {          name        }        passingTimes {          quay {            name            id          }        }      }    }  }}",
        "variables": {
            "id": id,
            "startTime": startTime.isoformat(),
            "numOfDepartures": numOfDepartures,
            "numberOfDeparturesPerLineDestinationDisplay": numberOfDeparturesPerLineDestinationDisplay,
            "includeCancelled": includeCancelled
        }
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("POST", url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        if 'data' in response.json():
            return response.json()["data"]
    
    return {"error": "No data found"}

def getTickets():
    url = "http://otp.clarifygdps.com/otp/routers/default/index/graphql"

    # Prepare the request
    payload = {
        "query": "query tickets {  ticketTypes {    currency    fareId    price    zones  }}"
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the request
    response = requests.request("POST", url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        if 'data' in response.json():
            return response.json()["data"]
        
    return {"error": "No data found"}