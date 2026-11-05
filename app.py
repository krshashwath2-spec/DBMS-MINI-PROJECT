"""SQLite-backed Disaster Response and Relief Management System."""

from __future__ import annotations

import json
import math
import mimetypes
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import project_data
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATABASE = Path(__import__("os").environ.get("RELIEF_DB", ROOT / "relief_management.db"))
HOST = "127.0.0.1"
PORT = int(__import__("os").environ.get("PORT", "8000"))
MONGODB_URI = __import__("os").environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DATABASE = __import__("os").environ.get("MONGODB_DATABASE", "relief_management")
_mongo_client: MongoClient | None = None

# API path -> SQL table, primary key, form fields.
ENTITIES = {
    "disasters": ("disaster", "disaster_id", (
        "disaster_name", "disaster_type", "start_date", "end_date", "severity", "status", "description")),
    "affected_areas": ("affected_area", "area_id", (
        "disaster_id", "area_name", "location", "people_affected", "priority_level")),
    "affected_people": ("affected_person", "person_id", (
        "area_id", "person_name", "age", "gender", "contact_no", "address", "need_type", "priority")),
    "relief_requests": ("relief_request", "request_id", (
        "area_id", "person_id", "request_type", "resource_id", "quantity_needed", "priority", "request_date", "status", "remarks")),
    "medical_requests": ("medical_request", "medical_req_id", (
        "person_id", "medical_issue", "priority", "request_date", "status", "assigned_to", "notes")),
    "shelters": ("shelter", "shelter_id", (
        "shelter_name", "location", "capacity", "current_occupancy", "shelter_type", "contact_no", "status")),
    "shelter_allocations": ("shelter_allocation", "allocation_id", (
        "person_id", "shelter_id", "allocation_date", "status", "remarks")),
    "resources": ("resource", "resource_id", ("resource_name", "resource_type", "unit")),
    "inventory": ("inventory", "inventory_id", (
        "resource_id", "quantity_available", "last_updated", "location")),
    "supply_distributions": ("supply_distribution", "distribution_id", (
        "resource_id", "to_shelter_id", "to_area_id", "quantity_distributed", "distribution_date", "distributed_by", "remarks")),
    "rescue_teams": ("rescue_team", "team_id", ("team_name", "team_type", "team_leader", "contact_no", "status")),
    "vehicles": ("vehicle", "vehicle_id", (
        "team_id", "vehicle_type", "registration_no", "capacity", "status", "current_location")),
}

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS disaster (
 disaster_id INTEGER PRIMARY KEY AUTOINCREMENT,
 disaster_name TEXT NOT NULL, disaster_type TEXT NOT NULL DEFAULT 'Other',
 start_date TEXT, end_date TEXT,
 severity TEXT NOT NULL DEFAULT 'Moderate' CHECK(severity IN ('Low','Moderate','High','Critical')),
 status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Monitoring','Resolved')),
 description TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS affected_area (
 area_id INTEGER PRIMARY KEY AUTOINCREMENT,
 disaster_id INTEGER REFERENCES disaster(disaster_id) ON DELETE SET NULL,
 area_name TEXT NOT NULL, location TEXT NOT NULL,
 people_affected INTEGER NOT NULL DEFAULT 0 CHECK(people_affected >= 0),
 priority_level TEXT NOT NULL DEFAULT 'Medium' CHECK(priority_level IN ('Low','Medium','High','Critical'))
);
CREATE TABLE IF NOT EXISTS affected_person (
 person_id INTEGER PRIMARY KEY AUTOINCREMENT,
 area_id INTEGER REFERENCES affected_area(area_id) ON DELETE SET NULL,
 person_name TEXT NOT NULL, age INTEGER CHECK(age IS NULL OR age BETWEEN 0 AND 120),
 gender TEXT NOT NULL DEFAULT 'Not specified', contact_no TEXT NOT NULL DEFAULT '',
 address TEXT NOT NULL DEFAULT '', need_type TEXT NOT NULL DEFAULT 'General assistance',
 priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High','Critical'))
);
CREATE TABLE IF NOT EXISTS resource (
 resource_id INTEGER PRIMARY KEY AUTOINCREMENT, resource_name TEXT NOT NULL,
 resource_type TEXT NOT NULL, unit TEXT NOT NULL DEFAULT 'units'
);
CREATE TABLE IF NOT EXISTS relief_request (
 request_id INTEGER PRIMARY KEY AUTOINCREMENT,
 area_id INTEGER REFERENCES affected_area(area_id) ON DELETE SET NULL,
 person_id INTEGER REFERENCES affected_person(person_id) ON DELETE SET NULL,
 request_type TEXT NOT NULL, resource_id INTEGER REFERENCES resource(resource_id) ON DELETE SET NULL,
 quantity_needed REAL NOT NULL DEFAULT 1 CHECK(quantity_needed >= 0),
 priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High','Critical')),
 request_date TEXT NOT NULL DEFAULT (date('now')),
 status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Fulfilled','Rejected')),
 remarks TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS medical_request (
 medical_req_id INTEGER PRIMARY KEY AUTOINCREMENT,
 person_id INTEGER REFERENCES affected_person(person_id) ON DELETE SET NULL,
 medical_issue TEXT NOT NULL, priority TEXT NOT NULL DEFAULT 'Medium'
 CHECK(priority IN ('Low','Medium','High','Critical')),
 request_date TEXT NOT NULL DEFAULT (date('now')),
 status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Assigned','Completed')),
 assigned_to TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS shelter (
 shelter_id INTEGER PRIMARY KEY AUTOINCREMENT, shelter_name TEXT NOT NULL, location TEXT NOT NULL,
 capacity INTEGER NOT NULL CHECK(capacity >= 0),
 current_occupancy INTEGER NOT NULL DEFAULT 0 CHECK(current_occupancy >= 0 AND current_occupancy <= capacity),
 shelter_type TEXT NOT NULL DEFAULT 'Relief shelter', contact_no TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','Full','Closed'))
);
CREATE TABLE IF NOT EXISTS shelter_allocation (
 allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
 person_id INTEGER REFERENCES affected_person(person_id) ON DELETE SET NULL,
 shelter_id INTEGER REFERENCES shelter(shelter_id) ON DELETE SET NULL,
 allocation_date TEXT NOT NULL DEFAULT (date('now')),
 status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Released')),
 remarks TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS inventory (
 inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
 resource_id INTEGER NOT NULL REFERENCES resource(resource_id) ON DELETE CASCADE,
 quantity_available REAL NOT NULL DEFAULT 0 CHECK(quantity_available >= 0),
 last_updated TEXT NOT NULL DEFAULT (datetime('now')), location TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS supply_distribution (
 distribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
 resource_id INTEGER NOT NULL REFERENCES resource(resource_id),
 to_shelter_id INTEGER REFERENCES shelter(shelter_id) ON DELETE SET NULL,
 to_area_id INTEGER REFERENCES affected_area(area_id) ON DELETE SET NULL,
 quantity_distributed REAL NOT NULL CHECK(quantity_distributed > 0),
 distribution_date TEXT NOT NULL DEFAULT (date('now')),
 distributed_by TEXT NOT NULL DEFAULT '', remarks TEXT NOT NULL DEFAULT '',
 CHECK(to_shelter_id IS NOT NULL OR to_area_id IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS rescue_team (
 team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT NOT NULL,
 team_type TEXT NOT NULL DEFAULT 'General response', team_leader TEXT NOT NULL DEFAULT '',
 contact_no TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'Available' CHECK(status IN ('Available','Deployed','Unavailable'))
);
CREATE TABLE IF NOT EXISTS vehicle (
 vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
 team_id INTEGER REFERENCES rescue_team(team_id) ON DELETE SET NULL,
 vehicle_type TEXT NOT NULL, registration_no TEXT NOT NULL UNIQUE,
 capacity INTEGER NOT NULL DEFAULT 1 CHECK(capacity >= 0),
 status TEXT NOT NULL DEFAULT 'Available' CHECK(status IN ('Available','In use','Maintenance')),
 current_location TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_affected_area_disaster ON affected_area(disaster_id);
CREATE INDEX IF NOT EXISTS idx_affected_person_area ON affected_person(area_id);
CREATE INDEX IF NOT EXISTS idx_relief_request_status ON relief_request(status, priority);
CREATE INDEX IF NOT EXISTS idx_medical_request_status ON medical_request(status, priority);
CREATE INDEX IF NOT EXISTS idx_allocation_shelter ON shelter_allocation(shelter_id, status);
CREATE INDEX IF NOT EXISTS idx_distribution_date ON supply_distribution(distribution_date);
CREATE VIEW IF NOT EXISTS active_affected_people AS
 SELECT p.person_id,p.person_name,p.age,p.gender,p.contact_no,p.need_type,p.priority,
        a.area_name,a.location,d.disaster_name
 FROM affected_person p LEFT JOIN affected_area a ON a.area_id=p.area_id
 LEFT JOIN disaster d ON d.disaster_id=a.disaster_id;
CREATE VIEW IF NOT EXISTS shelter_availability AS
 SELECT shelter_id,shelter_name,location,capacity,current_occupancy,
        capacity-current_occupancy AS spaces_available,shelter_type,status
 FROM shelter;
CREATE TRIGGER IF NOT EXISTS allocation_increments_shelter
 AFTER INSERT ON shelter_allocation WHEN NEW.status='Active' AND NEW.shelter_id IS NOT NULL
 BEGIN
  UPDATE shelter SET current_occupancy=current_occupancy+1 WHERE shelter_id=NEW.shelter_id;
 END;
CREATE TRIGGER IF NOT EXISTS allocation_checks_capacity
 BEFORE INSERT ON shelter_allocation
 WHEN NEW.status='Active' AND NEW.shelter_id IS NOT NULL
 BEGIN
  SELECT CASE WHEN NOT EXISTS (
   SELECT 1 FROM shelter WHERE shelter_id=NEW.shelter_id AND status!='Closed'
    AND current_occupancy<capacity
  ) THEN RAISE(ABORT,'Shelter is closed or has no available spaces.') END;
 END;
CREATE TRIGGER IF NOT EXISTS allocation_releases_shelter
 AFTER UPDATE OF status,shelter_id ON shelter_allocation
 WHEN OLD.status='Active' AND (NEW.status!='Active' OR OLD.shelter_id IS NOT NEW.shelter_id)
 BEGIN
  UPDATE shelter SET current_occupancy=MAX(0,current_occupancy-1) WHERE shelter_id=OLD.shelter_id;
 END;
CREATE TRIGGER IF NOT EXISTS allocation_reassigns_shelter
 AFTER UPDATE OF status,shelter_id ON shelter_allocation
 WHEN NEW.status='Active' AND NEW.shelter_id IS NOT NULL
  AND (OLD.status!='Active' OR OLD.shelter_id IS NOT NEW.shelter_id)
 BEGIN
  UPDATE shelter SET current_occupancy=current_occupancy+1 WHERE shelter_id=NEW.shelter_id;
 END;
CREATE TRIGGER IF NOT EXISTS allocation_delete_releases_shelter
 AFTER DELETE ON shelter_allocation WHEN OLD.status='Active' AND OLD.shelter_id IS NOT NULL
 BEGIN
  UPDATE shelter SET current_occupancy=MAX(0,current_occupancy-1) WHERE shelter_id=OLD.shelter_id;
 END;
CREATE TRIGGER IF NOT EXISTS allocation_checks_updated_capacity
 BEFORE UPDATE OF status,shelter_id ON shelter_allocation
 WHEN NEW.status='Active' AND NEW.shelter_id IS NOT NULL
  AND (OLD.status!='Active' OR OLD.shelter_id IS NOT NEW.shelter_id)
 BEGIN
  SELECT CASE WHEN NOT EXISTS (
   SELECT 1 FROM shelter WHERE shelter_id=NEW.shelter_id AND status!='Closed'
    AND (current_occupancy<capacity OR shelter_id=OLD.shelter_id)
  ) THEN RAISE(ABORT,'Shelter is closed or has no available spaces.') END;
 END;
CREATE TRIGGER IF NOT EXISTS distribution_checks_stock
 BEFORE INSERT ON supply_distribution
 BEGIN
  SELECT CASE WHEN NOT EXISTS (
   SELECT 1 FROM inventory WHERE resource_id=NEW.resource_id
    AND quantity_available>=NEW.quantity_distributed
  ) THEN RAISE(ABORT,'Insufficient inventory for this distribution.') END;
 END;
CREATE TRIGGER IF NOT EXISTS distribution_decrements_inventory
 AFTER INSERT ON supply_distribution
 BEGIN
  UPDATE inventory SET quantity_available=quantity_available-NEW.quantity_distributed,
                       last_updated=datetime('now')
  WHERE resource_id=NEW.resource_id
    AND inventory_id=(SELECT inventory_id FROM inventory WHERE resource_id=NEW.resource_id
                      ORDER BY inventory_id LIMIT 1);
 END;
 CREATE TRIGGER IF NOT EXISTS distribution_checks_updated_stock
 BEFORE UPDATE OF resource_id,quantity_distributed ON supply_distribution
 BEGIN
  SELECT CASE WHEN NOT EXISTS (
   SELECT 1 FROM inventory WHERE resource_id=NEW.resource_id
    AND quantity_available + CASE WHEN resource_id=OLD.resource_id THEN OLD.quantity_distributed ELSE 0 END
        >= NEW.quantity_distributed
  ) THEN RAISE(ABORT,'Insufficient inventory for this distribution.') END;
 END;
 CREATE TRIGGER IF NOT EXISTS distribution_updates_inventory
 AFTER UPDATE OF resource_id,quantity_distributed ON supply_distribution
 BEGIN
  UPDATE inventory SET quantity_available=quantity_available+OLD.quantity_distributed,last_updated=datetime('now')
   WHERE resource_id=OLD.resource_id
    AND inventory_id=(SELECT inventory_id FROM inventory WHERE resource_id=OLD.resource_id ORDER BY inventory_id LIMIT 1);
  UPDATE inventory SET quantity_available=quantity_available-NEW.quantity_distributed,last_updated=datetime('now')
   WHERE resource_id=NEW.resource_id
    AND inventory_id=(SELECT inventory_id FROM inventory WHERE resource_id=NEW.resource_id ORDER BY inventory_id LIMIT 1);
 END;
 CREATE TRIGGER IF NOT EXISTS distribution_delete_restores_inventory
 AFTER DELETE ON supply_distribution
 BEGIN
  UPDATE inventory SET quantity_available=quantity_available+OLD.quantity_distributed,last_updated=datetime('now')
   WHERE resource_id=OLD.resource_id
    AND inventory_id=(SELECT inventory_id FROM inventory WHERE resource_id=OLD.resource_id ORDER BY inventory_id LIMIT 1);
 END;
"""

REQUIRED = {
    "disasters": ("disaster_name",),
    "affected_areas": ("area_name", "location"),
    "affected_people": ("person_name",),
    "relief_requests": ("request_type",),
    "medical_requests": ("medical_issue",),
    "shelters": ("shelter_name", "location", "capacity"),
    "shelter_allocations": ("person_id", "shelter_id"),
    "resources": ("resource_name", "resource_type"),
    "inventory": ("resource_id",),
    "supply_distributions": ("resource_id", "quantity_distributed"),
    "rescue_teams": ("team_name",),
    "vehicles": ("vehicle_type", "registration_no"),
}
NUMBERS = {"age", "people_affected", "quantity_needed", "capacity", "current_occupancy",
           "resource_id", "area_id", "person_id", "shelter_id", "team_id", "to_shelter_id",
           "to_area_id", "quantity_available", "quantity_distributed"}
OPTIONAL_IDS = {"disaster_id", "area_id", "person_id", "resource_id", "shelter_id",
                "team_id", "to_shelter_id", "to_area_id"}
LINKED_FIELDS = {
    "disaster_id": ("disaster", "disaster_id", "disaster_name"),
    "area_id": ("area", "area_id", "area_name"),
    "person_id": ("person", "person_id", "person_name"),
    "resource_id": ("resource", "resource_id", "resource_name"),
    "shelter_id": ("shelter", "shelter_id", "shelter_name"),
    "to_shelter_id": ("shelter", "shelter_id", "shelter_name"),
    "team_id": ("team", "team_id", "team_name"),
}
DEFAULTS = {
    "disasters": {"disaster_type": "Other", "severity": "Moderate", "status": "Active", "description": ""},
    "affected_areas": {"people_affected": 0, "priority_level": "Medium"},
    "affected_people": {"gender": "Not specified", "contact_no": "", "address": "",
                        "need_type": "General assistance", "priority": "Medium"},
    "relief_requests": {"quantity_needed": 1, "priority": "Medium", "status": "Pending", "remarks": ""},
    "medical_requests": {"priority": "Medium", "status": "Pending", "assigned_to": "", "notes": ""},
    "shelters": {"current_occupancy": 0, "shelter_type": "Relief shelter", "contact_no": "", "status": "Open"},
    "shelter_allocations": {"status": "Active", "remarks": ""},
    "resources": {"unit": "units"},
    "inventory": {"quantity_available": 0, "location": ""},
    "supply_distributions": {"distributed_by": "", "remarks": ""},
    "rescue_teams": {"team_type": "General response", "team_leader": "", "contact_no": "", "status": "Available"},
    "vehicles": {"team_id": None, "capacity": 1, "status": "Available", "current_location": ""},
}


@contextmanager
def connect():
    db = sqlite3.connect(DATABASE, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize_database() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript(SCHEMA)
        import_project_data(db)


def mongo_field_reports():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _mongo_client[MONGODB_DATABASE]["field_reports"]


def _find_or_insert(
    db: sqlite3.Connection,
    table: str,
    primary_key: str,
    signature: dict[str, object],
    values: dict[str, object],
) -> int:
    conditions = " AND ".join(f"lower({column})=lower(?)" if isinstance(value, str) else f"{column} IS ?"
                              for column, value in signature.items())
    row = db.execute(
        f"SELECT {primary_key} FROM {table} WHERE {conditions} ORDER BY {primary_key} LIMIT 1",
        list(signature.values()),
    ).fetchone()
    if row:
        return int(row[primary_key])
    columns = list(values)
    cursor = db.execute(
        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
        list(values.values()),
    )
    return int(cursor.lastrowid)


def import_project_data(db: sqlite3.Connection) -> None:
    """Idempotently load the documented SQL sample rows without replacing local records."""
    disaster_ids: dict[int, int] = {}
    for source_id, name, kind, start, end, severity, status, description in project_data.DISASTERS:
        disaster_ids[source_id] = _find_or_insert(
            db, "disaster", "disaster_id", {"disaster_name": name},
            {"disaster_name": name, "disaster_type": kind, "start_date": start, "end_date": end,
             "severity": "Moderate" if severity == "Medium" else severity,
             "status": "Resolved" if status == "Closed" else status,
             "description": description},
        )

    area_ids: dict[int, int] = {}
    for source_id, source_disaster_id, name, location, people, priority in project_data.AREAS:
        area_ids[source_id] = _find_or_insert(
            db, "affected_area", "area_id", {"area_name": name, "location": location},
            {"disaster_id": disaster_ids[source_disaster_id], "area_name": name, "location": location,
             "people_affected": people, "priority_level": priority},
        )

    person_ids: dict[int, int] = {}
    for source_id, source_area_id, name, age, gender, contact, address, need, priority in project_data.PEOPLE:
        person_ids[source_id] = _find_or_insert(
            db, "affected_person", "person_id", {"person_name": name, "contact_no": contact},
            {"area_id": area_ids[source_area_id], "person_name": name, "age": age, "gender": gender,
             "contact_no": contact, "address": address, "need_type": need, "priority": priority},
        )

    resource_ids: dict[int, int] = {}
    for source_id, name, kind, unit in project_data.RESOURCES:
        resource_ids[source_id] = _find_or_insert(
            db, "resource", "resource_id", {"resource_name": name, "resource_type": kind},
            {"resource_name": name, "resource_type": kind, "unit": unit},
        )

    allocation_counts: dict[int, int] = {}
    for _, _, source_shelter_id, _, status, _ in project_data.ALLOCATIONS:
        if status == "Allocated":
            allocation_counts[source_shelter_id] = allocation_counts.get(source_shelter_id, 0) + 1
    shelter_ids: dict[int, int] = {}
    for source_id, name, location, capacity, occupancy, kind, contact, status in project_data.SHELTERS:
        shelter_ids[source_id] = _find_or_insert(
            db, "shelter", "shelter_id", {"shelter_name": name, "location": location},
            {"shelter_name": name, "location": location, "capacity": capacity,
             "current_occupancy": max(0, occupancy - allocation_counts.get(source_id, 0)),
             "shelter_type": kind, "contact_no": contact,
             "status": "Open" if status == "Active" else status},
        )

    team_ids: dict[int, int] = {}
    for source_id, name, kind, leader, contact, status in project_data.RESCUE_TEAMS:
        team_ids[source_id] = _find_or_insert(
            db, "rescue_team", "team_id", {"team_name": name},
            {"team_name": name, "team_type": kind, "team_leader": leader, "contact_no": contact,
             "status": "Available" if status == "Active" else status},
        )

    for _, source_resource_id, quantity, updated, location in project_data.INVENTORY:
        _find_or_insert(
            db, "inventory", "inventory_id", {"resource_id": resource_ids[source_resource_id], "location": location},
            {"resource_id": resource_ids[source_resource_id], "quantity_available": quantity,
             "last_updated": updated, "location": location},
        )

    for _, source_person_id, source_shelter_id, allocated, status, remarks in project_data.ALLOCATIONS:
        person_id, shelter_id = person_ids[source_person_id], shelter_ids[source_shelter_id]
        _find_or_insert(
            db, "shelter_allocation", "allocation_id",
            {"person_id": person_id, "shelter_id": shelter_id, "allocation_date": allocated},
            {"person_id": person_id, "shelter_id": shelter_id, "allocation_date": allocated,
             "status": "Active" if status == "Allocated" else status, "remarks": remarks},
        )

    for _, source_area_id, source_person_id, source_resource_id, request, quantity, priority, requested, status, remarks in project_data.RELIEF_REQUESTS:
        _find_or_insert(
            db, "relief_request", "request_id",
            {"person_id": person_ids[source_person_id], "request_type": request, "request_date": requested},
            {"area_id": area_ids[source_area_id], "person_id": person_ids[source_person_id],
             "request_type": request, "resource_id": resource_ids[source_resource_id],
             "quantity_needed": quantity, "priority": priority, "request_date": requested,
             "status": "Fulfilled" if status == "Completed" else status, "remarks": remarks},
        )

    for _, source_person_id, issue, priority, requested, status, assigned in project_data.MEDICAL_REQUESTS:
        _find_or_insert(
            db, "medical_request", "medical_req_id",
            {"person_id": person_ids[source_person_id], "medical_issue": issue, "request_date": requested},
            {"person_id": person_ids[source_person_id], "medical_issue": issue, "priority": priority,
             "request_date": requested, "status": status, "assigned_to": assigned, "notes": ""},
        )

    db.execute("DROP TRIGGER IF EXISTS distribution_checks_stock")
    db.execute("DROP TRIGGER IF EXISTS distribution_decrements_inventory")
    try:
        for _, source_resource_id, source_shelter_id, source_area_id, quantity, delivered, team, remarks in project_data.DISTRIBUTIONS:
            resource_id, shelter_id = resource_ids[source_resource_id], shelter_ids[source_shelter_id]
            area_id = area_ids[source_area_id]
            _find_or_insert(
                db, "supply_distribution", "distribution_id",
                {"resource_id": resource_id, "to_shelter_id": shelter_id, "to_area_id": area_id,
                 "distribution_date": delivered, "quantity_distributed": quantity},
                {"resource_id": resource_id, "to_shelter_id": shelter_id, "to_area_id": area_id,
                 "quantity_distributed": quantity, "distribution_date": delivered,
                 "distributed_by": team, "remarks": remarks},
            )
    finally:
        db.execute("""
        CREATE TRIGGER IF NOT EXISTS distribution_checks_stock
         BEFORE INSERT ON supply_distribution
         BEGIN
          SELECT CASE WHEN NOT EXISTS (
           SELECT 1 FROM inventory WHERE resource_id=NEW.resource_id
            AND quantity_available>=NEW.quantity_distributed
          ) THEN RAISE(ABORT,'Insufficient inventory for this distribution.') END;
         END
        """)
        db.execute("""
        CREATE TRIGGER IF NOT EXISTS distribution_decrements_inventory
         AFTER INSERT ON supply_distribution
         BEGIN
          UPDATE inventory SET quantity_available=quantity_available-NEW.quantity_distributed,
                               last_updated=datetime('now')
          WHERE resource_id=NEW.resource_id
            AND inventory_id=(SELECT inventory_id FROM inventory WHERE resource_id=NEW.resource_id
                              ORDER BY inventory_id LIMIT 1);
         END
        """)

    for _, source_team_id, kind, registration, capacity, status, location in project_data.VEHICLES:
        _find_or_insert(
            db, "vehicle", "vehicle_id", {"registration_no": registration},
            {"team_id": team_ids[source_team_id], "vehicle_type": kind, "registration_no": registration,
             "capacity": capacity, "status": "In use" if status == "In Use" else status,
             "current_location": location},
        )


def as_dict(row: sqlite3.Row) -> dict:
    return dict(row)


class APIError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


class ReliefHandler(BaseHTTPRequestHandler):
    server_version = "ReliefFlow/1.0"

    def send_json(self, status: int, value: object) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                raise APIError(413, "Request body exceeds 1 MB.")
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            raise APIError(400, "Request body must be valid JSON.") from None
        if not isinstance(payload, dict):
            raise APIError(400, "Expected a JSON object.")
        return payload

    def handle_api(self, method: str, path: str) -> None:
        if path == "/api/field_reports" or path.startswith("/api/field_reports/"):
            self.handle_field_reports(method, path)
            return
        if path == "/api/dashboard" and method == "GET":
            with connect() as db:
                metrics = {
                    "active_disasters": db.execute("SELECT COUNT(*) FROM disaster WHERE status!='Resolved'").fetchone()[0],
                    "affected_people": db.execute("SELECT COUNT(*) FROM affected_person").fetchone()[0],
                    "pending_relief": db.execute("SELECT COUNT(*) FROM relief_request WHERE status='Pending'").fetchone()[0],
                    "medical_requests": db.execute("SELECT COUNT(*) FROM medical_request WHERE status!='Completed'").fetchone()[0],
                    "available_shelter_spaces": db.execute("SELECT COALESCE(SUM(spaces_available),0) FROM shelter_availability WHERE status='Open'").fetchone()[0],
                    "inventory_items": db.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
                }
                disasters = db.execute(
                    """SELECT d.disaster_id,d.disaster_name,d.disaster_type,d.severity,d.status,d.start_date,
                              COUNT(DISTINCT a.area_id) AS area_count,
                              COUNT(DISTINCT p.person_id) AS people_count
                       FROM disaster d LEFT JOIN affected_area a ON a.disaster_id=d.disaster_id
                       LEFT JOIN affected_person p ON p.area_id=a.area_id
                       GROUP BY d.disaster_id ORDER BY d.disaster_id DESC LIMIT 6"""
                ).fetchall()
                requests = db.execute(
                    """SELECT rr.request_id,rr.request_type,rr.priority,rr.status,rr.quantity_needed,
                              aa.area_name,ap.person_name
                       FROM relief_request rr LEFT JOIN affected_area aa ON aa.area_id=rr.area_id
                       LEFT JOIN affected_person ap ON ap.person_id=rr.person_id
                       ORDER BY CASE rr.priority WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 ELSE 2 END,
                                rr.request_id DESC LIMIT 5"""
                ).fetchall()
            self.send_json(200, {"metrics": metrics, "disasters": [as_dict(row) for row in disasters],
                                 "urgent_requests": [as_dict(row) for row in requests]})
            return
        match = re.fullmatch(r"/api/([a-z_]+)(?:/(\d+))?", path)
        if not match or match.group(1) not in ENTITIES:
            raise APIError(404, "API endpoint not found.")
        key, record_id = match.groups()
        table, pk, fields = ENTITIES[key]
        with connect() as db:
            if method == "GET":
                if record_id:
                    row = db.execute(f"SELECT * FROM {table} WHERE {pk}=?", (int(record_id),)).fetchone()
                    if row is None:
                        raise APIError(404, "Record not found.")
                    self.send_json(200, as_dict(row))
                else:
                    rows = db.execute(f"SELECT * FROM {table} ORDER BY {pk} DESC").fetchall()
                    self.send_json(200, [as_dict(row) for row in rows])
                return
            if method == "DELETE":
                if not record_id:
                    raise APIError(405, "Provide a record ID to delete.")
                cursor = db.execute(f"DELETE FROM {table} WHERE {pk}=?", (int(record_id),))
                if cursor.rowcount == 0:
                    raise APIError(404, "Record not found.")
                self.send_json(200, {"message": "Record deleted."})
                return
            if method not in ("POST", "PUT"):
                raise APIError(405, "Method not allowed.")
            if method == "PUT" and not record_id:
                raise APIError(405, "Provide a record ID to update.")
            payload = self.read_json()
            if method == "POST":
                values = {**DEFAULTS.get(key, {}), **payload}
            else:
                existing = db.execute(f"SELECT * FROM {table} WHERE {pk}=?", (int(record_id),)).fetchone()
                if not existing:
                    raise APIError(404, "Record not found.")
                values = {**dict(existing), **payload}
            values = {
                field: self.resolve_link(db, field, values[field])
                for field in fields
                if field in values
            }
            missing = [field for field in REQUIRED[key]
                       if method == "POST" and (values.get(field) is None or values.get(field) == "")]
            if missing:
                raise APIError(400, f"Required field: {missing[0].replace('_', ' ')}.")
            if key == "shelter_allocations" and method == "POST":
                shelter = db.execute("SELECT capacity,current_occupancy,status FROM shelter WHERE shelter_id=?",
                                     (values.get("shelter_id"),)).fetchone()
                if shelter is None:
                    raise APIError(400, "Choose an existing shelter.")
                if shelter["status"] == "Closed" or shelter["current_occupancy"] >= shelter["capacity"]:
                    raise APIError(400, "This shelter is closed or has no available spaces.")
            if key == "supply_distributions" and method == "POST":
                stock = db.execute("SELECT quantity_available FROM inventory WHERE resource_id=? ORDER BY inventory_id LIMIT 1",
                                   (values["resource_id"],)).fetchone()
                if stock is None or stock["quantity_available"] < values["quantity_distributed"]:
                    raise APIError(400, "Insufficient inventory for this distribution.")
            if key == "supply_distributions" and method == "PUT":
                old = db.execute("SELECT resource_id,quantity_distributed FROM supply_distribution WHERE distribution_id=?",
                                 (int(record_id),)).fetchone()
                stock = db.execute("SELECT quantity_available FROM inventory WHERE resource_id=? ORDER BY inventory_id LIMIT 1",
                                   (values["resource_id"],)).fetchone()
                available = stock["quantity_available"] if stock else 0
                if old["resource_id"] == values["resource_id"]:
                    available += old["quantity_distributed"]
                if stock is None or available < values["quantity_distributed"]:
                    raise APIError(400, "Insufficient inventory for this distribution.")
            try:
                if method == "POST":
                    columns = list(values)
                    cursor = db.execute(
                        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                        [values[field] for field in columns],
                    )
                    new_id = cursor.lastrowid
                else:
                    changed = {field: values[field] for field in fields if field in payload}
                    if not changed:
                        raise APIError(400, "Provide at least one field to update.")
                    assignments = ",".join(f"{field}=?" for field in changed)
                    db.execute(f"UPDATE {table} SET {assignments} WHERE {pk}=?",
                               [*changed.values(), int(record_id)])
                    new_id = int(record_id)
                row = db.execute(f"SELECT * FROM {table} WHERE {pk}=?", (new_id,)).fetchone()
            except sqlite3.IntegrityError as exc:
                raise APIError(400, f"Could not save record: {exc}") from None
            self.send_json(201 if method == "POST" else 200, as_dict(row))

    def handle_field_reports(self, method: str, path: str) -> None:
        match = re.fullmatch(r"/api/field_reports(?:/([^/]+))?", path)
        if not match:
            raise APIError(404, "API endpoint not found.")
        raw_id = match.group(1)
        report_id = None
        if raw_id:
            if not ObjectId.is_valid(raw_id):
                raise APIError(400, "Field report ID must be a valid MongoDB ObjectId.")
            report_id = ObjectId(raw_id)

        collection = mongo_field_reports()
        if method == "GET":
            if report_id:
                report = collection.find_one({"_id": report_id})
                if report is None:
                    raise APIError(404, "Field report not found.")
                self.send_json(200, self.serialize_report(report))
            else:
                reports = collection.find().sort("reported_at", -1).limit(500)
                self.send_json(200, [self.serialize_report(report) for report in reports])
            return
        if method == "DELETE":
            if report_id is None:
                raise APIError(405, "Provide a field report ID to delete.")
            if collection.delete_one({"_id": report_id}).deleted_count == 0:
                raise APIError(404, "Field report not found.")
            self.send_json(200, {"message": "Field report deleted."})
            return
        if method not in ("POST", "PUT"):
            raise APIError(405, "Method not allowed.")
        if method == "PUT" and report_id is None:
            raise APIError(405, "Provide a field report ID to update.")

        payload = self.read_json()
        allowed = {"disaster_name", "location", "report_type", "details", "reported_by",
                   "reported_at", "status", "extra_fields"}
        unsupported = set(payload) - allowed
        if unsupported:
            raise APIError(400, f"Unsupported field: {sorted(unsupported)[0]}.")
        existing = collection.find_one({"_id": report_id}) if report_id else None
        if method == "PUT" and existing is None:
            raise APIError(404, "Field report not found.")
        report = self.clean_report(payload, existing, method == "POST")
        if method == "POST":
            result = collection.insert_one(report)
            report["_id"] = result.inserted_id
        else:
            collection.update_one({"_id": report_id}, {"$set": report})
            report["_id"] = report_id
        self.send_json(201 if method == "POST" else 200, self.serialize_report(report))

    @staticmethod
    def clean_report(payload: dict, existing: dict | None, creating: bool) -> dict:
        values = {
            "disaster_name": "",
            "location": "",
            "report_type": "",
            "details": "",
            "reported_by": "",
            "reported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "New",
            "extra_fields": {},
        }
        if existing:
            values.update({key: value for key, value in existing.items() if key != "_id"})
        values.update(payload)
        for field in ("disaster_name", "location", "report_type", "details", "reported_by", "reported_at"):
            value = values[field]
            if not isinstance(value, str):
                raise APIError(400, f"{field.replace('_', ' ').title()} must be text.")
            values[field] = value.strip()
            if len(values[field]) > 4000:
                raise APIError(400, f"{field.replace('_', ' ').title()} is too long.")
        for field in ("location", "report_type", "details"):
            if not values[field]:
                raise APIError(400, f"Required field: {field.replace('_', ' ')}.")
        if values["status"] not in ("New", "Verified", "Resolved"):
            raise APIError(400, "Status must be New, Verified, or Resolved.")
        if not isinstance(values["extra_fields"], dict):
            raise APIError(400, "Additional fields must be a JSON object.")
        ReliefHandler.validate_mongo_fields(values["extra_fields"])
        return values

    @staticmethod
    def validate_mongo_fields(value: object) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if not isinstance(key, str) or not key or "." in key or key.startswith("$"):
                    raise APIError(400, "Additional field names cannot be empty or contain '.' or start with '$'.")
                ReliefHandler.validate_mongo_fields(nested)
        elif isinstance(value, list):
            for nested in value:
                ReliefHandler.validate_mongo_fields(nested)
        elif isinstance(value, float) and not math.isfinite(value):
            raise APIError(400, "Additional fields cannot contain non-finite numbers.")
        elif isinstance(value, int) and not isinstance(value, bool) and not -(2**63) <= value < 2**63:
            raise APIError(400, "Additional field numbers must fit in a signed 64-bit integer.")
        elif not isinstance(value, (str, int, float, bool, type(None))):
            raise APIError(400, "Additional fields must contain JSON-compatible values.")

    @staticmethod
    def serialize_report(report: dict) -> dict:
        return {**report, "_id": str(report["_id"])}

    @staticmethod
    def clean_value(field: str, value: object) -> object:
        if value == "" and field in OPTIONAL_IDS:
            return None
        if value == "" and field in NUMBERS:
            return None
        if field in NUMBERS and value is not None:
            try:
                number = float(value)
                return int(number) if number.is_integer() else number
            except (TypeError, ValueError):
                raise APIError(400, f"{field.replace('_', ' ').title()} must be a number.") from None
        if isinstance(value, str):
            value = value.strip()
            if len(value) > 4000:
                raise APIError(400, f"{field.replace('_', ' ').title()} is too long.")
        return value

    @staticmethod
    def resolve_link(db: sqlite3.Connection, field: str, value: object) -> object:
        if field not in LINKED_FIELDS or not isinstance(value, str) or not value.strip():
            return ReliefHandler.clean_value(field, value)
        name = value.strip()
        try:
            return int(name)
        except ValueError:
            pass

        link_type, primary_key, label_field = LINKED_FIELDS[field]
        table = {
            "disaster": "disaster",
            "area": "affected_area",
            "person": "affected_person",
            "resource": "resource",
            "shelter": "shelter",
            "team": "rescue_team",
        }[link_type]
        existing = db.execute(
            f"SELECT {primary_key} FROM {table} WHERE lower({label_field})=lower(?) ORDER BY {primary_key} LIMIT 1",
            (name,),
        ).fetchone()
        if existing:
            return existing[primary_key]

        new_record = {
            "disaster": ("disaster", {"disaster_name": name, "disaster_type": "Other"}),
            "area": ("affected_area", {"area_name": name, "location": name, "people_affected": 0}),
            "person": ("affected_person", {"person_name": name, "need_type": "General assistance"}),
            "resource": ("resource", {"resource_name": name, "resource_type": "Other", "unit": "units"}),
            "shelter": ("shelter", {
                "shelter_name": name, "location": name, "capacity": 100,
                "current_occupancy": 0, "shelter_type": "Relief shelter",
            }),
            "team": ("rescue_team", {"team_name": name, "team_type": "General response"}),
        }[link_type]
        columns = list(new_record[1])
        cursor = db.execute(
            f"INSERT INTO {new_record[0]} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            [new_record[1][column] for column in columns],
        )
        return cursor.lastrowid

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            try:
                self.handle_api("GET", path)
            except APIError as exc:
                self.send_json(exc.status, {"error": str(exc)})
            except sqlite3.Error:
                self.send_json(500, {"error": "A database error occurred."})
            except PyMongoError:
                self.send_json(503, {"error": "MongoDB is unavailable. Start MongoDB and verify MONGODB_URI."})
            return
        self.serve_static(path)

    def do_POST(self) -> None:
        self.run_api("POST")

    def do_PUT(self) -> None:
        self.run_api("PUT")

    def do_DELETE(self) -> None:
        self.run_api("DELETE")

    def run_api(self, method: str) -> None:
        try:
            self.handle_api(method, urlparse(self.path).path)
        except APIError as exc:
            self.send_json(exc.status, {"error": str(exc)})
        except sqlite3.Error:
            self.send_json(500, {"error": "A database error occurred."})
        except PyMongoError:
            self.send_json(503, {"error": "MongoDB is unavailable. Start MongoDB and verify MONGODB_URI."})

    def serve_static(self, path: str) -> None:
        relative = unquote(path.lstrip("/")) or "index.html"
        target = (STATIC / relative).resolve()
        if not target.is_relative_to(STATIC.resolve()) or not target.is_file():
            self.send_error(404)
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    initialize_database()
    print(f"ReliefFlow is running at http://localhost:{PORT}")
    try:
        ThreadingHTTPServer((HOST, PORT), ReliefHandler).serve_forever()
    except KeyboardInterrupt:
        print("\nReliefFlow stopped.")
    finally:
        if _mongo_client is not None:
            _mongo_client.close()
