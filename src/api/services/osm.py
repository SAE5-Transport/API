import requests

def getAdresses(name):
    url = f"https://photon.komoot.io/api/?q={name}&limit=5"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        streets = []

        for feature in data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [0, 0])
            
            if properties.get('type') in ['district', 'street', 'house', 'city', 'locality']:
                streets.append({
                    "name": properties.get('name', ''),
                    "subname": f"{properties.get('city', '')}, {properties.get('state', '')}",
                    "lat": coordinates[1],
                    "lon": coordinates[0],
                    "type": properties.get('type', ''),
                })

        return streets
        
    return {}

def getAdressesByCoordinates(lat, lon):
    url = f"https://photon.komoot.io/reverse?lat={lat}&lon={lon}"


    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        streets = [{
            "name": data['features'][0]["properties"]["name"],
            "subname": f"{data['features'][0]['properties'].get('city', '')}, {data['features'][0]['properties'].get('state', '')}",
            "lat": data['features'][0]["geometry"]["coordinates"][1],
            "lon": data['features'][0]["geometry"]["coordinates"][0],
            "type": data['features'][0]["properties"]["type"],
        }]
        return streets
        
    else:
        print(f"Erreur {response.status_code}: {response.text}")
    return {}