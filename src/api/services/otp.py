import requests

def getStations(name):
    url = "http://otp.clarifygdps.com/otp/routers/default/index/graphql"

    payload = {
        "query": "query getStations($name: String) { stations(name: $name) { name, lat, lon, gtfsId, stops { gtfsId, routes { gtfsId, longName, shortName, color, textColor, mode } } } }",
        "variables": {
            "name": name
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    if response.status_code == 200:
        if 'data' in response.json():
            data = response.json()['data']['stations']

            modes = []

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
                station["mode"] = min([orders[line["mode"]] for stop in station["stops"] for line in stop["routes"]])

            # Sort stations by mode
            data.sort(key=lambda x: x["mode"])

            return data
        
    return {"error": "No data found"}