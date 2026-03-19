"""
CodeCraftHub — A simple personalized learning platform REST API.

Developers can track courses they want to learn using this Flask API.
Course data is stored in a local JSON file (courses.json) — no database needed.
"""

import json
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path to the JSON file that stores all course data
COURSES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json")

# Valid status values for a course
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


# ---------------------------------------------------------------------------
# Helper functions for reading / writing the JSON file
# ---------------------------------------------------------------------------

def load_courses():
    """Read courses from the JSON file. Returns an empty list if the file
    doesn't exist yet or contains invalid JSON."""
    if not os.path.exists(COURSES_FILE):
        return []
    try:
        with open(COURSES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_courses(courses):
    """Write the courses list to the JSON file."""
    try:
        with open(COURSES_FILE, "w") as f:
            json.dump(courses, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to write to {COURSES_FILE}: {e}")


def get_next_id(courses):
    """Generate the next auto-incremented integer ID."""
    if not courses:
        return 1
    return max(c["id"] for c in courses) + 1


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Welcome message with a summary of available endpoints."""
    return jsonify({
        "message": "Welcome to CodeCraftHub!",
        "endpoints": {
            "POST   /api/courses": "Add a new course",
            "GET    /api/courses": "Get all courses",
            "GET    /api/courses/<id>": "Get a specific course",
            "PUT    /api/courses/<id>": "Update a course",
            "DELETE /api/courses/<id>": "Delete a course",
            "GET    /api/courses/stats": "Get course statistics",
        },
    })


# ---- CREATE ---------------------------------------------------------------

@app.route("/api/courses", methods=["POST"])
def add_course():
    """Add a new course. All four fields are required:
    name, description, target_date (YYYY-MM-DD), status."""
    data = request.get_json(silent=True) or {}

    # Validate required fields
    required = ["name", "description", "target_date", "status"]
    missing = [f for f in required if f not in data or not str(data[f]).strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Validate status value
    if data["status"] not in VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        }), 400

    # Validate target_date format
    try:
        datetime.strptime(data["target_date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid target_date format. Use YYYY-MM-DD"}), 400

    courses = load_courses()

    new_course = {
        "id": get_next_id(courses),
        "name": data["name"],
        "description": data["description"],
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": datetime.now().isoformat(),
    }

    courses.append(new_course)
    save_courses(courses)

    return jsonify(new_course), 201


# ---- READ (all) -----------------------------------------------------------

@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Return all courses stored in the JSON file."""
    courses = load_courses()
    return jsonify(courses)


# ---- READ (single) --------------------------------------------------------

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """Return a single course by its ID."""
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    if course is None:
        return jsonify({"error": f"Course with id {course_id} not found"}), 404

    return jsonify(course)


# ---- UPDATE ---------------------------------------------------------------

@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """Update one or more fields of an existing course."""
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    # Validate status if provided
    if "status" in data and data["status"] not in VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        }), 400

    # Validate target_date if provided
    if "target_date" in data:
        try:
            datetime.strptime(data["target_date"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid target_date format. Use YYYY-MM-DD"}), 400

    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    if course is None:
        return jsonify({"error": f"Course with id {course_id} not found"}), 404

    # Only update allowed fields
    updatable = ["name", "description", "target_date", "status"]
    for field in updatable:
        if field in data:
            course[field] = data[field]

    save_courses(courses)

    return jsonify(course)


# ---- DELETE ---------------------------------------------------------------

@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course by its ID."""
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    if course is None:
        return jsonify({"error": f"Course with id {course_id} not found"}), 404

    courses = [c for c in courses if c["id"] != course_id]
    save_courses(courses)

    return jsonify({"message": f"Course {course_id} deleted successfully"})


# ---- STATS (bonus) --------------------------------------------------------

@app.route("/api/courses/stats", methods=["GET"])
def get_stats():
    """Return statistics: total courses and count by status."""
    courses = load_courses()

    stats = {
        "total_courses": len(courses),
        "by_status": {
            "Not Started": sum(1 for c in courses if c["status"] == "Not Started"),
            "In Progress": sum(1 for c in courses if c["status"] == "In Progress"),
            "Completed": sum(1 for c in courses if c["status"] == "Completed"),
        },
    }

    return jsonify(stats)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(" * CodeCraftHub API is starting...")
    print(f" * Data will be stored in: {COURSES_FILE}")
    print(" * API will be available at: http://localhost:5000")
    app.run(debug=True)
