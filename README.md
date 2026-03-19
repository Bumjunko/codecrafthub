# CodeCraftHub — Personalized Learning Platform

## Project Overview

CodeCraftHub is a RESTful API for a **personalized learning management system** built with Python Flask. It allows users to browse courses, enroll, track lesson progress, and receive course recommendations tailored to their interests.

The entire application runs from a single `app.py` file with in-memory data — no database setup required — making it ideal for learning and prototyping.

## Features

- Browse registered users and available courses
- Enroll users in courses
- Track lesson-by-lesson progress per user
- Get personalized course recommendations based on user interests
- Full error handling with appropriate HTTP status codes (400, 404, 409)
- All responses in JSON format

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **Flask 3.0** | Lightweight web framework for building the REST API |
| **pytest 8.0** | Testing framework for unit and integration tests |
| **curl** | Command-line tool for manual API testing |

## Project Structure

```
codecrafthub/
├── app.py              # Main Flask application (endpoints + in-memory data)
├── requirements.txt    # Python dependencies with pinned versions
├── test_app.py         # pytest test suite (41 test cases)
├── README.md           # Project documentation (this file)
└── docs/
    └── api_overview.md # Detailed API reference with request/response examples
```

## Setup Instructions

**1. Clone or download the project**

```bash
cd codecrafthub
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

## How to Run the Server

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000** in debug mode.

Alternatively, using the Flask CLI:

```bash
flask run
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message with a list of all available endpoints |
| GET | `/users` | Retrieve all registered users |
| GET | `/courses` | Retrieve all available courses |
| GET | `/progress/<user_id>` | View a specific user's enrollment and lesson progress |
| POST | `/enroll` | Enroll a user in a course |
| POST | `/complete_lesson` | Mark the next lesson as completed for an enrolled course |
| GET | `/recommend/<user_id>` | Get personalized course recommendations |

### curl Examples

```bash
# 1. Welcome / Home
curl http://127.0.0.1:5000/

# 2. List all users
curl http://127.0.0.1:5000/users

# 3. List all courses
curl http://127.0.0.1:5000/courses

# 4. Check a user's progress
curl http://127.0.0.1:5000/progress/u1

# 5. Enroll a user in a course
curl -X POST http://127.0.0.1:5000/enroll \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "course_id": "c2"}'

# 6. Complete a lesson
curl -X POST http://127.0.0.1:5000/complete_lesson \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "course_id": "c1"}'

# 7. Get recommendations
curl http://127.0.0.1:5000/recommend/u1
```

> **Tip:** Pipe the output through `python -m json.tool` for pretty-printed JSON.

For full request/response details, see [`docs/api_overview.md`](docs/api_overview.md).

## How to Run Tests

```bash
pytest test_app.py -v
```

The test suite contains **41 test cases** organized by endpoint, covering:

| Test Class | Tests | What it verifies |
|------------|-------|------------------|
| `TestIndex` | 3 | Home endpoint returns 200 and lists endpoints |
| `TestGetUsers` | 4 | Returns all users with correct fields |
| `TestGetCourses` | 4 | Returns all courses with correct fields |
| `TestGetProgress` | 5 | Progress lookup, empty progress, unknown user (404) |
| `TestEnroll` | 10 | Successful enrollment, duplicates (409), missing fields (400), unknown IDs (404) |
| `TestCompleteLesson` | 8 | Lesson increment, already-completed course, not-enrolled error (404) |
| `TestRecommend` | 7 | Recommendation results, ranking order, enrolled-course exclusion, unknown user (404) |

## Recommendation Logic

The `/recommend/<user_id>` endpoint uses a simple **interest-based filtering** algorithm:

1. **Retrieve** the user's `interests` list (e.g., `["python", "data-science"]`)
2. **Exclude** courses the user is already enrolled in
3. **Score** each remaining course by counting how many of the user's interests overlap with the course's `tags`
4. **Rank** courses by score in descending order — courses matching more interests appear first
5. **Return** the sorted list with matching tags shown for transparency

**Example:** Alice has interests `["python", "data-science"]` and is enrolled in "Python Basics" (`c1`). The recommender:
- Skips `c1` (already enrolled)
- Scores "Data Science with Pandas" → 2 matches (`python`, `data-science`) — ranked first
- Scores "Flask Web Development" → 1 match (`python`) — ranked second
- Skips JavaScript/React courses → 0 matches

## Use of Generative AI in Development

This project was developed with the assistance of **Generative AI (GenAI)** tools.

### What GenAI Did

| Step | GenAI Contribution |
|------|--------------------|
| 1 | Generated the initial Flask API structure (`app.py`) with 7 endpoints and in-memory sample data |
| 2 | Drafted the `README.md` including project overview, setup instructions, and API documentation |
| 3 | Created the pytest test suite (`test_app.py`) with 41 test cases covering success and failure paths |
| 4 | Wrote the API reference document (`docs/api_overview.md`) with request/response examples |
| 5 | Reviewed code for Flask best practices — `request.get_json()` usage, HTTP status codes, error handling |
| 6 | Iterated on the recommendation logic through conversational feedback |

### What the Developer Did

| Step | Human Review & Editing |
|------|------------------------|
| 1 | Defined all requirements, endpoint specifications, and data models |
| 2 | Reviewed every line of generated code for correctness and readability |
| 3 | Ran `pytest` and `curl` tests to validate all endpoints manually |
| 4 | Edited and refined documentation to match the actual implementation |
| 5 | Made final decisions on error handling strategies and HTTP status codes |

> Generative AI was used to help draft the initial server structure, create project documentation, and generate test case ideas. The generated content was reviewed, edited, and validated through manual testing.
