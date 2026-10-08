import sqlite3

DATABASE = "insurance.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Vehicle models table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            vehicle_type TEXT NOT NULL
        )
    """)

    # Parts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (model_id) REFERENCES vehicle_models(id)
        )
    """)

    # Check whether vehicles already exist
    cursor.execute("SELECT COUNT(*) FROM vehicle_models")
    vehicle_count = cursor.fetchone()[0]

    if vehicle_count == 0:

        vehicles = [
            ("Maruti Suzuki", "Swift", "Car"),
            ("Maruti Suzuki", "Baleno", "Car"),
            ("Maruti Suzuki", "Brezza", "SUV"),

            ("Hyundai", "i20", "Car"),
            ("Hyundai", "Creta", "SUV"),
            ("Hyundai", "Venue", "SUV"),

            ("Tata", "Nexon", "SUV"),
            ("Tata", "Punch", "SUV"),
        ]

        cursor.executemany("""
            INSERT INTO vehicle_models
            (brand, model, vehicle_type)
            VALUES (?, ?, ?)
        """, vehicles)

    # Check whether parts exist
    cursor.execute("SELECT COUNT(*) FROM parts")
    part_count = cursor.fetchone()[0]

    if part_count == 0:

        # Get vehicle IDs
        cursor.execute("""
            SELECT id, brand, model
            FROM vehicle_models
        """)

        vehicles = cursor.fetchall()

        parts = []

        for vehicle in vehicles:

            model_id = vehicle["id"]
            model = vehicle["model"]

            # Demo prices — not official insurance/market rates

            if model == "Swift":
                prices = {
                    "Front Bumper": 8000,
                    "Rear Bumper": 8000,
                    "Front Door": 20000,
                    "Windshield": 12000,
                    "Bonnet": 18000,
                }

            elif model == "Baleno":
                prices = {
                    "Front Bumper": 8500,
                    "Rear Bumper": 8500,
                    "Front Door": 21000,
                    "Windshield": 12500,
                    "Bonnet": 19000,
                }

            elif model == "Brezza":
                prices = {
                    "Front Bumper": 10000,
                    "Rear Bumper": 10000,
                    "Front Door": 23000,
                    "Windshield": 14000,
                    "Bonnet": 22000,
                }

            elif model == "i20":
                prices = {
                    "Front Bumper": 9000,
                    "Rear Bumper": 9000,
                    "Front Door": 22000,
                    "Windshield": 13000,
                    "Bonnet": 20000,
                }

            elif model == "Creta":
                prices = {
                    "Front Bumper": 12000,
                    "Rear Bumper": 12000,
                    "Front Door": 28000,
                    "Windshield": 17000,
                    "Bonnet": 25000,
                }

            elif model == "Venue":
                prices = {
                    "Front Bumper": 10500,
                    "Rear Bumper": 10500,
                    "Front Door": 25000,
                    "Windshield": 15000,
                    "Bonnet": 22000,
                }

            elif model == "Nexon":
                prices = {
                    "Front Bumper": 10000,
                    "Rear Bumper": 10000,
                    "Front Door": 24000,
                    "Windshield": 14500,
                    "Bonnet": 21000,
                }

            elif model == "Punch":
                prices = {
                    "Front Bumper": 9500,
                    "Rear Bumper": 9500,
                    "Front Door": 22000,
                    "Windshield": 13500,
                    "Bonnet": 20000,
                }

            else:
                continue

            parts.extend([
                (model_id, "Front Bumper", "Rubber",
                 prices["Front Bumper"]),

                (model_id, "Rear Bumper", "Rubber",
                 prices["Rear Bumper"]),

                (model_id, "Front Door", "Metal",
                 prices["Front Door"]),

                (model_id, "Windshield", "Glass",
                 prices["Windshield"]),

                (model_id, "Bonnet", "Metal",
                 prices["Bonnet"]),
            ])

        cursor.executemany("""
            INSERT INTO parts
            (model_id, name, type, price)
            VALUES (?, ?, ?, ?)
        """, parts)

    connection.commit()
    connection.close()