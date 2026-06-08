# Feedback Intelligence System - Enterprise Edition

An enterprise-grade, multi-channel feedback intelligence platform that uses advanced NLP to automatically analyze customer sentiment, generate AI-driven automated responses, and produce comprehensive weekly PDF reports.

## 🚀 Running in GitHub Codespaces (Recommended)

This project is fully configured for a seamless 1-click launch using GitHub Codespaces:
1. Click the **"Code"** button on GitHub and select **"Create codespace on main"**.
2. Wait a minute for the Codespace to initialize. Our `.devcontainer` will automatically install all Python and Node dependencies!
3. Open a terminal in your Codespace and start the backend:
   ```bash
   source venv/bin/activate
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```
4. Open a **second** terminal and start the React frontend:
   ```bash
   cd frontend
   npm run dev
   ```
5. Click the pop-up links in the bottom right corner of VS Code to view the running app!

---

## 🌟 Extra Credit Features Implemented

## Architecture
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic Migrations
- **Async Workers:** Celery, Redis (Broker and Backend)
- **AI/NLP:** HuggingFace `transformers` (distilbert), Local AI Prompt Heuristics
- **Frontend:** React, Vite, TypeScript, Vanilla CSS (Modern aesthetic), Recharts
- **DevOps:** Docker, Docker Compose

## Setup & Deployment (Docker)

This application is fully containerized. You do not need to install Python or Node locally.

1. Ensure Docker and Docker Compose are installed on your machine.
2. Clone the repository and navigate to the project root.
3. Build and launch the ecosystem:
   ```bash
   docker-compose up --build
   ```
   *This command will pull the Postgres/Redis images, build the Python backend, build the Celery worker, and build the React frontend.*

### Services
- **React Dashboard:** Available at `http://localhost:5173`
- **FastAPI Backend (Swagger Docs):** Available at `http://localhost:8000/docs`
- **PostgreSQL Database:** Running on port `5432`
- **Redis Broker:** Running on port `6379`

## Testing
To run the automated test suite (verifying >80% coverage):
```bash
# While inside the python environment or docker container
pytest tests/ --cov=src
```

## Features
- **Asynchronous Scraping**: Hit `/api/ingest/playstore` or `/api/ingest/appstore`. A Celery worker will fetch the data in the background and process the NLP without blocking the API.
- **AI Executive Summary**: Weekly PDF reports now include an AI-generated textual summary of trends and urgent issues.
- **Database Migrations**: Alembic tracks all schema changes for production environments.
