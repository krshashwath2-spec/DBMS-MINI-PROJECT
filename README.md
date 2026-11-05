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

Open [http://localhost:8000](http://localhost:8000) and choose **Create account**. Sign in with an email address and password. The first registered account becomes Administrator; later self-registered accounts are Coordinators. Use a unique email address and a password of at least 12 characters. Administrators can also create Coordinator and additional Administrator accounts from **User accounts**. Administrators can reset another account's password there. A forgotten Administrator password can be reset locally with `py -3 app.py --reset-password EMAIL`; the command prompts for a new password and revokes that account's sessions. Coordinators should contact an Administrator for a reset. Password reset is intentionally not an unauthenticated public form because the local app has no verified email or identity-recovery service. Email is used as the login identifier; the app does not send email or verify ownership. For a database initialized with an account before browser signup, use `py -3 app.py --create-admin` once instead.

The server creates `relief_management.db` in the project directory, creates the SQLite schema and views, and imports the SQL example records from the project brief. This import is repeatable and adds missing examples without replacing existing records or applying historical distributions to current inventory; new distributions entered in the app still update stock. The `Field reports · MongoDB` section stores flexible field observations in a separate MongoDB database named `relief_management`, collection `field_reports`. MongoDB uses `mongodb://127.0.0.1:27017` by default; set `MONGODB_URI` and optionally `MONGODB_DATABASE` to use MongoDB Atlas or another server. The relational app remains available if MongoDB is stopped, but field report operations require MongoDB to be running. Press Ctrl+C to stop the server. Remove the SQLite database file only when you explicitly want to reset all local relational data.

## What is included

- Overview dashboard with incident, affected-person, resource, and shelter summaries.
- Dashboard emergency contacts for India: 112 (national emergency), 108 (ambulance), and 101 (fire services), with tap-to-call links; the supplied Relief Team number 656565 is highlighted in a moving red call banner.
- Searchable tables and create, edit, and delete forms for all 12 project entities.
- Login with SQLite-backed user accounts, salted PBKDF2 password hashes, and expiring server-side sessions.
- Two roles enforced by the API: Administrators can manage records and create accounts; Coordinators can view, add, and edit records but cannot delete records or manage accounts. The Coordinator UI also hides delete actions.
- Type linked disasters, affected areas, people, resources, shelters, and teams directly into their fields; existing records are suggested, and new entries are created automatically when the form is saved.
- Relational foreign keys, useful value checks, indexes, and database views for active affected people and shelter availability.
- Related disaster, area, person, resource, shelter, and rescue-team selections in forms.
- JSON CRUD API at `/api/<entity>` and dashboard endpoint at `/api/dashboard`.
- MongoDB-backed field report CRUD API at `/api/field_reports`, including flexible per-report `extra_fields` JSON.

## Database schema

`disaster` → `affected_area` → `affected_person` connects incidents with locations and residents. `relief_request` and `medical_request` record response needs. `shelter` and `shelter_allocation` track placement and capacity. `resource` and `inventory` track supplies; `supply_distribution` records delivery to an area or shelter. `rescue_team` and `vehicle` coordinate field response. Foreign keys preserve these relationships.

The app's dashboard demonstrates SELECT, JOIN, GROUP BY, aggregate, and view queries. The schema also defines indexes and triggers to maintain inventory and shelter counts when distributions and allocations change. MongoDB is used for flexible incident observations whose fields can vary between reports; it supplements rather than replaces the SQLite DBMS portion of the project.

Email addresses, password hashes, roles, and session hashes are stored in the `app_user` and `auth_session` SQLite tables. SQLite does not provide per-user database grants, so role-based access is enforced by the backend on every API request using the persisted database role. Do not expose this prototype to the public internet; production use needs HTTPS, stronger operational controls, and security review. When serving behind HTTPS, set `RELIEF_COOKIE_SECURE=1` to add the Secure cookie attribute.

## Run tests

```powershell
py -3 -m unittest discover -s tests -v
```

Tests use a temporary SQLite database and exercise authentication, role permissions, the schema, dashboard, CRUD and relationship flow, database safeguards, and static frontend.
