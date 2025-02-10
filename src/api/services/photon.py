import requests

def getAdresses(name, limit=5):
    url = f"https://photon.komoot.io/api/?q={name}"

    response = requests.get(url)
    
    if response.status_code == 200:
        if 'features' in response.json().keys():
            data = response.json()['features']
            
            streets = []

            for feature in data:
                geometry_street = feature['geometry']
                property_street = feature['properties']

                if property_street['type'] in ['city', 'district', 'street']:
                    streets.append({
                        "name": property_street['name'],
                        "lat": geometry_street['coordinates'][1],
                        "lon": geometry_street['coordinates'][0],
                        "city": property_street['city'] if 'city' in property_street else None,
                        "type": property_street['type'],
                        "postcode": property_street['postcode'] if 'postcode' in property_street else None,
                    })

            return streets[0:limit]
        
    return {}
