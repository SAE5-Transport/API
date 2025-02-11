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

            return data
        
    return {"error": "No data found"}