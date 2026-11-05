import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import app
from pymongo.errors import ServerSelectionTimeoutError


class FakeMongoCursor:
    def __init__(self, reports):
        self.reports = reports

    def sort(self, field, direction):
        self.reports.sort(key=lambda report: report[field], reverse=direction < 0)
        return self

    def limit(self, count):
        self.reports = self.reports[:count]
        return self

    def __iter__(self):
        return iter(self.reports)


class FakeMongoCollection:
    def __init__(self):
        self.reports = []

    def find(self):
        return FakeMongoCursor([dict(report) for report in self.reports])

    def find_one(self, query):
        return next((dict(report) for report in self.reports if report["_id"] == query["_id"]), None)

    def insert_one(self, report):
        from bson import ObjectId

        report["_id"] = ObjectId()
        self.reports.append(dict(report))
        return type("InsertResult", (), {"inserted_id": report["_id"]})()

    def update_one(self, query, update):
        for report in self.reports:
            if report["_id"] == query["_id"]:
                report.update(update["$set"])
                return

    def delete_one(self, query):
        previous_count = len(self.reports)
        self.reports = [report for report in self.reports if report["_id"] != query["_id"]]
        return type("DeleteResult", (), {"deleted_count": previous_count - len(self.reports)})()


class ReliefApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.db_patch = patch.object(app, "DATABASE", Path(cls.tempdir.name) / "test.db")
        cls.db_patch.start()
        app.initialize_database()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.ReliefHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.db_patch.stop()
        cls.tempdir.cleanup()

    def setUp(self):
        app.DATABASE = Path(self.tempdir.name) / f"{self._testMethodName}.db"
        app.initialize_database()
        app.create_user("test-admin@example.com", "test-admin-password-12", "Administrator")
        self.cookie = None
        self.request("/api/auth/login", "POST", {
            "email": "test-admin@example.com", "password": "test-admin-password-12",
        })

    def request(self, path, method="GET", body=None):
        request = self.make_request(path, method, body)
        with urlopen(request) as response:
            set_cookie = response.headers.get("Set-Cookie")
            if set_cookie:
                self.cookie = set_cookie.split(";", 1)[0]
            return response.status, json.loads(response.read())

    def make_request(self, path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
        if self.cookie:
            headers["Cookie"] = self.cookie
        return Request(self.base + path, data=data, method=method, headers=headers)

    def test_authentication_and_database_role_permissions(self):
        admin_cookie = self.cookie
        status, user = self.request("/api/auth/me")
        self.assertEqual(status, 200)
        self.assertEqual(user["user"]["role"], "Administrator")

        with app.connect() as db:
            row = db.execute("SELECT password_hash FROM app_user WHERE username='test-admin@example.com'").fetchone()
        self.assertNotIn("test-admin-password-12", row["password_hash"])
        self.assertTrue(row["password_hash"].startswith("pbkdf2_sha256$"))

        coordinator = self.request("/api/users", "POST", {
            "email": "test-coordinator@example.com",
            "password": "test-coordinator-password-12",
            "role": "Coordinator",
        })[1]
        self.assertEqual(
            self.request(f"/api/users/{coordinator['user_id']}/password", "PUT",
                         {"password": "new-coordinator-password-12"})[0],
            200,
        )
        self.cookie = None
        with self.assertRaises(HTTPError) as error:
            self.request("/api/dashboard")
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

        status, _ = self.request("/api/auth/login", "POST", {
            "email": "test-coordinator@example.com", "password": "new-coordinator-password-12",
        })
        self.assertEqual(status, 200)
        self.assertEqual(self.request("/api/auth/me")[1]["user"]["role"], "Coordinator")
        self.assertEqual(self.request("/api/disasters")[0], 200)

        with self.assertRaises(HTTPError) as error:
            self.request("/api/users")
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

        first_disaster = self.request("/api/disasters")[1][0]
        self.assertEqual(
            self.request(f"/api/disasters/{first_disaster['disaster_id']}", "PUT",
                         {"description": "Coordinator update"})[0],
            200,
        )
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/disasters/{first_disaster['disaster_id']}", "DELETE")
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

        self.cookie = admin_cookie
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/users/{user['user']['user_id']}/password", "PUT",
                         {"password": "new-admin-password-12"})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

        with self.assertRaises(HTTPError) as error:
            self.request("/api/auth/login", "POST", {
                "email": "test-coordinator@example.com", "password": "test-coordinator-password-12",
            })
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

        with self.assertRaises(HTTPError) as error:
            self.request("/api/auth/login", "POST", {
                "email": "test-admin@example.com", "password": "wrong-password-000",
            })
        self.assertEqual(error.exception.code, 401)
        error.exception.close()

    def test_self_registration_bootstraps_admin_then_coordinator(self):
        with app.connect() as db:
            db.execute("DELETE FROM auth_session")
            db.execute("DELETE FROM app_user")
        status, first = self.request("/api/auth/register", "POST", {
            "email": "First-Admin@Example.com", "password": "first-admin-password-12",
        })
        self.assertEqual(status, 201)
        self.assertEqual(first["user"]["role"], "Administrator")
        self.assertEqual(self.request("/api/auth/me")[1]["user"]["email"], "first-admin@example.com")

        status, second = self.request("/api/auth/register", "POST", {
            "email": "second-coordinator@example.com", "password": "second-coordinator-password-12",
        })
        self.assertEqual(status, 201)
        self.assertEqual(second["user"]["role"], "Coordinator")
        self.request("/api/auth/login", "POST", {
            "email": "FIRST-ADMIN@EXAMPLE.COM", "password": "first-admin-password-12",
        })
        self.assertEqual(self.request("/api/users")[0], 200)

        with self.assertRaises(HTTPError) as error:
            self.request("/api/auth/register", "POST", {
                "email": "first-admin@example.com", "password": "another-password-123",
            })
        self.assertEqual(error.exception.code, 409)
        error.exception.close()

        with self.assertRaises(HTTPError) as error:
            self.request("/api/auth/register", "POST", {
                "email": "not-an-email", "password": "long-enough-password-12",
            })
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

        with self.assertRaises(HTTPError) as error:
            self.request("/api/auth/register", "POST", {
                "email": "short-password@example.com", "password": "short",
            })
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_schema_dashboard_and_static_frontend(self):
        status, dashboard = self.request("/api/dashboard")
        self.assertEqual(status, 200)
        self.assertEqual(dashboard["metrics"]["active_disasters"], 3)
        self.assertEqual(dashboard["metrics"]["affected_people"], 10)
        self.assertEqual(dashboard["metrics"]["available_shelter_spaces"], 1180)
        for path in ("/", "/styles.css", "/app.js"):
            with urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                contents = response.read()
                self.assertGreater(len(contents), 100)
                if path == "/app.js":
                    self.assertIn(b"timeZone:\"Asia/Kolkata\"", contents)
                    self.assertIn(b"Date &amp; time (IST)", contents)
                    for label, number in ((b"National emergency", b"112"),
                                          (b"Ambulance", b"108"),
                                          (b"Fire services", b"101"),
                                          (b"RELIEF TEAM EMERGENCY CONTACT", b"656565")):
                        self.assertIn(label, contents)
                        self.assertIn(f"tel:{number.decode()}".encode(), contents)
                if path == "/styles.css":
                    self.assertIn(b"@keyframes relief-contact-scroll", contents)
        with app.connect() as db:
            tables = {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            for table, expected in {
                "disaster": 5, "affected_area": 10, "affected_person": 10, "resource": 6,
                "inventory": 6, "shelter": 6, "shelter_allocation": 8, "relief_request": 10,
                "medical_request": 8, "supply_distribution": 8, "rescue_team": 5, "vehicle": 6,
            }.items():
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], expected)
        self.assertTrue(set(table for table, _, _ in app.ENTITIES.values()).issubset(tables))
        app.initialize_database()
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM disaster").fetchone()[0], 5)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM affected_area").fetchone()[0], 10)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM shelter_allocation").fetchone()[0], 8)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM supply_distribution").fetchone()[0], 8)

    def test_resident_create_update_delete_flow(self):
        area_id = self.request("/api/affected_areas")[1][0]["area_id"]
        status, resident = self.request("/api/affected_people", "POST", {
            "area_id": area_id, "person_name": "Test Resident", "age": 31,
            "gender": "Female", "contact_no": "555-0199", "address": "North",
            "need_type": "Food", "priority": "High",
        })
        self.assertEqual(status, 201)
        person_id = resident["person_id"]
        self.assertEqual(self.request(f"/api/affected_people/{person_id}", "PUT", {"priority": "Low"})[1]["priority"], "Low")
        self.assertEqual(self.request("/api/affected_people")[1][0]["person_name"], "Test Resident")
        self.assertEqual(self.request(f"/api/affected_people/{person_id}", "DELETE")[0], 200)
        with self.assertRaises(HTTPError) as error:
            self.request(f"/api/affected_people/{person_id}")
        self.assertEqual(error.exception.code, 404)
        error.exception.close()

    def test_typed_link_creates_or_reuses_related_record(self):
        status, first = self.request("/api/affected_people", "POST", {
            "area_id": "New typed area", "person_name": "Typed link test",
            "need_type": "Shelter",
        })
        self.assertEqual(status, 201)
        areas = self.request("/api/affected_areas")[1]
        created_area = next(area for area in areas if area["area_name"] == "New typed area")
        self.assertEqual(created_area["location"], "New typed area")
        self.assertEqual(first["area_id"], created_area["area_id"])

        status, second = self.request("/api/affected_people", "POST", {
            "area_id": "New typed area", "person_name": "Typed link test two",
            "need_type": "Food",
        })
        self.assertEqual(status, 201)
        self.assertEqual(second["area_id"], created_area["area_id"])
        self.assertEqual(
            sum(area["area_name"] == "New typed area" for area in self.request("/api/affected_areas")[1]),
            1,
        )

    def test_failed_parent_record_rolls_back_typed_link(self):
        request = self.make_request("/api/affected_areas", "POST", {
            "disaster_id": "Must not persist", "area_name": "",
        })
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()
        disasters = self.request("/api/disasters")[1]
        self.assertFalse(any(row["disaster_name"] == "Must not persist" for row in disasters))

    def test_shelter_allocation_updates_occupancy_and_release(self):
        person = self.request("/api/affected_people")[1][0]
        shelter = self.request("/api/shelters")[1][0]
        status, allocation = self.request("/api/shelter_allocations", "POST", {
            "person_id": person["person_id"], "shelter_id": shelter["shelter_id"],
        })
        self.assertEqual(status, 201)
        self.assertEqual(
            self.request(f"/api/shelters/{shelter['shelter_id']}")[1]["current_occupancy"],
            shelter["current_occupancy"] + 1,
        )
        self.request(f"/api/shelter_allocations/{allocation['allocation_id']}", "PUT", {"status": "Released"})
        self.assertEqual(
            self.request(f"/api/shelters/{shelter['shelter_id']}")[1]["current_occupancy"],
            shelter["current_occupancy"],
        )
        self.request(f"/api/shelter_allocations/{allocation['allocation_id']}", "DELETE")
        self.assertEqual(
            self.request(f"/api/shelters/{shelter['shelter_id']}")[1]["current_occupancy"],
            shelter["current_occupancy"],
        )

    def test_distribution_decrements_inventory_and_rejects_insufficient_stock(self):
        resource = self.request("/api/resources")[1][0]
        area = self.request("/api/affected_areas")[1][0]
        inventory = self.request("/api/inventory")[1][0]
        self.request("/api/supply_distributions", "POST", {
            "resource_id": resource["resource_id"], "to_area_id": area["area_id"],
            "quantity_distributed": 25,
        })
        self.assertEqual(self.request("/api/inventory")[1][0]["quantity_available"], inventory["quantity_available"] - 25)
        request = self.make_request("/api/supply_distributions", "POST", {
            "resource_id": resource["resource_id"], "to_area_id": area["area_id"],
            "quantity_distributed": 999999,
        })
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_database_rejects_invalid_shelter_occupancy(self):
        request = self.make_request("/api/shelters", "POST", {
            "shelter_name": "Invalid", "location": "Test", "capacity": 5,
            "current_occupancy": 6,
        })
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_create_flow_covers_all_project_entities(self):
        area = self.request("/api/affected_areas")[1][0]
        person = self.request("/api/affected_people")[1][0]
        shelter = self.request("/api/shelters")[1][0]
        resource = self.request("/api/resources")[1][0]
        team = self.request("/api/rescue_teams")[1][0]
        records = {
            "disasters": {"disaster_name": "Test cyclone"},
            "affected_areas": {"area_name": "East sector", "location": "East"},
            "affected_people": {"person_name": "Another resident"},
            "relief_requests": {"area_id": area["area_id"], "person_id": person["person_id"],
                                "request_type": "Drinking water", "resource_id": resource["resource_id"]},
            "medical_requests": {"person_id": person["person_id"], "medical_issue": "First aid"},
            "shelters": {"shelter_name": "East shelter", "location": "East", "capacity": 40},
            "shelter_allocations": {"person_id": person["person_id"], "shelter_id": shelter["shelter_id"]},
            "resources": {"resource_name": "First-aid kit", "resource_type": "Medical"},
            "inventory": {"resource_id": resource["resource_id"], "quantity_available": 10},
            "supply_distributions": {"resource_id": resource["resource_id"], "to_area_id": area["area_id"],
                                     "quantity_distributed": 1},
            "rescue_teams": {"team_name": "East response team"},
            "vehicles": {"team_id": team["team_id"], "vehicle_type": "Ambulance",
                         "registration_no": "TEST-001"},
        }
        for endpoint, payload in records.items():
            with self.subTest(endpoint=endpoint):
                status, result = self.request(f"/api/{endpoint}", "POST", payload)
                self.assertEqual(status, 201)
                primary_key = app.ENTITIES[endpoint][1]
                self.assertIsInstance(result[primary_key], int)

    def test_mongodb_field_report_crud_and_validation(self):
        collection = FakeMongoCollection()
        with patch.object(app, "mongo_field_reports", return_value=collection):
            status, report = self.request("/api/field_reports", "POST", {
                "disaster_name": "Kodagu landslide",
                "location": "Madikeri north road",
                "report_type": "Road blocked",
                "details": "Debris is blocking the road.",
                "reported_by": "Rescue Team A",
                "extra_fields": {"water_level": "2m", "people_needing_help": 12},
            })
            self.assertEqual(status, 201)
            self.assertEqual(report["extra_fields"]["people_needing_help"], 12)
            report_id = report["_id"]

            self.assertEqual(self.request("/api/field_reports")[1][0]["_id"], report_id)
            self.assertEqual(self.request(f"/api/field_reports/{report_id}")[1]["location"],
                             "Madikeri north road")
            updated = self.request(f"/api/field_reports/{report_id}", "PUT", {
                "status": "Verified",
                "extra_fields": {"water_level": "2.5m", "roads_affected": ["north", "east"]},
            })[1]
            self.assertEqual(updated["status"], "Verified")
            self.assertEqual(updated["extra_fields"]["roads_affected"], ["north", "east"])
            self.assertEqual(self.request(f"/api/field_reports/{report_id}", "DELETE")[0], 200)
            self.assertEqual(self.request("/api/field_reports")[1], [])

            request = self.make_request("/api/field_reports", "POST", {
                "location": "Madikeri", "report_type": "Hazard",
                "details": "Unsafe field key.", "extra_fields": {"$where": "bad"},
            })
            with self.assertRaises(HTTPError) as error:
                urlopen(request)
            self.assertEqual(error.exception.code, 400)
            error.exception.close()

    def test_mongodb_unavailable_returns_setup_error(self):
        with patch.object(app, "mongo_field_reports",
                          side_effect=ServerSelectionTimeoutError("MongoDB is not running")):
            with self.assertRaises(HTTPError) as error:
                self.request("/api/field_reports")
            self.assertEqual(error.exception.code, 503)
            self.assertEqual(json.loads(error.exception.read())["error"],
                             "MongoDB is unavailable. Start MongoDB and verify MONGODB_URI.")
            error.exception.close()


if __name__ == "__main__":
    unittest.main()
