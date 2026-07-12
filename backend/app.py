from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app) 

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transitops.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            destination TEXT,
            vehicle_id INTEGER,
            driver_id INTEGER,
            cargo_weight REAL,
            planned_distance REAL,
            status TEXT DEFAULT 'Draft',
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY(driver_id) REFERENCES drivers(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            description TEXT,
            cost REAL,
            date_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vehicles")
    vehicles = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in vehicles]), 200

@app.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO vehicles (registration_number, name_model, type, max_load_capacity, odometer, acquisition_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('registration_number'), data.get('name_model'), data.get('type'), 
              data.get('max_load_capacity'), data.get('odometer'), data.get('acquisition_cost')))
        conn.commit()
        return jsonify({"message": "Vehicle registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM drivers")
    drivers = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in drivers]), 200

@app.route('/api/drivers', methods=['POST'])
def create_driver():
    data = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO drivers (name, license_number, license_category, license_expiry_date, contact_number, safety_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data.get('name'), data.get('license_number'), data.get('license_category'), 
              data.get('license_expiry_date'), data.get('contact_number'), data.get('safety_score')))
        conn.commit()
        return jsonify({"message": "Driver registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/trips/<int:trip_id>/dispatch', methods=['POST'])
def dispatch_trip(trip_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE trips SET status = 'Dispatched' WHERE id = ? AND status = 'Draft'", (trip_id,))
        if c.rowcount == 0:
            return jsonify({"error": "Trip not found or not in Draft status"}), 400
            
        c.execute("SELECT vehicle_id, driver_id FROM trips WHERE id = ?", (trip_id,))
        trip = c.fetchone()
        
        c.execute("UPDATE vehicles SET status = 'On Trip' WHERE id = ?", (trip['vehicle_id'],))
        c.execute("UPDATE drivers SET status = 'On Trip' WHERE id = ?", (trip['driver_id'],))
        
        conn.commit()
        return jsonify({"message": "Trip dispatched successfully"}), 200
    finally:
        conn.close()

@app.route('/api/trips/<int:trip_id>/complete', methods=['POST'])
def complete_trip(trip_id):
    data = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE trips SET status = 'Completed' WHERE id = ? AND status = 'Dispatched'", (trip_id,))
        if c.rowcount == 0:
            return jsonify({"error": "Trip not found or not Dispatched"}), 400
            
        c.execute("SELECT vehicle_id, driver_id FROM trips WHERE id = ?", (trip_id,))
        trip = c.fetchone()
        
        c.execute("UPDATE vehicles SET status = 'Available', odometer = ? WHERE id = ?", (data.get('final_odometer', 0), trip['vehicle_id']))
        c.execute("UPDATE drivers SET status = 'Available' WHERE id = ?", (trip['driver_id'],))
        
        conn.commit()
        return jsonify({"message": "Trip completed."}), 200
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)