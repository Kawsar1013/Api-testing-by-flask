# Flask Event Management & Course Repository System

A comprehensive Flask web application with user authentication, event management, and course repository features. The system includes both web interfaces and public REST APIs for programmatic access.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Event Management**: Create, view, edit, and delete events with various types (events, competitions, programs)
- **Course Repository**: Manage course resources including documents, links, videos, assignments, and syllabi
- **Public REST API**: Access event and course data programmatically
- **Search Functionality**: Search courses and events
- **File Upload**: Support for document uploads in course resources

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   - Web Interface: `http://localhost:5000/21201327`
   - API Base URL: `http://localhost:5000/api/`

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password` (Hashed)

### Events Table
- `id` (Primary Key)
- `title`
- `description`
- `event_type` (event, competition, program)
- `date`
- `location`
- `max_participants`
- `current_participants`
- `status` (upcoming, ongoing, completed, cancelled)
- `created_at`
- `user_id` (Foreign Key to Users)

### Courses Table
- `id` (Primary Key)
- `course_code` (Unique, e.g., CSE110)
- `course_name`
- `description`
- `department`
- `created_at`

### CourseResources Table
- `id` (Primary Key)
- `title`
- `description`
- `resource_type` (document, link, video, assignment, syllabus)
- `file_path` (For uploaded files)
- `external_link` (For external URLs)
- `file_size` (File size in bytes)
- `uploaded_at`
- `course_id` (Foreign Key to Courses)

## Web Interface Routes

### Authentication Routes
- `GET /21201327` - Home page (requires login)
- `GET /register/21201327` - Registration page
- `POST /register/21201327` - Register new user
- `GET /login/21201327` - Login page
- `POST /login/21201327` - User login
- `GET /logout/21201327` - User logout

### Event Management Routes
- `GET /events/21201327` - List all events
- `GET /events/create/21201327` - Create event form
- `POST /events/create/21201327` - Create new event
- `GET /events/<id>/21201327` - View specific event
- `GET /events/<id>/edit/21201327` - Edit event form
- `POST /events/<id>/edit/21201327` - Update event
- `POST /events/<id>/delete/21201327` - Delete event

### Course Repository Routes
- `GET /courses/21201327` - List all courses
- `GET /courses/<id>/21201327` - View course resources
- `GET /courses/<id>/resources/add/21201327` - Add resource form
- `POST /courses/<id>/resources/add/21201327` - Add new resource
- `POST /courses/resources/<id>/delete/21201327` - Delete resource
- `GET /courses/resources/<id>/download/21201327` - Download resource file

## Public REST API

### Event API Endpoints

#### Get All Events
```http
GET /api/events/21201327
```
**Response**:
```json
[
  {
    "id": 1,
    "title": "Python Workshop",
    "description": "Learn Python programming basics",
    "event_type": "event",
    "date": "2024-01-15T10:00:00",
    "location": "Room 101",
    "max_participants": 50,
    "current_participants": 25,
    "status": "upcoming",
    "created_at": "2024-01-01T09:00:00",
    "creator": "john_doe"
  }
]
```

#### Get Specific Event
```http
GET /api/events/{event_id}/21201327
```
**Response**:
```json
{
  "id": 1,
  "title": "Python Workshop",
  "description": "Learn Python programming basics",
  "event_type": "event",
  "date": "2024-01-15T10:00:00",
  "location": "Room 101",
  "max_participants": 50,
  "current_participants": 25,
  "status": "upcoming",
  "created_at": "2024-01-01T09:00:00",
  "creator": "john_doe"
}
```

#### Create New Event
```http
POST /api/events/21201327
Content-Type: application/json

{
  "title": "New Event",
  "description": "Event description",
  "event_type": "event",
  "date": "2024-02-01T10:00:00",
  "location": "Room 102",
  "max_participants": 30
}
```

#### Update Event
```http
PUT /api/events/{event_id}/21201327
Content-Type: application/json

