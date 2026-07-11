# AI Customer Support Automation Platform – Backend

Production-ready FastAPI backend that integrates with an n8n workflow for AI-powered customer support. When the AI confidence score falls below the threshold, n8n escalates the query to human support by creating a ticket via this API.

Live Backend:
https://backend-1-2fdm.onrender.com

API Documentation:
https://backend-1-2fdm.onrender.com/docs

## Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Framework    | FastAPI                 |
| ORM          | SQLAlchemy 2.x          |
| Database     | SQLite (`tickets.db`)   |
| Validation   | Pydantic v2             |
| Server       | Uvicorn                 |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Server

```bash
# From the backend/ directory (with venv activated)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Resource    | URL                              |
|-------------|----------------------------------|
| API base    | http://localhost:8000            |
| Swagger UI  | http://localhost:8000/docs       |
| ReDoc       | http://localhost:8000/redoc      |
| Health      | http://localhost:8000/health       |

The SQLite database file `tickets.db` is created automatically on first startup.

---

## API Endpoints

### Tickets

| Method   | Endpoint            | Description                          | Status Codes        |
|----------|---------------------|--------------------------------------|---------------------|
| `POST`   | `/tickets`          | Create a new ticket (n8n integration)| `201`, `422`        |
| `GET`    | `/tickets`          | List all tickets                     | `200`               |
| `GET`    | `/tickets/{id}`     | Get a single ticket                  | `200`, `404`        |
| `PATCH`  | `/tickets/{id}`     | Update `status` and/or `priority`    | `200`, `404`, `422` |
| `DELETE` | `/tickets/{id}`     | Delete a ticket                      | `200`, `404`        |

### Dashboard

| Method | Endpoint      | Description              | Status Codes |
|--------|---------------|--------------------------|--------------|
| `GET`  | `/dashboard`  | Aggregated ticket stats  | `200`        |

### Health

| Method | Endpoint  | Description    |
|--------|-----------|----------------|
| `GET`  | `/health` | Liveness probe |

---

### Request / Response Examples

#### POST /tickets

**Request:**
```json
{
  "customer_name": "Jane Smith",
  "customer_query": "I was charged twice for my subscription",
  "priority": "High",
  "confidence": 38.2,
  "sentiment": "Negative"
}
```

**Response (201):**
```json
{
  "success": true,
  "ticket_id": 1,
  "message": "Ticket created successfully"
}
```

#### GET /dashboard

**Response (200):**
```json
{
  "total_tickets": 20,
  "open_tickets": 5,
  "resolved_tickets": 15,
  "high_priority": 3,
  "average_confidence": 84.5
}
```

#### PATCH /tickets/1

**Request:**
```json
{
  "status": "Resolved",
  "priority": "Low"
}
```

---

## Project Architecture

```
backend/
├── app/
│   ├── __init__.py      # Package marker
│   ├── main.py          # FastAPI app, CORS, exception handlers, startup
│   ├── config.py        # Settings (DB URL, CORS origins, API metadata)
│   ├── database.py      # SQLAlchemy engine, session, init_db()
│   ├── models.py        # Ticket ORM model
│   ├── schemas.py       # Pydantic request/response models
│   ├── crud.py          # Database operations (no raw SQL)
│   └── routes.py        # API route handlers
├── tickets.db           # SQLite database (auto-created)
├── requirements.txt
└── README.md
```

### Data Flow with n8n

```
Telegram User
      ↓
Telegram Trigger (n8n)
      ↓
Google Sheets FAQ Lookup (n8n)
      ↓
Gemini AI (n8n)
      ↓
Confidence & Sentiment (n8n)
      ↓
IF Node – confidence >= threshold?
      │
      ├── TRUE  → Send AI Response (n8n)
      │
      └── FALSE → POST /tickets (this backend)
                        ↓
                  Store in tickets.db
                        ↓
                  Notify Human Support (n8n)
