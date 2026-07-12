from flask import Flask, request, jsonify, send_from_directory
import requests
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='.')

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
def calculate_route_distance(lon1, lat1, lon2, lat2):
    """
    Calls the free OSRM API to get the driving distance between two coordinates.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("code") == "Ok":
            # OSRM returns distance in meters, convert to kilometers
            distance_km = data["routes"][0]["distance"] / 1000.0
            return round(distance_km, 2)
        return None
    except Exception as e:
        print(f"Routing API Error: {e}")
        return None

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

@app.route('/api/trips', methods=['GET'])
def get_trips():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT trips.*, vehicles.registration_number, drivers.name as driver_name 
        FROM trips
        JOIN vehicles ON trips.vehicle_id = vehicles.id
        JOIN drivers ON trips.driver_id = drivers.id
    ''')
    trips = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in trips]), 200

@app.route('/api/trips', methods=['POST'])
def create_trip():
    data = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM vehicles WHERE id = ?", (data.get('vehicle_id'),))
        vehicle = c.fetchone()
        if not vehicle: return jsonify({"error": "Vehicle not found"}), 404
        if vehicle['status'] != 'Available': return jsonify({"error": "Vehicle is not available"}), 400
        if float(data.get('cargo_weight', 0)) > vehicle['max_load_capacity']: return jsonify({"error": "Cargo exceeds capacity"}), 400

        c.execute("SELECT * FROM drivers WHERE id = ?", (data.get('driver_id'),))
        driver = c.fetchone()
        if not driver: return jsonify({"error": "Driver not found"}), 404
        if driver['status'] != 'Available': return jsonify({"error": "Driver is not available"}), 400

        c.execute('''
            INSERT INTO trips (source, destination, vehicle_id, driver_id, cargo_weight, planned_distance, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Draft')
        ''', (data.get('source'), data.get('destination'), data.get('vehicle_id'), data.get('driver_id'), 
              data.get('cargo_weight'), data.get('planned_distance')))
        conn.commit()
        return jsonify({"message": "Trip created successfully", "trip_id": c.lastrowid}), 201
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
        if c.rowcount == 0: return jsonify({"error": "Trip not found or not in Draft status"}), 400
            
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
        if c.rowcount == 0: return jsonify({"error": "Trip not found or not Dispatched"}), 400
            
        c.execute("SELECT vehicle_id, driver_id FROM trips WHERE id = ?", (trip_id,))
        trip = c.fetchone()
        
        c.execute("UPDATE vehicles SET status = 'Available', odometer = ? WHERE id = ?", (data.get('final_odometer', 0), trip['vehicle_id']))
        c.execute("UPDATE drivers SET status = 'Available' WHERE id = ?", (trip['driver_id'],))
        conn.commit()
        return jsonify({"message": "Trip completed."}), 200
    finally:
        conn.close()

@app.route('/api/maintenance', methods=['POST'])
def create_maintenance_log():
    data = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE vehicles SET status = 'In Shop' WHERE id = ?", (data.get('vehicle_id'),))
        if c.rowcount == 0: return jsonify({"error": "Vehicle not found"}), 404
             
        c.execute('''
            INSERT INTO maintenance_logs (vehicle_id, description, cost)
            VALUES (?, ?, ?)
        ''', (data.get('vehicle_id'), data.get('description'), data.get('cost')))
        conn.commit()
        return jsonify({"message": "Maintenance logged. Vehicle In Shop."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/route/calculate', methods=['POST'])
def get_optimal_route():
    data = request.get_json()

    lon1 = data.get('source_lon')
    lat1 = data.get('source_lat')
    lon2 = data.get('dest_lon')
    lat2 = data.get('dest_lat')
    
    if not all([lon1, lat1, lon2, lat2]):
        return jsonify({"error": "Missing coordinate data"}), 400
        
    distance = calculate_route_distance(lon1, lat1, lon2, lat2)
    
    if distance:
        return jsonify({
            "message": "Route calculated successfully",
            "distance_km": distance,
            "estimated_fuel_cost": round(distance * 0.15, 2)
        }), 200
    else:
        return jsonify({"error": "Could not calculate route"}), 500

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/dashboard/kpis', methods=['GET'])
def get_kpis():
    conn = get_db_connection()
    c = conn.cursor()
    # Count database items for the dashboard
    c.execute("SELECT COUNT(*) FROM vehicles")
    total_v = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'Available'")
    avail_v = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'In Shop'")
    maint_v = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trips WHERE status = 'Dispatched'")
    active_t = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        "activeVehicles": total_v - avail_v,
        "availableVehicles": avail_v,
        "inMaintenance": maint_v,
        "utilization": round(((total_v - avail_v) / total_v) * 100) if total_v > 0 else 0,
        "activeTrips": active_t,
        "pendingTrips": 0,
        "driversOnDuty": 0
    })

@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify({
        "operationalCost": 184200,
        "fleetUtilization": 81,
        "perVehicle": [
            {"name": "Truck-11", "fuel": 30000, "maint": 12300, "total": 42300},
            {"name": "Van-05", "fuel": 10000, "maint": 8900, "total": 18900}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)