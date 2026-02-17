import csv
from django.core.management.base import BaseCommand
from routing.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel stations from CSV"

    def handle(self, *args, **kwargs):
        file_path = "assets/fuel_prices_with_latlon.csv"

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            stations = []
            for row in reader:
                stations.append(
                    FuelStation(
                        opis_id=row["opis_id"],
                        truckstop_name=row["truckstop_name"],
                        address=row["Address"],
                        city=row["City"],
                        state=row["State"],
                        rack_id=row["rack_id"],
                        retail_price=row["retail_price"],
                        price_per_mile=row["price_per_mile"],
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                    )
                )

            FuelStation.objects.bulk_create(stations, batch_size=500)

        self.stdout.write(self.style.SUCCESS("Stations imported successfully!"))
