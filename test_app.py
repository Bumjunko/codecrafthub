"""
test_app.py — pytest test suite for the CodeCraftHub API.

Covers every endpoint with both success and failure cases.
Run with:  pytest test_app.py -v
"""

import pytest
from app import app, PROGRESS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a Flask test client for sending requests."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_progress():
    """Reset in-memory PROGRESS data before every test so tests stay independent."""
    original = {
        "u1": [{"course_id": "c1", "completed_lessons": 3}],
        "u2": [{"course_id": "c3", "completed_lessons": 6}],
    }
    PROGRESS.clear()
    PROGRESS.update(original)
    yield
    PROGRESS.clear()
    PROGRESS.update(original)


# ===========================================================================
# 1. GET /  — Home / Welcome
# ===========================================================================

class TestIndex:
    def test_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_returns_json_with_welcome_message(self, client):
        body = client.get("/").get_json()
        assert "Welcome" in body["message"]

    def test_lists_available_endpoints(self, client):
        body = client.get("/").get_json()
        assert "endpoints" in body
        assert len(body["endpoints"]) >= 6


# ===========================================================================
# 2. GET /users
# ===========================================================================

class TestGetUsers:
    def test_returns_200(self, client):
        res = client.get("/users")
        assert res.status_code == 200

    def test_returns_list(self, client):
        users = client.get("/users").get_json()
        assert isinstance(users, list)

    def test_contains_all_sample_users(self, client):
        users = client.get("/users").get_json()
        names = {u["name"] for u in users}
        assert names == {"Alice", "Bob", "Charlie"}

    def test_each_user_has_required_fields(self, client):
        users = client.get("/users").get_json()
        for user in users:
            assert "id" in user
            assert "name" in user
            assert "interests" in user


# ===========================================================================
# 3. GET /courses
# ===========================================================================

class TestGetCourses:
    def test_returns_200(self, client):
        res = client.get("/courses")
        assert res.status_code == 200

    def test_returns_list(self, client):
        courses = client.get("/courses").get_json()
        assert isinstance(courses, list)

    def test_contains_all_sample_courses(self, client):
        courses = client.get("/courses").get_json()
        assert len(courses) == 5

    def test_each_course_has_required_fields(self, client):
        courses = client.get("/courses").get_json()
        for course in courses:
            assert "id" in course
            assert "title" in course
            assert "tags" in course
            assert "total_lessons" in course


# ===========================================================================
# 4. GET /progress/<user_id>
# ===========================================================================

class TestGetProgress:
    # ---- Success cases ----------------------------------------------------

    def test_returns_200_for_valid_user(self, client):
        res = client.get("/progress/u1")
        assert res.status_code == 200

    def test_returns_user_info_and_progress(self, client):
        body = client.get("/progress/u1").get_json()
        assert body["user_id"] == "u1"
        assert body["user_name"] == "Alice"
        assert len(body["progress"]) == 1

    def test_progress_contains_course_details(self, client):
        prog = client.get("/progress/u1").get_json()["progress"][0]
        assert prog["course_id"] == "c1"
        assert prog["course_title"] == "Python Basics"
        assert prog["completed_lessons"] == 3
        assert prog["total_lessons"] == 5

    def test_user_with_no_enrollments(self, client):
        body = client.get("/progress/u3").get_json()
        assert body["user_id"] == "u3"
        assert body["progress"] == []

    # ---- Failure cases ----------------------------------------------------

    def test_404_for_unknown_user(self, client):
        res = client.get("/progress/u999")
        assert res.status_code == 404
        assert "error" in res.get_json()


# ===========================================================================
# 5. POST /enroll
# ===========================================================================

