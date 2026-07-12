import sqlite3
import os

def seed_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transitops.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number TEXT UNIQUE,
            name_model TEXT,
            type TEXT,
            max_load_capacity REAL,
            odometer REAL,
            acquisition_cost REAL,
            status TEXT DEFAULT 'Available'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            license_number TEXT UNIQUE,
            license_category TEXT,
            license_expiry_date TEXT,
            contact_number TEXT,
            safety_score REAL,
            status TEXT DEFAULT 'Available'
        )
    ''')

    vehicles = [
        ('VAN-01', 'Ford Transit', 'Van', 1000.0, 15000, 35000),
        ('TRK-99', 'Volvo FH16', 'Heavy Truck', 25000.0, 120000, 150000),
        ('VAN-02', 'Mercedes Sprinter', 'Van', 1200.0, 5000, 42000)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO vehicles (registration_number, name_model, type, max_load_capacity, odometer, acquisition_cost)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', vehicles)

    drivers = [
        ('Alex Mercer', 'DL-12345', 'Heavy', '2028-10-15', '555-0101', 9.5),
        ('Sarah Connor', 'DL-98765', 'Light', '2027-05-22', '555-0202', 8.8)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO drivers (name, license_number, license_category, license_expiry_date, contact_number, safety_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', drivers)

    conn.commit()
    conn.close()
    
    print(f"Data successfully seeded into database at: {db_path}")

if __name__ == '__main__':
    seed_database()