```

### Layer Responsibilities

| Layer      | File          | Responsibility                              |
|------------|---------------|---------------------------------------------|
| Routes     | `routes.py`   | HTTP handling, status codes, validation     |
| CRUD       | `crud.py`     | All database reads/writes via SQLAlchemy    |
| Models     | `models.py`   | Table schema definition                     |
| Schemas    | `schemas.py`  | API contract (input/output validation)      |
| Database   | `database.py` | Connection pooling, session lifecycle       |
| Config     | `config.py`   | Centralized configuration                   |

---

## Connecting with n8n

### Workflow Integration Point

In your n8n workflow, the **FALSE** branch of the confidence IF node should call `POST /tickets` on this backend before notifying human support.

### Prerequisites

1. Start this backend (`uvicorn app.main:app --reload --port 8000`).
2. Ensure n8n can reach `http://localhost:8000` (or your machine's LAN IP if n8n runs in Docker).

### n8n HTTP Request Node Configuration

See the **n8n HTTP Request Configuration** section at the bottom of this document for the exact node settings.

### Mapping n8n Variables to the Request Body

Use n8n expressions to map workflow data:

```json
{
  "customer_name": "{{ $json.customer_name }}",
  "customer_query": "{{ $json.message }}",
  "priority": "{{ $json.priority }}",
  "confidence": {{ $json.confidence }},
  "sentiment": "{{ $json.sentiment }}"
}
```

### Suggested n8n Flow After Ticket Creation

```
POST /tickets  →  Store Ticket (Set node)  →  Notify Human Support (Email/Slack/Telegram)
```

Use the `ticket_id` from the API response (`{{ $json.ticket_id }}`) in your notification message.

---

## Workflow Screenshots

### Workflow Overview
<img src="https://github.com/user-attachments/assets/3f5a47f9-db04-4ee4-b402-4fb83ef21e57">

### Screenshot 2
<img src="https://github.com/user-attachments/assets/542bfb21-265a-4d68-b15e-87b768c0caed">

### Screenshot 3
<img src="https://github.com/user-attachments/assets/ae7d97e7-9fce-4f7c-ae7a-bee6167ce19d">

### Screenshot 4
<img src="https://github.com/user-attachments/assets/454d006e-04a7-4bff-9b39-6504e8b878c5">

---

## Ticket Model

| Column          | Type     | Notes                          |
|-----------------|----------|--------------------------------|
| `id`            | Integer  | Auto-increment primary key     |
| `customer_name` | String   | Required                       |
| `customer_query`| String   | Required                       |
| `priority`      | String   | e.g. High, Medium, Low         |
| `confidence`    | Float    | 0–100 from AI pipeline         |
| `sentiment`     | String   | e.g. Positive, Negative        |
| `status`        | String   | Default: `"Open"`              |
| `created_at`    | DateTime | Auto-set on creation           |

---

## Error Handling

| Scenario              | HTTP Status | Response                              |
|-----------------------|-------------|---------------------------------------|
| Validation failure    | 422         | `{ "detail": "field: error message" }`|
| Ticket not found      | 404         | `{ "detail": "Ticket with id X not found" }` |
| Database error        | 500         | `{ "detail": "A database error occurred..." }` |
| Unhandled exception   | 500         | `{ "detail": "An unexpected error occurred." }` |

---

## n8n HTTP Request Configuration

Use these exact settings in your n8n **HTTP Request** node (FALSE branch of the IF node):

| Setting       | Value                                                                 |
|---------------|-----------------------------------------------------------------------|
| **Method**    | `POST`                                                                |
| **URL**       | `http://localhost:8000/tickets`                                       |
| **Authentication** | `None`                                                          |
| **Send Body** | `Yes`                                                                 |
| **Body Content Type** | `JSON`                                                        |

### Headers

| Header         | Value              |
|----------------|--------------------|
| `Content-Type` | `application/json` |

### Body (JSON)

```json
{
  "customer_name": "{{ $json.customer_name }}",
  "customer_query": "{{ $json.customer_query }}",
  "priority": "{{ $json.priority }}",
  "confidence": {{ $json.confidence }},
  "sentiment": "{{ $json.sentiment }}"
}
```

### Example Static Body (for testing)

```json
{
  "customer_name": "John Doe",
  "customer_query": "My order has not arrived after 2 weeks",
  "priority": "High",
  "confidence": 35.0,
  "sentiment": "Negative"
}
```

### Expected Response

```json
{
  "success": true,
  "ticket_id": 1,
  "message": "Ticket created successfully"
}
```

---

## License

MIT
