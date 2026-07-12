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

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY, reg TEXT UNIQUE, name TEXT, max_load_capacity REAL, status TEXT DEFAULT "Available")')
    conn.execute('CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY, name TEXT, status TEXT DEFAULT "Available")')
    conn.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, vehicle_id INTEGER, driver_id INTEGER, status TEXT, FOREIGN KEY(vehicle_id) REFERENCES vehicles(id), FOREIGN KEY(driver_id) REFERENCES drivers(id))')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index(): return send_from_directory('.', 'dashboard.html')

@app.route('/<path:path>')
def serve_files(path): return send_from_directory('.', path)

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    avail = conn.execute("SELECT COUNT(*) FROM vehicles WHERE status='Available'").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM trips WHERE status='Dispatched'").fetchone()[0]
    conn.close()
    return jsonify({"activeVehicles": total-avail, "availableVehicles": avail, "activeTrips": active})

@app.route('/api/vehicles', methods=['GET', 'POST'])
def handle_vehicles():
    conn = get_db()
    if request.method == 'POST':
        data = request.json
        conn.execute("INSERT INTO vehicles (reg, name, max_load_capacity) VALUES (?, ?, ?)", (data['reg'], data['name'], data['cap']))
        conn.commit()
        return jsonify({"message": "Added"}), 201
    vehicles = [dict(v) for v in conn.execute("SELECT * FROM vehicles").fetchall()]
    conn.close()
    return jsonify(vehicles)

@app.route('/api/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    conn = get_db()
    try:
        # Business Rule: Dispatching checks availability
        v = conn.execute("SELECT * FROM vehicles WHERE id=?", (data['v_id'],)).fetchone()
        if v['status'] != 'Available': return jsonify({"error": "Vehicle busy"}), 400
        conn.execute("UPDATE vehicles SET status='On Trip' WHERE id=?", (data['v_id'],))
        conn.execute("INSERT INTO trips (vehicle_id, driver_id, status) VALUES (?, ?, 'Dispatched')", (data['v_id'], data['d_id']))
        conn.commit()
        return jsonify({"message": "Success"})
    finally: conn.close()

if __name__ == '__main__':
    app.run(port=5000)