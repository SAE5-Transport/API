import requests
from datetime import datetime
from api.utils.functions import checkDistanceBetweenPoints

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
    url = "http://otp.clarifygdps.com/otp/transmodel/v3"

    # Prepare the request
    payload = {
        "query": "query trip($accessEgressPenalty: [PenaltyForStreetMode!], $alightSlackDefault: Int, $alightSlackList: [TransportModeSlack], $arriveBy: Boolean, $banned: InputBanned, $bicycleOptimisationMethod: BicycleOptimisationMethod, $bikeSpeed: Float, $boardSlackDefault: Int, $boardSlackList: [TransportModeSlack], $bookingTime: DateTime, $dateTime: DateTime, $filters: [TripFilterInput!], $from: Location!, $ignoreRealtimeUpdates: Boolean, $includePlannedCancellations: Boolean, $includeRealtimeCancellations: Boolean, $itineraryFilters: ItineraryFilters, $locale: Locale, $maxAccessEgressDurationForMode: [StreetModeDurationInput!], $maxDirectDurationForMode: [StreetModeDurationInput!], $maximumAdditionalTransfers: Int, $maximumTransfers: Int, $modes: Modes, $numTripPatterns: Int, $pageCursor: String, $relaxTransitGroupPriority: RelaxCostInput, $searchWindow: Int, $timetableView: Boolean, $to: Location!, $transferPenalty: Int, $transferSlack: Int, $triangleFactors: TriangleFactors, $useBikeRentalAvailabilityInformation: Boolean, $via: [TripViaLocationInput!], $waitReluctance: Float, $walkReluctance: Float, $walkSpeed: Float, $wheelchairAccessible: Boolean, $whiteListed: InputWhiteListed) {  trip(    accessEgressPenalty: $accessEgressPenalty    alightSlackDefault: $alightSlackDefault    alightSlackList: $alightSlackList    arriveBy: $arriveBy    banned: $banned    bicycleOptimisationMethod: $bicycleOptimisationMethod    bikeSpeed: $bikeSpeed    boardSlackDefault: $boardSlackDefault    boardSlackList: $boardSlackList    bookingTime: $bookingTime    dateTime: $dateTime    filters: $filters    from: $from    ignoreRealtimeUpdates: $ignoreRealtimeUpdates    includePlannedCancellations: $includePlannedCancellations    includeRealtimeCancellations: $includeRealtimeCancellations    itineraryFilters: $itineraryFilters    locale: $locale    maxAccessEgressDurationForMode: $maxAccessEgressDurationForMode    maxDirectDurationForMode: $maxDirectDurationForMode    maximumAdditionalTransfers: $maximumAdditionalTransfers    maximumTransfers: $maximumTransfers    modes: $modes    numTripPatterns: $numTripPatterns    pageCursor: $pageCursor    relaxTransitGroupPriority: $relaxTransitGroupPriority    searchWindow: $searchWindow    timetableView: $timetableView    to: $to    transferPenalty: $transferPenalty    transferSlack: $transferSlack    triangleFactors: $triangleFactors    useBikeRentalAvailabilityInformation: $useBikeRentalAvailabilityInformation    via: $via    waitReluctance: $waitReluctance    walkReluctance: $walkReluctance    walkSpeed: $walkSpeed    wheelchairAccessible: $wheelchairAccessible    whiteListed: $whiteListed  ) {    previousPageCursor    nextPageCursor    tripPatterns {      aimedStartTime      aimedEndTime      expectedEndTime      expectedStartTime      duration      distance      legs {        id        mode        aimedStartTime        aimedEndTime        expectedEndTime        expectedStartTime        realtime        distance        duration        fromPlace {          name          quay {            id          }        }        toPlace {          name          quay {            id          }        }        toEstimatedCall {          destinationDisplay {            frontText          }        }        line {          publicCode          name          id          transportMode          presentation {            colour            textColour          }        }        authority {          name          id        }        pointsOnLink {          points        }        interchangeTo {          staySeated        }        interchangeFrom {          staySeated        }        intermediateEstimatedCalls {          quay {            name          }          aimedDepartureTime          expectedDepartureTime          realtime          cancellation        }      }      systemNotices {        tag      }    }  }}",
        "variables": {
            "from": {
                "coordinates": {
                    "latitude": departure_lat,
                    "longitude": departure_lon
                }
            },
            "to": {
                "coordinates": {
                    "latitude": arrival_lat,
                    "longitude": arrival_lon
                }
            },
            "dateTime": date.isoformat(),
            "numTripPatterns": numTrips,
            "arriveBy": arrival
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