class TestEnroll:
    # ---- Success cases ----------------------------------------------------

    def test_enroll_returns_201(self, client):
        res = client.post("/enroll", json={"user_id": "u1", "course_id": "c2"})
        assert res.status_code == 201

    def test_enroll_response_contains_confirmation(self, client):
        body = client.post(
            "/enroll", json={"user_id": "u1", "course_id": "c2"}
        ).get_json()
        assert "enrolled" in body["message"]
        assert body["user_id"] == "u1"
        assert body["course_id"] == "c2"

    def test_enroll_updates_progress(self, client):
        client.post("/enroll", json={"user_id": "u1", "course_id": "c4"})
        body = client.get("/progress/u1").get_json()
        enrolled_courses = [p["course_id"] for p in body["progress"]]
        assert "c4" in enrolled_courses

    def test_enroll_user_with_no_prior_enrollment(self, client):
        res = client.post("/enroll", json={"user_id": "u3", "course_id": "c1"})
        assert res.status_code == 201

    # ---- Failure cases ----------------------------------------------------

    def test_400_when_missing_course_id(self, client):
        res = client.post("/enroll", json={"user_id": "u1"})
        assert res.status_code == 400

    def test_400_when_missing_user_id(self, client):
        res = client.post("/enroll", json={"course_id": "c1"})
        assert res.status_code == 400

    def test_400_when_empty_body(self, client):
        res = client.post("/enroll", json={})
        assert res.status_code == 400

    def test_404_for_unknown_user(self, client):
        res = client.post("/enroll", json={"user_id": "u999", "course_id": "c1"})
        assert res.status_code == 404

    def test_404_for_unknown_course(self, client):
        res = client.post("/enroll", json={"user_id": "u1", "course_id": "c999"})
        assert res.status_code == 404

    def test_409_for_duplicate_enrollment(self, client):
        res = client.post("/enroll", json={"user_id": "u1", "course_id": "c1"})
        assert res.status_code == 409
        assert "already enrolled" in res.get_json()["error"]


# ===========================================================================
# 6. POST /complete_lesson
# ===========================================================================

class TestCompleteLesson:
    # ---- Success cases ----------------------------------------------------

    def test_returns_200(self, client):
        res = client.post(
            "/complete_lesson", json={"user_id": "u1", "course_id": "c1"}
        )
        assert res.status_code == 200

    def test_increments_completed_lessons(self, client):
        body = client.post(
            "/complete_lesson", json={"user_id": "u1", "course_id": "c1"}
        ).get_json()
        assert body["completed_lessons"] == 4
        assert body["total_lessons"] == 5

    def test_multiple_completions_increment_correctly(self, client):
        client.post("/complete_lesson", json={"user_id": "u1", "course_id": "c1"})
        body = client.post(
            "/complete_lesson", json={"user_id": "u1", "course_id": "c1"}
        ).get_json()
        assert body["completed_lessons"] == 5

    def test_already_fully_completed(self, client):
        body = client.post(
            "/complete_lesson", json={"user_id": "u2", "course_id": "c3"}
        ).get_json()
        assert "fully completed" in body["message"]

    # ---- Failure cases ----------------------------------------------------

    def test_400_when_empty_body(self, client):
        res = client.post("/complete_lesson", json={})
        assert res.status_code == 400

    def test_404_for_unknown_user(self, client):
        res = client.post(
            "/complete_lesson", json={"user_id": "u999", "course_id": "c1"}
        )
        assert res.status_code == 404

    def test_404_for_unknown_course(self, client):
        res = client.post(
            "/complete_lesson", json={"user_id": "u1", "course_id": "c999"}
        )
        assert res.status_code == 404

    def test_404_when_not_enrolled(self, client):
        res = client.post(
            "/complete_lesson", json={"user_id": "u3", "course_id": "c1"}
        )
        assert res.status_code == 404
        assert "not enrolled" in res.get_json()["error"]


# ===========================================================================
# 7. GET /recommend/<user_id>
# ===========================================================================

class TestRecommend:
    # ---- Success cases ----------------------------------------------------

    def test_returns_200(self, client):
        res = client.get("/recommend/u1")
        assert res.status_code == 200

    def test_returns_recommendations_list(self, client):
        body = client.get("/recommend/u1").get_json()
        assert "recommendations" in body
        assert isinstance(body["recommendations"], list)

    def test_excludes_already_enrolled_courses(self, client):
        recs = client.get("/recommend/u1").get_json()["recommendations"]
        rec_ids = [r["course_id"] for r in recs]
        assert "c1" not in rec_ids

    def test_recommendations_match_user_interests(self, client):
        recs = client.get("/recommend/u1").get_json()["recommendations"]
        for rec in recs:
            assert len(rec["matching_tags"]) > 0

    def test_recommendations_ranked_by_relevance(self, client):
        recs = client.get("/recommend/u1").get_json()["recommendations"]
        tag_counts = [len(r["matching_tags"]) for r in recs]
        assert tag_counts == sorted(tag_counts, reverse=True)

    def test_recommend_after_enrolling_reduces_results(self, client):
        before = client.get("/recommend/u1").get_json()["recommendations"]
        new_course = before[0]["course_id"]
        client.post("/enroll", json={"user_id": "u1", "course_id": new_course})
        after = client.get("/recommend/u1").get_json()["recommendations"]
        assert len(after) < len(before)

    # ---- Failure cases ----------------------------------------------------

    def test_404_for_unknown_user(self, client):
        res = client.get("/recommend/u999")
        assert res.status_code == 404
        assert "error" in res.get_json()
