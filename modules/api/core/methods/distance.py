import math

from core.general.schemes.restaurant import Location


def get_distance(first_point: Location, second_point: Location) -> int:
    first_point_latitude, first_point_longitude = math.radians(first_point.latitude), math.radians(first_point.longitude)
    second_point_latitude, second_point_longitude = math.radians(second_point.latitude), math.radians(second_point.longitude)

    sin_lat1, cos_lat1 = math.sin(first_point_latitude), math.cos(first_point_latitude)
    sin_lat2, cos_lat2 = math.sin(second_point_latitude), math.cos(second_point_latitude)

    delta_lng = second_point_longitude - first_point_longitude
    cos_delta_lng, sin_delta_lng = math.cos(delta_lng), math.sin(delta_lng)

    distance = math.atan2(
        math.sqrt((cos_lat2 * sin_delta_lng) ** 2 + (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta_lng) ** 2),
        sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta_lng
    )

    return round(6371.009 * distance * 1000)
