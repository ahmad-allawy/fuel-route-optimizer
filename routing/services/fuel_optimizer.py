from geopy.distance import geodesic
from ..models import FuelStation


class FuelOptimizer:

    MAX_RANGE = 500  # miles
    MPG = 10

    @staticmethod
    def calculate_stops(route_points, total_distance):
        """
        route_points: list of (lat, lon)
        total_distance: miles
        """

        stops = []
        distance_accumulated = 0
        last_stop_index = 0

        for i in range(1, len(route_points)):
            segment_distance = geodesic(
                route_points[i - 1],
                route_points[i]
            ).miles

            distance_accumulated += segment_distance

            if distance_accumulated >= FuelOptimizer.MAX_RANGE:
                current_point = route_points[i]

                station = FuelOptimizer.find_best_station_near_route(
                    route_points[last_stop_index:i]
                )

                if station:
                    stops.append(station)

                distance_accumulated = 0
                last_stop_index = i

        return stops


   


    @staticmethod
    def find_best_station_near_route(route_segment, max_distance=20):
        """
        Find cheapest station within max_distance (miles) of any point in route_segment
        """

        lats = [p[0] for p in route_segment]
        lons = [p[1] for p in route_segment]

        lat_min, lat_max = min(lats) - 0.5, max(lats) + 0.5
        lon_min, lon_max = min(lons) - 0.5, max(lons) + 0.5

        candidates = FuelStation.objects.filter(
            latitude__range=(lat_min, lat_max),
            longitude__range=(lon_min, lon_max)
        )

        best_station = None
        best_price = float('inf')

        for station in candidates:
            for point in route_segment:
                dist = geodesic((station.latitude, station.longitude), point).miles
                if dist <= max_distance and station.retail_price < best_price:
                    best_price = station.retail_price
                    best_station = station
                    break

        return best_station


def calculate_total_cost(stops, start_point, end_point):
    """
    حساب التكلفة بشكل دقيق بين كل نقطتين (start → stop1 → stop2 → ... → end)
    """

    points = [start_point] + [(stop.latitude, stop.longitude) for stop in stops] + [end_point]

    total_cost = 0
    MPG = 10

    for i in range(len(points) - 1):
        segment_distance = geodesic(points[i], points[i + 1]).miles
        gallons = segment_distance / MPG

        if i == 0 and stops:
            price_per_gallon = stops[0].retail_price
        elif i-1 < len(stops) and i-1 >= 0:
            price_per_gallon = stops[i-1].retail_price
        else:
            price_per_gallon = 0

        total_cost += gallons * price_per_gallon

    return round(total_cost, 2)

