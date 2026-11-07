# InterviewAI Coach

<p align="center">
  <strong>Prepare for your job interviews with artificial intelligence.</strong>
</p>

<p align="center">
  An intelligent platform that helps candidates prepare for professional interviews with personalized questions generated from their résumé and the job posting they are targeting.
</p>

---

## About the Project

**InterviewAI Coach** is a SaaS web application designed to help candidates prepare for job interviews more effectively using artificial intelligence.

The application uses the information in a résumé and a job posting to generate interview questions tailored to the candidate's profile, skills, and target position.

The goal is to offer a personalized, interactive, and evolving preparation experience, allowing candidates to practice, keep their answers, and eventually improve their performance through intelligent analysis.

## Goals

- Make job interview preparation easier.
- Personalize questions based on the candidate's profile.
- Use résumés and job postings to give context to practice sessions.
- Let users practice in an interactive environment.
- Keep a history of simulations and answers.
- Gradually help candidates improve their performance.

## Features

### Implemented Features

- **Authentication** — Registration, login, and user account management.
- **User profile** — Management of personal information.
- **Résumé management** — Upload and storage of résumés in PDF format.
- **Job posting management** — Import and management of job postings.
- **PDF content extraction** — Text retrieval from documents.
- **Personalized preparation** — Linking a résumé and a job posting to create a preparation context.
- **AI-powered question generation** — Creation of questions tailored to the profile and the target position.
- **Text-based interview simulation** — Questions and answers typed by the user.
- **Answer persistence** — Answers are saved in the database.
- **Voice answers** — The answer can be recorded with the microphone (webm/wav/mp3/ogg, 10 MB max).
- **Speech transcription** — Recorded answers are transcribed to French text by Gemini, then reviewed and corrected by the user before validation.
- **AI analysis of answers** — Score, criteria, strengths, weaknesses and advice for a completed session.
- **Progress dashboard** — Follow-up of scores and evolution across sessions.

### Features in Progress and Planned

- Full interview history.
- Detailed review of questions and answers.
- Resuming unfinished simulations.
- Personalized recommendations to improve answers.

## Technologies Used

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Frontend | TypeScript |
| Database | PostgreSQL |
| Artificial Intelligence | Google Gemini API |
| Documents | PDF text extraction |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

> The frontend stack and the database system will be specified according to the actual dependencies and configuration of the repository.

## Project Architecture

InterviewAI Coach is built on an architecture that separates the responsibilities of the frontend, the backend, the database, and the artificial intelligence service.

```text
InterviewAI-Coach/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
│
├── docker-compose.yml
├── .env.example
└── README.md
```

*This directory structure is indicative: it should be adapted to the actual organization of the repository.*

## Installation and Setup

### 1. Prerequisites

Before you begin, install:

- Git
- Python 3
- Node.js and npm
- Docker and Docker Compose (if used)
- A Google Gemini API key

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/interview-ai-coach.git

cd interview-ai-coach
```

### 3. Configure Environment Variables

Create the required `.env` files from the examples provided in the project.

Example configuration:

```env
GEMINI_API_KEY=your_api_key
```

The other required variables (database, authentication, server configuration) must be filled in according to the project's configuration files.

**Important: never publish API keys, passwords, or other secrets in a GitHub repository.**

### 4. Run the Backend

Go to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The interactive API documentation is usually available at:

```text
http://127.0.0.1:8000/docs
```

### 5. Run the Frontend

In another terminal:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend's local address depends on the project configuration and the framework used.

## Docker

The project also includes a containerization approach with Docker to simplify setup and deployment of the application.

Once the `docker-compose.yml` file is configured for all services:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

## User Journey

The general workflow of InterviewAI Coach follows these steps:

1. The user creates an account and logs in.
2. They upload their résumé.
3. They upload a job posting.
4. They create a preparation by linking the two documents.
5. The artificial intelligence analyzes the context and generates personalized questions.
6. The user starts an interview simulation.
7. They answer the questions, by typing or by recording their voice (the recording is transcribed to text).
8. Their answers are saved so they can be reviewed and used later.
9. Upcoming analysis features will provide personalized feedback and let them track their progress.

## Roadmap

- [x] User authentication and management
- [x] User profile management
- [x] Résumé upload
- [x] Job posting import
- [x] PDF content extraction
- [x] Preparation creation
- [x] Personalized question generation with AI
- [x] Text-based interview simulation
- [x] Answer saving
- [ ] Simulation history
- [ ] Detailed results review
- [ ] Resuming unfinished sessions
- [ ] AI analysis of answers
- [ ] Performance evaluation
- [ ] Personalized tips and recommendations
- [x] Progress dashboard
- [x] Voice simulation
- [x] Automatic transcription of answers

## Security

The security of user data is an important aspect of the project.

The principles to follow include:

- Protection of routes that require authentication.
- Data isolation between users.
- Protection of personal information.
- Secure storage of API keys.
- Validation of uploaded files.
- Proper handling of errors and unauthorized access.

## Project Vision

InterviewAI Coach aims to become a true personal assistant for job interview preparation.

Beyond simply generating questions, the vision is to provide intelligent coaching that can understand a candidate's profile, simulate realistic professional situations, evaluate their answers, and help them improve over the course of their practice sessions.

**The goal: turn every preparation into an opportunity to improve and to approach your next interview with greater confidence.**

---

## Author

**Project: InterviewAI Coach**

Developed as a personal project to design and build a SaaS application that integrates artificial intelligence.

---

<p align="center">
  <strong>InterviewAI Coach — Prepare smarter. Interview better.</strong>
</p>