{
  "title": "Updated Event Title",
  "description": "Updated description",
  "status": "ongoing"
}
```

#### Delete Event
```http
DELETE /api/events/{event_id}/21201327
```

### Course Repository API Endpoints

#### Get All Courses
```http
GET /api/courses/21201327
```
**Query Parameters**:
- `search` (optional): Search courses by code, name, or department

**Response**:
```json
[
  {
    "course_id": 1,
    "course_code": "CSE110",
    "course_name": "Programming Language I",
    "description": "Introduction to programming concepts using Python",
    "department": "Computer Science and Engineering",
    "resource_count": 4,
    "created_at": "2024-01-01T09:00:00"
  }
]
```

#### Get Specific Course with Resources
```http
GET /api/courses/{course_id}/21201327
```
**Response**:
```json
{
  "course_id": 1,
  "course_code": "CSE110",
  "course_name": "Programming Language I",
  "description": "Introduction to programming concepts using Python",
  "department": "Computer Science and Engineering",
  "created_at": "2024-01-01T09:00:00",
  "resources": [
    {
      "resource_id": 1,
      "title": "Week 1 Lecture Notes",
      "description": "Introduction to Python programming basics",
      "resource_type": "document",
      "file_size": 1024000,
      "external_link": null,
      "uploaded_at": "2024-01-01T10:00:00"
    }
  ]
}
```

#### Get Course Resources
```http
GET /api/courses/{course_id}/resources/21201327
```
**Response**:
```json
[
  {
    "resource_id": 1,
    "title": "Week 1 Lecture Notes",
    "description": "Introduction to Python programming basics",
    "resource_type": "document",
    "file_size": 1024000,
    "external_link": null,
    "uploaded_at": "2024-01-01T10:00:00"
  }
]
```

#### Get Specific Resource
```http
GET /api/courses/resources/{resource_id}/21201327
```
**Response**:
```json
{
  "resource_id": 1,
  "title": "Week 1 Lecture Notes",
  "description": "Introduction to Python programming basics",
  "resource_type": "document",
  "file_size": 1024000,
  "external_link": null,
  "uploaded_at": "2024-01-01T10:00:00",
  "course_id": 1,
  "course_code": "CSE110",
  "course_name": "Programming Language I"
}
```

## API Usage Examples

### Using cURL

#### Get all courses
```bash
curl -X GET "http://localhost:5000/api/courses/21201327"
```

#### Search courses
```bash
curl -X GET "http://localhost:5000/api/courses/21201327?search=CSE110"
```

#### Get specific course with resources
```bash
curl -X GET "http://localhost:5000/api/courses/1/21201327"
```

#### Get course resources
```bash
curl -X GET "http://localhost:5000/api/courses/1/resources/21201327"
```

### Using Postman

1. **Get All Courses**:
   - Method: `GET`
   - URL: `http://localhost:5000/api/courses/21201327`

2. **Search Courses**:
   - Method: `GET`
   - URL: `http://localhost:5000/api/courses/21201327?search=CSE110`

3. **Get Course with Resources**:
   - Method: `GET`
   - URL: `http://localhost:5000/api/courses/1/21201327`

4. **Get Course Resources**:
   - Method: `GET`
   - URL: `http://localhost:5000/api/courses/1/resources/21201327`

## Security Notes

- All web routes require authentication except login and register
- Public API endpoints are accessible without authentication
- File uploads are restricted to specific formats
- Passwords are hashed using Werkzeug's security functions

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── events.html       # Events list
│   ├── create_event.html # Create event form
│   ├── view_event.html   # View event details
│   ├── edit_event.html   # Edit event form
│   ├── courses.html      # Course repository
│   ├── view_course.html  # View course resources
│   └── add_resource.html # Add resource form
└── uploads/              # Uploaded files directory
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `404` - Resource not found
- `500` - Internal server error

Error responses include an `error` field with a descriptive message:
```json
{
  "error": "Course not found"
}
```
