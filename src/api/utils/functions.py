from geopy.distance import great_circle

def checkDistanceBetweenPoints(lat1, lon1, lat2, lon2, distance_max):
    """
    Check if the distance between two points is less than a maximum distance
    :param lat1: latitude of the first point
    :param lon1: longitude of the first point
    :param lat2: latitude of the second point
    :param lon2: longitude of the second point
    :param distance_max: maximum distance
    :return: True if the distance is less than the maximum distance, False otherwise
    """
    distance = great_circle((lat1, lon1), (lat2, lon2)).km
    return distance <= distance_max