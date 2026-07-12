# Odoo-Hackathon
GitHub repository for our team

# TransitOps Backend
A high-performance logistics and fleet management API built with Flask, SQLite, and OSRM integration.

## Key API Endpoints
- `GET /api/vehicles`: List all fleet assets.
- `GET /api/drivers`: List all drivers and safety scores.
- `POST /api/trips`: Create a new dispatch request (Validates load capacity & availability).
- `POST /api/route/calculate`: Real-time routing distance via OSRM.
- `POST /api/maintenance`: Log maintenance and flag vehicle status as "In Shop".

## Architecture
- **Database**: SQLite with automated relational schema (Vehicles, Drivers, Trips, Maintenance).
- **Security**: CORS enabled for cross-platform frontend integration.
- **Routing**: OSRM API integration for automated distance calculation.