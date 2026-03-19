"""
CodeCraftHub — A personalized learning platform REST API.

This single-file Flask app provides endpoints to manage users, courses,
enrollment, lesson completion, and simple course recommendations.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory data stores
# ---------------------------------------------------------------------------

USERS = {
    "u1": {
        "id": "u1",
        "name": "Alice",
        "interests": ["python", "data-science"],
    },
    "u2": {
        "id": "u2",
        "name": "Bob",
        "interests": ["web", "javascript"],
    },
    "u3": {
        "id": "u3",
        "name": "Charlie",
        "interests": ["python", "web"],
    },
}

COURSES = {
    "c1": {
        "id": "c1",
        "title": "Python Basics",
        "tags": ["python"],
        "total_lessons": 5,
    },
    "c2": {
        "id": "c2",
        "title": "Data Science with Pandas",
        "tags": ["python", "data-science"],
        "total_lessons": 8,
    },
    "c3": {
        "id": "c3",
        "title": "JavaScript Fundamentals",
        "tags": ["javascript", "web"],
        "total_lessons": 6,
    },
    "c4": {
        "id": "c4",
        "title": "Flask Web Development",
        "tags": ["python", "web"],
        "total_lessons": 7,
    },
    "c5": {
        "id": "c5",
        "title": "React for Beginners",
        "tags": ["javascript", "web"],
        "total_lessons": 10,
    },
}

# Maps user_id -> list of enrollment records.
# Each record tracks which course the user enrolled in and lessons completed.
PROGRESS = {
    "u1": [
        {"course_id": "c1", "completed_lessons": 3},
    ],
    "u2": [
        {"course_id": "c3", "completed_lessons": 6},
    ],
}

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Welcome message with a quick summary of available endpoints."""
    return jsonify({
        "message": "Welcome to CodeCraftHub!",
        "endpoints": {
            "GET  /users": "List all users",
            "GET  /courses": "List all courses",
            "GET  /progress/<user_id>": "View a user's learning progress",
            "POST /enroll": "Enroll a user in a course",
            "POST /complete_lesson": "Mark a lesson as completed",
            "GET  /recommend/<user_id>": "Get course recommendations",
        },
    })


@app.route("/users")
def get_users():
    """Return every user."""
    return jsonify(list(USERS.values()))


@app.route("/courses")
def get_courses():
    """Return every course."""
    return jsonify(list(COURSES.values()))


@app.route("/progress/<user_id>")
def get_progress(user_id):
    """Return enrollment & lesson progress for a single user."""
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404

    records = PROGRESS.get(user_id, [])

    enriched = []
    for rec in records:
        course = COURSES[rec["course_id"]]
        enriched.append({
            "course_id": course["id"],
            "course_title": course["title"],
            "completed_lessons": rec["completed_lessons"],
            "total_lessons": course["total_lessons"],
        })

    return jsonify({
        "user_id": user_id,
        "user_name": USERS[user_id]["name"],
        "progress": enriched,
    })


@app.route("/enroll", methods=["POST"])
def enroll():
    """
    Enroll a user in a course.

    Expects JSON: {"user_id": "u1", "course_id": "c2"}
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    course_id = data.get("course_id")

    if not user_id or not course_id:
        return jsonify({"error": "user_id and course_id are required"}), 400
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    if course_id not in COURSES:
        return jsonify({"error": "Course not found"}), 404

    user_progress = PROGRESS.setdefault(user_id, [])

    already_enrolled = any(r["course_id"] == course_id for r in user_progress)
    if already_enrolled:
        return jsonify({"error": "User is already enrolled in this course"}), 409

    user_progress.append({"course_id": course_id, "completed_lessons": 0})

    return jsonify({
        "message": f"{USERS[user_id]['name']} enrolled in {COURSES[course_id]['title']}",
        "user_id": user_id,
        "course_id": course_id,
    }), 201


@app.route("/complete_lesson", methods=["POST"])
def complete_lesson():
    """
    Mark one more lesson as completed for a user's enrolled course.

    Expects JSON: {"user_id": "u1", "course_id": "c1"}
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    course_id = data.get("course_id")

    if not user_id or not course_id:
        return jsonify({"error": "user_id and course_id are required"}), 400
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    if course_id not in COURSES:
        return jsonify({"error": "Course not found"}), 404

    user_progress = PROGRESS.get(user_id, [])
    record = next((r for r in user_progress if r["course_id"] == course_id), None)

    if record is None:
        return jsonify({"error": "User is not enrolled in this course"}), 404

    total = COURSES[course_id]["total_lessons"]
    if record["completed_lessons"] >= total:
        return jsonify({"message": "Course already fully completed!"}), 200

    record["completed_lessons"] += 1

    return jsonify({
        "message": "Lesson completed!",
        "user_id": user_id,
        "course_id": course_id,
        "completed_lessons": record["completed_lessons"],
        "total_lessons": total,
    })


@app.route("/recommend/<user_id>")
def recommend(user_id):
    """
    Recommend courses the user hasn't enrolled in yet, ranked by how many of
    the user's interests match each course's tags.
    """
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404

    user = USERS[user_id]
    interests = set(user["interests"])

    enrolled_ids = {r["course_id"] for r in PROGRESS.get(user_id, [])}

    scored = []
    for course in COURSES.values():
        if course["id"] in enrolled_ids:
            continue
        overlap = interests & set(course["tags"])
        if overlap:
            scored.append((len(overlap), course))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    recommendations = [
        {
            "course_id": course["id"],
            "course_title": course["title"],
            "matching_tags": list(interests & set(course["tags"])),
        }
        for _, course in scored
    ]

    return jsonify({
        "user_id": user_id,
        "user_name": user["name"],
        "recommendations": recommendations,
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
