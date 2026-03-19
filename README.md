# CodeCraftHub — Personalized Learning Platform

## Project Overview

CodeCraftHub is a simple RESTful API for a **personalized learning platform** where developers can track courses they want to learn. Built with Python Flask, it stores course data in a local JSON file (`courses.json`) — no database needed.

This project was designed as a beginner-friendly introduction to REST APIs and CRUD operations.

## Features

- Full CRUD operations for courses (Create, Read, Update, Delete)
- File-based data storage using JSON — data persists between server restarts
- Auto-generated course IDs (starting from 1)
- Status tracking: `Not Started`, `In Progress`, `Completed`
- Input validation for all required fields, date format, and status values
- Proper error handling with descriptive messages
- Bonus: Statistics endpoint showing course counts by status
- All responses in JSON format

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **Flask 3.0** | Lightweight web framework for building the REST API |
| **pytest 8.0** | Testing framework for unit and integration tests |
| **JSON** | File-based data storage (`courses.json`) |
| **curl** | Command-line tool for manual API testing |

## Project Structure

```
codecrafthub/
├── app.py              # Main Flask application (all CRUD endpoints)
├── courses.json        # Auto-generated data file (created on first POST)
├── requirements.txt    # Python dependencies with pinned versions
├── test_app.py         # pytest test suite (30+ test cases)
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

You should see output similar to:

```
 * CodeCraftHub API is starting...
 * Data will be stored in: /path/to/courses.json
 * API will be available at: http://localhost:5000
```

Alternatively, using the Flask CLI:

```bash
flask run
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message with endpoint directory |
| POST | `/api/courses` | Add a new course |
| GET | `/api/courses` | Get all courses |
| GET | `/api/courses/<id>` | Get a specific course |
| PUT | `/api/courses/<id>` | Update a course |
| DELETE | `/api/courses/<id>` | Delete a course |
| GET | `/api/courses/stats` | Get course statistics by status |

### Course Data Model

Each course has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Auto-generated, starting from 1 |
| name | string | Course name (required) |
| description | string | Course description (required) |
| target_date | string | Target completion date in `YYYY-MM-DD` format (required) |
| status | string | One of: `Not Started`, `In Progress`, `Completed` (required) |
| created_at | string | Auto-generated ISO timestamp |

### curl Test Examples

```bash
# 1. Welcome / Home
curl http://localhost:5000/

# 2. Add a course (POST)
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Basics",
    "description": "Learn Python fundamentals",
    "target_date": "2025-12-31",
    "status": "Not Started"
  }'

# 3. Get all courses (GET)
curl http://localhost:5000/api/courses

# 4. Get a specific course (GET)
curl http://localhost:5000/api/courses/1

# 5. Update a course (PUT)
curl -X PUT http://localhost:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress"
  }'

# 6. Delete a course (DELETE)
curl -X DELETE http://localhost:5000/api/courses/1

# 7. Get course statistics (GET)
curl http://localhost:5000/api/courses/stats
```

> **Tip:** Pipe the output through `python -m json.tool` for pretty-printed JSON.

For full request/response details, see [`docs/api_overview.md`](docs/api_overview.md).

## How to Run Tests

```bash
pytest test_app.py -v
```

The test suite covers:

| Test Class | What it verifies |
|------------|------------------|
| `TestIndex` | Home endpoint returns 200 and welcome message |
| `TestCreateCourse` | Course creation, auto-ID, validation (missing fields, invalid status/date) |
| `TestGetAllCourses` | Empty list, multiple courses |
| `TestGetSingleCourse` | Fetch by ID, 404 for missing course |
| `TestUpdateCourse` | Partial updates, validation, persistence, 404 |
| `TestDeleteCourse` | Successful delete, file update, 404 |
| `TestStats` | Empty stats, counts by status |
| `TestFullWorkflow` | End-to-end Create → Read → Update → Delete cycle |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` |
| Port 5000 already in use | Stop the other process or use `flask run --port 5001` |
| `courses.json` not created | It is auto-created on the first `POST /api/courses` request |
| Permission error on `courses.json` | Check file permissions in the project directory |

## Use of Generative AI in Development

This project was developed with the assistance of **Generative AI (GenAI)** tools.

### What GenAI Did

| Step | GenAI Contribution |
|------|--------------------|
| 1 | Generated the initial Flask API structure (`app.py`) with CRUD endpoints and JSON file storage |
| 2 | Drafted the `README.md` including project overview, setup instructions, and API documentation |
| 3 | Created the pytest test suite (`test_app.py`) covering success paths, error handling, and edge cases |
| 4 | Wrote the API reference document (`docs/api_overview.md`) with request/response examples |
| 5 | Reviewed code for Flask best practices — `request.get_json()` usage, HTTP status codes, error handling |
| 6 | Added the bonus statistics endpoint through iterative prompting |

### What the Developer Did

| Step | Human Review & Editing |
|------|------------------------|
| 1 | Defined all requirements, endpoint specifications, and data models |
| 2 | Reviewed every line of generated code for correctness and readability |
| 3 | Ran `pytest` and `curl` tests to validate all endpoints manually |
| 4 | Edited and refined documentation to match the actual implementation |
| 5 | Made final decisions on error handling strategies and HTTP status codes |

> Generative AI was used to help draft the initial server structure, create project documentation, and generate test case ideas. The generated content was reviewed, edited, and validated through manual testing.
