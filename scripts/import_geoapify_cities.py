"""
Geoapify World Cities Dataset Importer & Seeder.
Imports global locality records (cities, towns, villages, hamlets) into SQLite (world_cities table).
Preserves uniqueness using osm_type + osm_id.
"""

import sys
import os
import json
import zipfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.database import SessionLocal, engine, Base
from app.database.models import WorldCity


SAMPLE_GEOAPIFY_WORLD_CITIES = [
    # India
    {"name": "Hyderabad", "country_code": "IN", "country_name": "India", "state": "Telangana", "county": "Hyderabad", "population": 6809970, "settlement_type": "city", "latitude": 17.3850, "longitude": 78.4867, "osm_type": "node", "osm_id": "24560945"},
    {"name": "Amalapuram", "country_code": "IN", "country_name": "India", "state": "Andhra Pradesh", "county": "East Godavari", "population": 53231, "settlement_type": "town", "latitude": 16.5787, "longitude": 82.0061, "osm_type": "node", "osm_id": "31456980"},
    {"name": "Delhi", "country_code": "IN", "country_name": "India", "state": "Delhi", "county": "Central Delhi", "population": 11034555, "settlement_type": "city", "latitude": 28.6139, "longitude": 77.2090, "osm_type": "node", "osm_id": "19409823"},
    {"name": "Mumbai", "country_code": "IN", "country_name": "India", "state": "Maharashtra", "county": "Mumbai Suburban", "population": 12442373, "settlement_type": "city", "latitude": 19.0760, "longitude": 72.8777, "osm_type": "node", "osm_id": "24560111"},
    {"name": "Panaji", "country_code": "IN", "country_name": "India", "state": "Goa", "county": "North Goa", "population": 114759, "settlement_type": "city", "latitude": 15.4909, "longitude": 73.8278, "osm_type": "node", "osm_id": "29875412"},
    {"name": "Manali", "country_code": "IN", "country_name": "India", "state": "Himachal Pradesh", "county": "Kullu", "population": 8096, "settlement_type": "town", "latitude": 32.2432, "longitude": 77.1892, "osm_type": "node", "osm_id": "40198234"},
    
    # Japan
    {"name": "Tokyo", "country_code": "JP", "country_name": "Japan", "state": "Tokyo", "county": "Special Wards", "population": 13960000, "settlement_type": "city", "latitude": 35.6762, "longitude": 139.6503, "osm_type": "node", "osm_id": "12345678"},
    {"name": "Kyoto", "country_code": "JP", "country_name": "Japan", "state": "Kyoto", "county": "Kyoto City", "population": 1475000, "settlement_type": "city", "latitude": 35.0116, "longitude": 135.7681, "osm_type": "node", "osm_id": "23456789"},
    {"name": "Osaka", "country_code": "JP", "country_name": "Japan", "state": "Osaka", "county": "Osaka City", "population": 2691000, "settlement_type": "city", "latitude": 34.6937, "longitude": 135.5023, "osm_type": "node", "osm_id": "34567890"},

    # France
    {"name": "Paris", "country_code": "FR", "country_name": "France", "state": "Île-de-France", "county": "Paris", "population": 2161000, "settlement_type": "city", "latitude": 48.8566, "longitude": 2.3522, "osm_type": "node", "osm_id": "45678901"},
    {"name": "Nice", "country_code": "FR", "country_name": "France", "state": "Provence-Alpes-Côte d'Azur", "county": "Alpes-Maritimes", "population": 342522, "settlement_type": "city", "latitude": 43.7102, "longitude": 7.2620, "osm_type": "node", "osm_id": "56789012"},
    {"name": "Lyon", "country_code": "FR", "country_name": "France", "state": "Auvergne-Rhône-Alpes", "county": "Rhône", "population": 515695, "settlement_type": "city", "latitude": 45.7640, "longitude": 4.8357, "osm_type": "node", "osm_id": "67890123"},

    # Italy
    {"name": "Rome", "country_code": "IT", "country_name": "Italy", "state": "Lazio", "county": "Rome", "population": 2873000, "settlement_type": "city", "latitude": 41.9028, "longitude": 12.4964, "osm_type": "node", "osm_id": "78901234"},
    {"name": "Florence", "country_code": "IT", "country_name": "Italy", "state": "Tuscany", "county": "Florence", "population": 382258, "settlement_type": "city", "latitude": 43.7696, "longitude": 11.2558, "osm_type": "node", "osm_id": "89012345"},

    # UK
    {"name": "London", "country_code": "GB", "country_name": "United Kingdom", "state": "England", "county": "Greater London", "population": 8982000, "settlement_type": "city", "latitude": 51.5074, "longitude": -0.1278, "osm_type": "node", "osm_id": "90123456"},

    # USA
    {"name": "New York", "country_code": "US", "country_name": "United States", "state": "New York", "county": "New York County", "population": 8419000, "settlement_type": "city", "latitude": 40.7128, "longitude": -74.0060, "osm_type": "node", "osm_id": "10987654"},

    # UAE
    {"name": "Dubai", "country_code": "AE", "country_name": "United Arab Emirates", "state": "Dubai", "county": "Dubai", "population": 3331000, "settlement_type": "city", "latitude": 25.2048, "longitude": 55.2708, "osm_type": "node", "osm_id": "21098765"},

    # Switzerland
    {"name": "Zurich", "country_code": "CH", "country_name": "Switzerland", "state": "Zurich", "county": "Zurich District", "population": 402762, "settlement_type": "city", "latitude": 47.3769, "longitude": 8.5417, "osm_type": "node", "osm_id": "32109876"}
]


def import_world_cities():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    count_imported = 0
    count_skipped = 0

    try:
        for c in SAMPLE_GEOAPIFY_WORLD_CITIES:
            existing = db.query(WorldCity).filter(
                WorldCity.osm_type == c["osm_type"],
                WorldCity.osm_id == c["osm_id"]
            ).first()

            if existing:
                count_skipped += 1
                continue

            city_obj = WorldCity(
                name=c["name"],
                normalized_name=c["name"].lower().strip(),
                display_name=f"{c['name']}, {c.get('state', '')}, {c['country_name']}".strip(", "),
                country_code=c["country_code"],
                country_name=c["country_name"],
                state=c.get("state"),
                county=c.get("county"),
                population=c["population"],
                settlement_type=c["settlement_type"],
                latitude=c["latitude"],
                longitude=c["longitude"],
                osm_type=c["osm_type"],
                osm_id=c["osm_id"]
            )
            db.add(city_obj)
            count_imported += 1

        db.commit()
        print(f"[GEOAPIFY IMPORT SUCCESS] Imported {count_imported} localities ({count_skipped} skipped duplicates). Total WorldCities in DB: {db.query(WorldCity).count()}")
    except Exception as e:
        db.rollback()
        print(f"[GEOAPIFY IMPORT ERROR] {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import_world_cities()
