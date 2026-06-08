from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import endpoints

# Create database tables automatically for SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Feedback Intelligence API",
    description="API for the Feedback Intelligence System",
    version="1.0.0"
)

# Configure CORS for the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local development. Update in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "Feedback Intelligence API is running"}
