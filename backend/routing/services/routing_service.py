import requests
import polyline
from django.conf import settings


#  the limitaion of the ORS API is that the total route distance must not exceed 6000 km (6000000 meters).
# {
#     "error": {
#         "code": 2004,
#         "message": "Request parameters exceed the server configuration limits. The approximated route distance must not be greater than 6000000.0 meters."
#     },
#     "info": {
#         "engine": {
#             "build_date": "2025-10-31T12:33:09Z",
#             "graph_version": "3",
#             "graph_date": "2026-02-08T11:35:31Z",
#             "osm_date": "2026-02-02T00:59:59Z",
#             "version": "9.5.0"
#         },
#         "timestamp": 1771386166978
#     }
# }

class RouteService:

    BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

    @staticmethod
    def get_route(start, end):
        
        headers = {
            "Authorization": settings.ORS_API_KEY,
            "Content-Type": "application/json"
        }

        body = {
            "coordinates": [
                [start[1], start[0]],  # [lon, lat]
                [end[1], end[0]]
            ]
        }

        response = requests.post(RouteService.BASE_URL, json=body, headers=headers)

        if response.status_code != 200:
            raise Exception("Failed to fetch route")

        data = response.json()
        route = data["routes"][0]

        return {
            "distance_miles": route["summary"]["distance"] / 1609.34,
            "duration_minutes": route["summary"]["duration"] / 60,
            "geometry": route["geometry"],
            "decoded_geometry": polyline.decode(route["geometry"])
        }

    @staticmethod
    def get_route_multi(points):
        """
        points: list of (lat, lon)
        ترجع مسار يمر عبر كل النقاط بالترتيب
        """
        headers = {
            "Authorization": settings.ORS_API_KEY,
            "Content-Type": "application/json"
        }

        coords = [[p[1], p[0]] for p in points] 

        body = {
            "coordinates": coords
        }

        response = requests.post(RouteService.BASE_URL, json=body, headers=headers)
        print("ORS API response:", response.status_code)

        if response.status_code != 200:
            raise Exception("Failed to fetch route")

        data = response.json()
        route = data["routes"][0]

        return {
            "distance_miles": route["summary"]["distance"] / 1609.34,
            "duration_minutes": route["summary"]["duration"] / 60,
            "geometry": route["geometry"],
            "decoded_geometry": polyline.decode(route["geometry"])
        }
