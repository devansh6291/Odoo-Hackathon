import sqlite3

def seed_database():
    conn = sqlite3.connect('transitops.db')
    c = conn.cursor()

    # Insert Dummy Vehicles
    vehicles = [
        ('VAN-01', 'Ford Transit', 'Van', 1000.0, 15000, 35000),
        ('TRK-99', 'Volvo FH16', 'Heavy Truck', 25000.0, 120000, 150000),
        ('VAN-02', 'Mercedes Sprinter', 'Van', 1200.0, 5000, 42000)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO vehicles (registration_number, name_model, type, max_load_capacity, odometer, acquisition_cost)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', vehicles)

    # Insert Dummy Drivers
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
    print("Database seeded with test vehicles and drivers!")

if __name__ == '__main__':
    seed_database()

if __name__ == '__main__':
    seed_database()