import requests
import polyline


def obtenir_coordonnees_pieton(depart, arrivee, api_key, waypoints=None):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": depart,
        "destination": arrivee,
        "mode": "walking",
        "alternatives": "true",
        "key": api_key
    }

    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    response = requests.get(url, params=params)
    resultat = response.json()

    if resultat["status"] != "OK":
        raise Exception(
            f"Erreur API : {resultat['status']} - {resultat.get('error_message')}")

    # choisir la meilleure route (première ou selon tes critères)
    route = resultat["routes"][0]

    coordonnees_precises = []

    for leg in route["legs"]:
        for step in leg["steps"]:
            points = polyline.decode(step["polyline"]["points"])
            coordonnees_precises.extend(points)

    return coordonnees_precises
