import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "travel_planner.db"))
print("Connecting to SQLite database:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

additional_countries = [
    ("Liechtenstein", "LI", "Europe", "🇱🇮", 47.1410, 9.5209, "Alpine microstate known for medieval castles, mountain trails, and skiing."),
    ("Kosovo", "XK", "Europe", "🇽🇰", 42.6026, 20.9030, "Balkan nation known for Ottoman architecture in Prizren and Rugova Canyon."),
    ("Palestine", "PS", "Asia", "🇵🇸", 31.9522, 35.2332, "Historic Holy Land region featuring Bethlehem Nativity Church and Jericho.")
]

cursor.execute("SELECT code, name FROM countries")
existing_rows = cursor.fetchall()
existing_codes = set(row[0].upper() for row in existing_rows if row[0])
existing_names = set(row[1].lower() for row in existing_rows if row[1])

inserted = 0
for name, code, continent, flag_emoji, lat, lng, description in additional_countries:
    if code.upper() not in existing_codes and name.lower() not in existing_names:
        cursor.execute("""
            INSERT INTO countries (name, code, continent, flag_emoji, latitude, longitude, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, code, continent, flag_emoji, lat, lng, description, f"/static/images/countries/{code.lower()}.jpg"))
        existing_codes.add(code.upper())
        existing_names.add(name.lower())
        inserted += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM countries")
total = cursor.fetchone()[0]
print(f"Inserted {inserted} new countries. Total countries now in database: {total}")

conn.close()
