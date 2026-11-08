"""
Studio Growth OS - FastAPI Backend
Main application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import prisma
from core.logging import setup_logging
from api.v1.router import api_router
from workers.main import start_workers, stop_workers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await prisma.connect()
    await start_workers()
    yield
    # Shutdown
    await stop_workers()
    await prisma.disconnect()


app = FastAPI(
    title="Studio Growth OS API",
    description="AI-powered photography studio growth platform",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.DEBUG else "Internal error"},
    )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }

# API routes
app.include_router(api_router, prefix="/api/v1")

# Root
@app.get("/")
async def root():
    return {
        "name": "Studio Growth OS API",
        "version": "2.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )