# CodeCraftHub API Overview

Base URL: `http://localhost:5000`

---

## GET `/`

Welcome message with a directory of available endpoints.

**Response `200`**
```json
{
  "message": "Welcome to CodeCraftHub!",
  "endpoints": { ... }
}
```

---

## POST `/api/courses`

Add a new course.

**Request body** (all fields required)
```json
{
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2025-12-31",
  "status": "Not Started"
}
```

| Field | Type | Rules |
|-------|------|-------|
| name | string | Required, non-empty |
| description | string | Required, non-empty |
| target_date | string | Required, format `YYYY-MM-DD` |
| status | string | Required, one of: `Not Started`, `In Progress`, `Completed` |

**Response `201`**
```json
{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2025-12-31",
  "status": "Not Started",
  "created_at": "2025-03-19T10:30:00.000000"
}
```

**Error responses:** `400` — missing fields, invalid status, or invalid date format.

---

## GET `/api/courses`

Get all courses.

**Response `200`**
```json
[
  { "id": 1, "name": "Python Basics", ... },
  { "id": 2, "name": "Flask Web Dev", ... }
]
```

Returns an empty array `[]` if no courses exist.

---

## GET `/api/courses/<id>`

Get a specific course by ID.

**Response `200`**
```json
{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2025-12-31",
  "status": "Not Started",
  "created_at": "2025-03-19T10:30:00.000000"
}
```

**Response `404`** — Course not found.

---

## PUT `/api/courses/<id>`

Update one or more fields of an existing course.

**Request body** (only include fields you want to change)
```json
{
  "status": "In Progress"
}
```

Updatable fields: `name`, `description`, `target_date`, `status`.

**Response `200`** — Returns the full updated course object.

**Error responses:**
- `400` — Empty body, invalid status, or invalid date format
- `404` — Course not found

---

## DELETE `/api/courses/<id>`

Delete a course by ID.

**Response `200`**
```json
{
  "message": "Course 1 deleted successfully"
}
```

**Response `404`** — Course not found.

---

## GET `/api/courses/stats`

Get statistics about all courses.

**Response `200`**
```json
{
  "total_courses": 4,
  "by_status": {
    "Not Started": 1,
    "In Progress": 2,
    "Completed": 1
  }
}
```
