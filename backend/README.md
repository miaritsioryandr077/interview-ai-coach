# InterviewAI Coach - Backend API

FastAPI backend initial setup structured with Clean Architecture principles.

## 📐 Project Structure

```text
backend/
├── app/
│   ├── api/             # API Router & Versioned Endpoints (v1)
│   ├── core/            # App Configuration & DB Session Setup
│   ├── db/              # SQLAlchemy Base & Migrations setup
│   ├── models/          # SQLAlchemy ORM Database Models
│   ├── schemas/         # Pydantic Schemas / DTOs
│   ├── repositories/    # Data Access Layer (CRUD)
│   ├── services/        # Business Logic / Domain Services
│   └── main.py          # FastAPI Application Entrypoint
├── tests/               # Pytest Suite (Fixtures & Endpoint Tests)
├── .env.example         # Environment Variable Template
├── .gitignore           # Git Exclusion File
├── README.md            # Project Documentation & Guides
└── requirements.txt     # Dependencies List
```

---

## 🛠️ Installation & Setup

### 1. Requirements
- **Python 3.10+** installed
- **PostgreSQL 14+** (or Docker)

### 2. Environment Setup
Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables (.env)
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Adjust `.env` variables if necessary:
```env
PROJECT_NAME="InterviewAI Coach API"
API_V1_STR="/api/v1"
SECRET_KEY="your_super_secret_key_here"

POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=interview_ai_coach
```

---

## 🐘 Launching PostgreSQL

### Option A: Using Docker (Recommended)
```bash
docker run --name interview-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=interview_ai_coach -p 5432:5432 -d postgres:16-alpine
```

### Option B: Native Installation
Make sure your PostgreSQL service is running and create the database:
```sql
CREATE DATABASE interview_ai_coach;
```

---

## 🚀 Running the FastAPI Application

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

- **Swagger UI Interactive Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Running Tests

Run the test suite using `pytest`:

```bash
pytest
```

To view verbose output:
```bash
pytest -v
```
