# ReliefFlow — Disaster Response and Relief Management System

A full-stack DBMS mini project for coordinating disasters, affected areas and people, relief and medical requests, shelters and allocations, resources and inventory, supply distributions, rescue teams, and vehicles. It follows the 12-table schema in the project brief. Python's standard library and SQLite power the relational application; PyMongo connects the optional NoSQL field-report feature to MongoDB.

## Run locally

Requires Python 3.10 or newer and MongoDB running locally (or a MongoDB Atlas connection string). From the project directory:

```powershell
py -3 -m pip install -r requirements.txt
py -3 app.py
```

Or, on systems where Python is on PATH:

```sh
python3 -m pip install -r requirements.txt
python3 app.py
```

Open [http://localhost:8000](http://localhost:8000). The server creates `relief_management.db` in the project directory at first startup, creates the SQLite schema and views, and imports the SQL example records from the project brief. This import is repeatable and adds missing examples without replacing existing records or applying historical distributions to current inventory; new distributions entered in the app still update stock. The `Field reports · MongoDB` section stores flexible field observations in a separate MongoDB database named `relief_management`, collection `field_reports`. MongoDB uses `mongodb://127.0.0.1:27017` by default; set `MONGODB_URI` and optionally `MONGODB_DATABASE` to use MongoDB Atlas or another server. The relational app remains available if MongoDB is stopped, but field report operations require MongoDB to be running. Press Ctrl+C to stop the server. Remove the SQLite database file only when you explicitly want to reset all local relational data.

## What is included

- Overview dashboard with incident, affected-person, resource, and shelter summaries.
- Dashboard emergency contacts for India: 112 (national emergency), 108 (ambulance), and 101 (fire services), with tap-to-call links; the supplied Relief Team number 656565 is highlighted in a moving red call banner.
- Searchable tables and create, edit, and delete forms for all 12 project entities.
- Type linked disasters, affected areas, people, resources, shelters, and teams directly into their fields; existing records are suggested, and new entries are created automatically when the form is saved.
- Relational foreign keys, useful value checks, indexes, and database views for active affected people and shelter availability.
- Related disaster, area, person, resource, shelter, and rescue-team selections in forms.
- JSON CRUD API at `/api/<entity>` and dashboard endpoint at `/api/dashboard`.
- MongoDB-backed field report CRUD API at `/api/field_reports`, including flexible per-report `extra_fields` JSON.

## Database schema

`disaster` → `affected_area` → `affected_person` connects incidents with locations and residents. `relief_request` and `medical_request` record response needs. `shelter` and `shelter_allocation` track placement and capacity. `resource` and `inventory` track supplies; `supply_distribution` records delivery to an area or shelter. `rescue_team` and `vehicle` coordinate field response. Foreign keys preserve these relationships.

The app's dashboard demonstrates SELECT, JOIN, GROUP BY, aggregate, and view queries. The schema also defines indexes and triggers to maintain inventory and shelter counts when distributions and allocations change. MongoDB is used for flexible incident observations whose fields can vary between reports; it supplements rather than replaces the SQLite DBMS portion of the project.

## Run tests

```powershell
py -3 -m unittest discover -s tests -v
```

Tests use a temporary SQLite database and exercise the schema, dashboard, CRUD and relationship flow, database safeguards, and static frontend.
