from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='.')
CORS(app)

def get_db():
    conn = sqlite3.connect('transitops.db')
    conn.row_factory = sqlite3.Row
    return conn

# Automatic Database Setup
def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY, reg TEXT UNIQUE, name TEXT, max_load_capacity REAL, status TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, vehicle_id INTEGER, status TEXT, FOREIGN KEY(vehicle_id) REFERENCES vehicles(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, name TEXT, status TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---
@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    avail = conn.execute("SELECT COUNT(*) FROM vehicles WHERE status='Available'").fetchone()[0]
    maint = conn.execute("SELECT COUNT(*) FROM vehicles WHERE status='In Shop'").fetchone()[0]
    active_trips = conn.execute("SELECT COUNT(*) FROM trips WHERE status='Dispatched'").fetchone()[0]
    conn.close()
    return jsonify({"total": total, "available": avail, "maintenance": maint, "activeTrips": active_trips})

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = get_db()
    vehicles = [dict(v) for v in conn.execute("SELECT * FROM vehicles").fetchall()]
    conn.close()
    return jsonify(vehicles)

@app.route('/api/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    conn = get_db()
    try:
        # Business Rule validation
        veh = conn.execute("SELECT * FROM vehicles WHERE id=?", (data['v_id'],)).fetchone()
        if not veh or veh['status'] != 'Available':
            return jsonify({"error": "Vehicle not available"}), 400
        
        conn.execute("UPDATE vehicles SET status='On Trip' WHERE id=?", (data['v_id'],))
        conn.execute("INSERT INTO trips (vehicle_id, status) VALUES (?, 'Dispatched')", (data['v_id'],))
        conn.commit()
        return jsonify({"message": "Dispatched successfully"})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)