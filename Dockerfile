FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PostgreSQL driver and general compilation
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install existing requirements and the new enterprise requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary celery redis alembic pytest pytest-cov

COPY . .

# Environment variable to inform the app it's running in Docker
ENV DOCKER_ENV=1

# Command is overridden in docker-compose for worker/web
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
