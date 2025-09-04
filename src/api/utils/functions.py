from haversine import haversine, Unit

def checkDistanceBetweenPoints(lat1, lon1, lat2, lon2, distance_max):
    distance = haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)
    return distance <= distance_max