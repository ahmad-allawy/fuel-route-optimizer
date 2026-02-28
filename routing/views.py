from rest_framework.views import APIView
from rest_framework.response import Response
from routing.services.fuel_optimizer import FuelOptimizer, calculate_total_cost
from routing.services.routing_service import RouteService
from django.core.cache import cache
import hashlib
import json

class RouteFuelAPIView(APIView):

    def post(self, request):

        cache_key = hashlib.md5(
            json.dumps(request.data, sort_keys=True).encode()
        ).hexdigest()

        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        start = request.data.get("start")
        end = request.data.get("end")

        initial_route = RouteService.get_route(
            (start["lat"], start["lng"]),
            (end["lat"], end["lng"])
        )

        stops = FuelOptimizer.calculate_stops(
            initial_route["decoded_geometry"],
            initial_route["distance_miles"]
        )

        points = [(start["lat"], start["lng"])] + \
                 [(stop.latitude, stop.longitude) for stop in stops] + \
                 [(end["lat"], end["lng"])]


        final_route = RouteService.get_route_multi(points)

        total_cost = calculate_total_cost(
            final_route["distance_miles"],
            stops
        )

        response_data = {
            "distance_miles": final_route["distance_miles"],
            "duration_minutes": final_route["duration_minutes"],
            "fuel_stops": [
                {
                    "name": s.truckstop_name,
                    "city": s.city,
                    "state": s.state,
                    "price": s.retail_price,
                    "lat": s.latitude,
                    "lon": s.longitude
                }
                for s in stops
            ],
            "total_fuel_cost": total_cost,
            "route_geometry": final_route["geometry"]
        }

        cache.set(cache_key, response_data, timeout=60 * 60)  # Cache for 1 hour
        return Response(response_data)
