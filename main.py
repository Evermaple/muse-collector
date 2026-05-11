#!/usr/bin/env python3
"""Main API server script."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from utils.logger import log
from api.middleware import (
    log_requests_middleware,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from api.tasks import router as tasks_router
from api.data import router as data_router


# Create FastAPI app
app = FastAPI(
    title="Muse Collector API",
    description="API for music data collection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(log_requests_middleware)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(tasks_router)
app.include_router(data_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Muse Collector API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from utils.db_pool import db_pool
    
    db_healthy = db_pool.check_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    log.info("=" * 60)
    log.info("Muse Collector API Starting")
    log.info("=" * 60)
    log.info(f"Environment: {settings.app_env}")
    log.info(f"Host: {settings.api_host}:{settings.api_port}")
    log.info(f"Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    log.info(f"Docs: http://{settings.api_host}:{settings.api_port}/docs")
    log.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    log.info("Muse Collector API shutting down...")


def main():
    """Main entry point."""
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        access_log=False  # We handle logging in middleware
    )


if __name__ == "__main__":
    main()
