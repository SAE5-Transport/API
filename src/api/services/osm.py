import requests

def getAdresses(name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={name}"

    response = requests.get(url, headers={
        'User-Agent': 'MonAppFlutter/1.0 (monemail@example.com)',
        'Content-Type': 'application/json'
    })
    
    if response.status_code == 200:
        data = response.json()
        
        streets = []

        for feature in data:
            if feature['addresstype'] in ['town', 'village', 'road', 'bus_stop']:
                streets.append({
                    "name": feature['display_name'].split(", ")[0],
                    "subname": ", ".join(feature['display_name'].split(", ")[1:]),
                    "lat": feature['lat'],
                    "lon": feature['lon'],
                    "type": feature['addresstype'],
                })

        return streets
        
    return {}

def getAdressesByCoordinates(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"

    response = requests.get(url, headers={
        'User-Agent': 'MonAppFlutter/1.0 (monemail@example.com)',
        'Content-Type': 'application/json'
    })

    if response.status_code == 200:
        data = response.json()
        
        streets = []

        for feature in data:
            if feature['addresstype'] in ['town', 'village', 'road', 'bus_stop']:
                streets.append({
                    "name": feature['display_name'].split(", ")[0],
                    "subname": ", ".join(feature['display_name'].split(", ")[1:]),
                    "lat": feature['lat'],
                    "lon": feature['lon'],
                    "type": feature['addresstype'],
                })

        return streets
        
    return {}