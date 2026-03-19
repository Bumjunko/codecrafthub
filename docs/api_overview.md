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

## GET `/users`

List all registered users.

**Response `200`**
```json
[
  { "id": "u1", "name": "Alice", "interests": ["python", "data-science"] },
  { "id": "u2", "name": "Bob",   "interests": ["web", "javascript"] }
]
```

---

## GET `/courses`

List all available courses.

**Response `200`**
```json
[
  { "id": "c1", "title": "Python Basics", "tags": ["python"], "total_lessons": 5 }
]
```

---

## GET `/progress/<user_id>`

View a specific user's learning progress across all enrolled courses.

**Response `200`**
```json
{
  "user_id": "u1",
  "user_name": "Alice",
  "progress": [
    {
      "course_id": "c1",
      "course_title": "Python Basics",
      "completed_lessons": 3,
      "total_lessons": 5
    }
  ]
}
```

**Response `404`** — User not found.

---

## POST `/enroll`

Enroll a user in a course.

**Request body**
```json
{ "user_id": "u1", "course_id": "c2" }
```

| Status | Meaning |
|--------|---------|
| `201`  | Successfully enrolled |
| `400`  | Missing required fields |
| `404`  | User or course not found |
| `409`  | Already enrolled |

**Response `201`**
```json
{
  "message": "Alice enrolled in Data Science with Pandas",
  "user_id": "u1",
  "course_id": "c2"
}
```

---

## POST `/complete_lesson`

Mark the next lesson as completed for an enrolled course.

**Request body**
```json
{ "user_id": "u1", "course_id": "c1" }
```

| Status | Meaning |
|--------|---------|
| `200`  | Lesson marked complete (or course already fully completed) |
| `400`  | Missing required fields |
| `404`  | User/course not found or user not enrolled |

**Response `200`**
```json
{
  "message": "Lesson completed!",
  "user_id": "u1",
  "course_id": "c1",
  "completed_lessons": 4,
  "total_lessons": 5
}
```

---

## GET `/recommend/<user_id>`

Get personalized course recommendations based on the user's interests, excluding courses the user is already enrolled in. Results are ranked by how many interests match each course's tags.

**Response `200`**
```json
{
  "user_id": "u1",
  "user_name": "Alice",
  "recommendations": [
    {
      "course_id": "c2",
      "course_title": "Data Science with Pandas",
      "matching_tags": ["python", "data-science"]
    },
    {
      "course_id": "c4",
      "course_title": "Flask Web Development",
      "matching_tags": ["python"]
    }
  ]
}
```

**Response `404`** — User not found.
