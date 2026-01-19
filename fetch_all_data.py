import requests
import json
import random

BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

def clean_text(text):
    if not text: return ""
    return str(text).replace('"', "'").replace('\n', ' ').strip()

def fetch_food():
    print("\n[FOOD] Fetching Food Violations...")
    pkg = requests.get(f"{BASE_URL}/api/3/action/package_show", params={"id": "dinesafe"}).json()
    res_id = next(r["id"] for r in pkg["result"]["resources"] if r["datastore_active"])
    data = requests.get(f"{BASE_URL}/api/3/action/datastore_search", params={"id": res_id, "limit": 50000}).json()
    records = data["result"]["records"]

    danger_list = []
    for place in records:
        status = str(place.get('Establishment Status', '')).upper()
        if "CONDITIONAL" not in status and "CLOSED" not in status:
            continue

        try:
            lat = float(place.get('Latitude'))
            lon = float(place.get('Longitude'))
        except (TypeError, ValueError):
            continue

        lat += random.uniform(-0.0001, 0.0001)
        lon += random.uniform(-0.0001, 0.0001)

        details = clean_text(place.get('Infraction Details', '')).lower()

        code = "!"
        hazard_type = "GENERAL"

        if any(kw in details for kw in ["rodent", "mouse", "mice", "rat", "droppings"]):
            code = "R"; hazard_type = "RODENT"
        elif any(kw in details for kw in ["cockroach", "roach", "flies", "fly ", "insect", "vermin"]):
            code = "B"; hazard_type = "INSECT"
        elif any(kw in details for kw in ["temperature", "cold holding", "hot holding", "4 c", "60 c", "thaw", "refrigerat"]):
            code = "T"; hazard_type = "TEMP"
        elif any(kw in details for kw in ["contamina", "adulterat", "cross-contam"]):
            code = "X"; hazard_type = "CONTAMINATION"
        elif any(kw in details for kw in ["sewage", "backup", "drain block"]):
            code = "S"; hazard_type = "SEWAGE"
        elif any(kw in details for kw in ["handwash", "hand wash", "soap", "sanitary condition"]):
            code = "H"; hazard_type = "HYGIENE"

        danger_list.append({
            "name": clean_text(place.get('Establishment Name')),
            "address": clean_text(place.get('Establishment Address')),
            "status": status,
            "code": code,
            "hazard": hazard_type,
            "infractions": clean_text(place.get('Infraction Details')),
            "date": str(place.get('Inspection Date', ''))[:10],
            "severity": clean_text(place.get('Severity', '')),
            "lat": lat, "lon": lon
        })

    with open('data_food.json', 'w') as f:
        json.dump(danger_list, f)
    print(f"   Done: Saved {len(danger_list)} food violations")
    return len(danger_list)

if __name__ == "__main__":
    print("="*50)
    print("  TORONTO EXPOSED - Food Data Fetcher")
    print("="*50)

    total = fetch_food()

    print("\n" + "="*50)
    print(f"  TOTAL: {total} incidents saved")
    print("="*50)
    print("\nFile created: data_food.json")
