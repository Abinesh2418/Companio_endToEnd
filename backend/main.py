"""
AI Companio - Main FastAPI Application
Entry point for the API server with modularized feature routes
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from database import init_db

# Import feature routers
from features.auth.routes import router as auth_router
from features.goals.routes import router as goals_router
from features.tasks.routes import router as tasks_router
from features.productivity.routes import router as productivity_router

app = FastAPI(
    title="AI Companio API",
    version="2.0.0",
    description="Modular backend for AI-powered student companion with intelligent goal management"
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup"""
    init_db()
    print("✅ Database initialized successfully")
    print("🚀 AI Companio API is ready")


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Companio API is running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Authentication (PostgreSQL)",
            "Goal Management",
            "Intelligent Task Breakdown",
            "Productivity & Motivation",
            "Smart Reminders"
        ]
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


# Register feature routers
app.include_router(auth_router)
app.include_router(goals_router)
app.include_router(tasks_router)
app.include_router(productivity_router)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Companio API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
