import pandas as pd
import time
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


input_csv = "assets/failed_geocoding_rows first.csv"
output_csv = "assets/fuel_prices_with_latlon.csv"
failed_csv = "assets/failed_geocoding_rows.csv"

df = pd.read_csv(input_csv)

if "latitude" not in df.columns:
    df["latitude"] = None
if "longitude" not in df.columns:
    df["longitude"] = None

failed_rows = []


geolocator = Nominatim(user_agent="fuel_route_optimizer_v1")
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    max_retries=2,
    error_wait_seconds=5
)


OPENCAGE_API_KEY = "d0bf848bdead4f7ca85bb1f53c48e393"

def geocode_opencage(query):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": query,
        "key": OPENCAGE_API_KEY,
        "limit": 1,
        "countrycode": "us"
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]
            return location["lat"], location["lng"]
    return None, None


batch_size = 100
total_rows = len(df)

for idx, row in df.iterrows():

    if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
        continue

    queries = [
        f"{row['truckstop_name']}, {row['City']}, {row['State']}, USA",
        f"{row['Address']}, {row['City']}, {row['State']}, USA"
    ]

    lat, lon = None, None

    for query in queries:

        try:
            location = geocode(query)
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"✅ {idx}/{total_rows} - Nominatim success")
                break
        except Exception as e:
            print(f"⚠️ Nominatim error: {e}")

        try:
            lat, lon = geocode_opencage(query)
            if lat and lon:
                print(f"✅ {idx}/{total_rows} - OpenCage success")
                break
        except Exception as e:
            print(f"⚠️ OpenCage error: {e}")

    if lat and lon:
        df.at[idx, "latitude"] = lat
        df.at[idx, "longitude"] = lon
    else:
        print(f"❌ {idx}/{total_rows} - Failed completely")
        failed_rows.append(row)

    time.sleep(1)

    if idx % batch_size == 0 and idx != 0:
        df.to_csv(output_csv, index=False)
        print(f"💾 Intermediate save at row {idx}")

df.to_csv(output_csv, index=False)

if failed_rows:
    pd.DataFrame(failed_rows).to_csv(failed_csv, index=False)
    print(f"⚠️ Failed rows saved to {failed_csv}")

print("🎉 Geocoding completed successfully!")
