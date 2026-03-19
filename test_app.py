"""
test_app.py — pytest test suite for the CodeCraftHub API.

Covers all CRUD endpoints, validation, error handling, and the stats endpoint.
Run with:  pytest test_app.py -v
"""

import json
import os
import pytest
from app import app, COURSES_FILE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def clean_courses_file():
    """Ensure a fresh, empty courses.json before each test and clean up after."""
    if os.path.exists(COURSES_FILE):
        os.remove(COURSES_FILE)
    yield
    if os.path.exists(COURSES_FILE):
        os.remove(COURSES_FILE)


def sample_course(**overrides):
    """Return a valid course payload, with optional field overrides."""
    data = {
        "name": "Python Basics",
        "description": "Learn Python fundamentals",
        "target_date": "2025-12-31",
        "status": "Not Started",
    }
    data.update(overrides)
    return data


# ===========================================================================
# GET / — Welcome
# ===========================================================================

class TestIndex:
    def test_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_returns_welcome_message(self, client):
        body = client.get("/").get_json()
        assert "Welcome" in body["message"]

    def test_lists_endpoints(self, client):
        body = client.get("/").get_json()
        assert "endpoints" in body


# ===========================================================================
# POST /api/courses — Create
# ===========================================================================

class TestCreateCourse:
    def test_create_success(self, client):
        res = client.post("/api/courses", json=sample_course())
        assert res.status_code == 201
        body = res.get_json()
        assert body["id"] == 1
        assert body["name"] == "Python Basics"
        assert body["status"] == "Not Started"
        assert "created_at" in body

    def test_auto_increment_id(self, client):
        client.post("/api/courses", json=sample_course(name="Course A"))
        res = client.post("/api/courses", json=sample_course(name="Course B"))
        assert res.get_json()["id"] == 2

    def test_data_persists_in_json_file(self, client):
        client.post("/api/courses", json=sample_course())
        assert os.path.exists(COURSES_FILE)
        with open(COURSES_FILE) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Python Basics"

    def test_400_missing_name(self, client):
        res = client.post("/api/courses", json=sample_course(name=""))
        assert res.status_code == 400
        assert "name" in res.get_json()["error"]

    def test_400_missing_multiple_fields(self, client):
        res = client.post("/api/courses", json={})
        assert res.status_code == 400

    def test_400_invalid_status(self, client):
        res = client.post("/api/courses", json=sample_course(status="Unknown"))
        assert res.status_code == 400
        assert "Invalid status" in res.get_json()["error"]

    def test_400_invalid_date_format(self, client):
        res = client.post("/api/courses", json=sample_course(target_date="31-12-2025"))
        assert res.status_code == 400
        assert "target_date" in res.get_json()["error"]


# ===========================================================================
# GET /api/courses — Read All
# ===========================================================================

class TestGetAllCourses:
    def test_empty_list_when_no_courses(self, client):
        res = client.get("/api/courses")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_courses(self, client):
        client.post("/api/courses", json=sample_course(name="Course A"))
        client.post("/api/courses", json=sample_course(name="Course B"))
        res = client.get("/api/courses")
        assert res.status_code == 200
        assert len(res.get_json()) == 2


# ===========================================================================
# GET /api/courses/<id> — Read Single
# ===========================================================================

class TestGetSingleCourse:
    def test_get_existing_course(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.get("/api/courses/1")
        assert res.status_code == 200
        assert res.get_json()["name"] == "Python Basics"

    def test_404_course_not_found(self, client):
        res = client.get("/api/courses/999")
        assert res.status_code == 404
        assert "not found" in res.get_json()["error"]


# ===========================================================================
# PUT /api/courses/<id> — Update
# ===========================================================================

class TestUpdateCourse:
    def test_update_status(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.put("/api/courses/1", json={"status": "In Progress"})
        assert res.status_code == 200
        assert res.get_json()["status"] == "In Progress"

    def test_update_multiple_fields(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.put("/api/courses/1", json={
            "name": "Advanced Python",
            "target_date": "2026-06-30",
        })
        body = res.get_json()
        assert body["name"] == "Advanced Python"
        assert body["target_date"] == "2026-06-30"

    def test_update_persists_in_file(self, client):
        client.post("/api/courses", json=sample_course())
        client.put("/api/courses/1", json={"status": "Completed"})
        with open(COURSES_FILE) as f:
            data = json.load(f)
        assert data[0]["status"] == "Completed"

    def test_400_invalid_status(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.put("/api/courses/1", json={"status": "Invalid"})
        assert res.status_code == 400

    def test_400_invalid_date(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.put("/api/courses/1", json={"target_date": "not-a-date"})
        assert res.status_code == 400

    def test_400_empty_body(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.put("/api/courses/1", json={})
        assert res.status_code == 400

    def test_404_course_not_found(self, client):
        res = client.put("/api/courses/999", json={"status": "Completed"})
        assert res.status_code == 404


# ===========================================================================
# DELETE /api/courses/<id> — Delete
# ===========================================================================

class TestDeleteCourse:
    def test_delete_success(self, client):
        client.post("/api/courses", json=sample_course())
        res = client.delete("/api/courses/1")
        assert res.status_code == 200
        assert "deleted" in res.get_json()["message"]

    def test_delete_removes_from_file(self, client):
        client.post("/api/courses", json=sample_course())
        client.delete("/api/courses/1")
        res = client.get("/api/courses")
        assert len(res.get_json()) == 0

    def test_404_course_not_found(self, client):
        res = client.delete("/api/courses/999")
        assert res.status_code == 404


# ===========================================================================
# GET /api/courses/stats — Statistics (Bonus)
# ===========================================================================

class TestStats:
    def test_stats_empty(self, client):
        res = client.get("/api/courses/stats")
        assert res.status_code == 200
        body = res.get_json()
        assert body["total_courses"] == 0

    def test_stats_counts_by_status(self, client):
        client.post("/api/courses", json=sample_course(name="A", status="Not Started"))
        client.post("/api/courses", json=sample_course(name="B", status="In Progress"))
        client.post("/api/courses", json=sample_course(name="C", status="In Progress"))
        client.post("/api/courses", json=sample_course(name="D", status="Completed"))
        res = client.get("/api/courses/stats")
        body = res.get_json()
        assert body["total_courses"] == 4
        assert body["by_status"]["Not Started"] == 1
        assert body["by_status"]["In Progress"] == 2
        assert body["by_status"]["Completed"] == 1


# ===========================================================================
# Full CRUD Workflow — Integration Test
# ===========================================================================

class TestFullWorkflow:
    def test_create_read_update_delete(self, client):
        # CREATE
        res = client.post("/api/courses", json=sample_course())
        assert res.status_code == 201
        course_id = res.get_json()["id"]

        # READ
        res = client.get(f"/api/courses/{course_id}")
        assert res.status_code == 200
        assert res.get_json()["status"] == "Not Started"

        # UPDATE
        res = client.put(f"/api/courses/{course_id}", json={"status": "Completed"})
        assert res.status_code == 200
        assert res.get_json()["status"] == "Completed"

        # DELETE
        res = client.delete(f"/api/courses/{course_id}")
        assert res.status_code == 200

        # VERIFY DELETED
        res = client.get(f"/api/courses/{course_id}")
        assert res.status_code == 404
