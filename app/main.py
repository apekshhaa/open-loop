"""
Main FastAPI application.

Initializes and configures the FastAPI server for the AI Agent Credit System.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.config import settings
from app.models import HealthCheckResponse
from app.routes import loan_router
from app.utils import create_error_response

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description="A modular multi-agent lending pipeline system",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Application Lifecycle ==============

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    TODO: Implement:
        - Database connection
        - Service initialization
        - Cache warming
        - Configuration validation
    """
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    TODO: Implement:
        - Database connection cleanup
        - Resource cleanup
        - Graceful shutdown
    """
    logger.info("Application shutting down")
    logger.info("Cleanup complete")


# ============== Health & Status Routes ==============

@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns the current health status of the API.
    
    Returns:
        HealthCheckResponse with status details
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.api_version
    )


@app.get("/status", tags=["health"])
async def get_status():
    """
    Get detailed API status.
    
    Returns comprehensive status information including:
    - Application version
    - Environment
    - Configuration status
    - Service health
    """
    return {
        "status": "running",
        "version": settings.api_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "timestamp": datetime.utcnow().isoformat(),
        "database_configured": settings.mongodb_url is not None or settings.supabase_url is not None,
        "blockchain_configured": settings.blockchain_provider_url is not None
    }


# ============== API Routes ==============

# Include loan routes
app.include_router(loan_router)


# ============== Root Route ==============

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API information.
    
    Returns basic information about the API and links to documentation.
    """
    return {
        "title": settings.api_title,
        "version": settings.api_version,
        "description": "Multi-agent AI lending pipeline system",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "loans": "/loan"
        }
    }


# ============== Error Handlers ==============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")
    
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code="HTTP_ERROR",
            error_message=str(exc.detail)
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An unexpected error occurred"
        )
    )


# ============== Pipeline Info Route ==============

@app.get("/pipeline/info", tags=["pipeline"])
async def pipeline_info():
    """
    Get information about the lending pipeline.
    
    Returns:
        Description of all pipeline stages and agents
    """
    return {
        "title": "AI Agent Credit System Pipeline",
        "description": "Multi-stage lending pipeline with specialized agents",
        "stages": [
            {
                "order": 1,
                "name": "gatekeeper",
                "description": "Identity verification and KYC compliance",
                "endpoint": "POST /loan/{loan_id}/verify",
                "output": "Verification status"
            },
            {
                "order": 2,
                "name": "analyst",
                "description": "Credit scoring and financial analysis",
                "endpoint": "POST /loan/{loan_id}/score",
                "output": "Credit score and risk assessment"
            },
            {
                "order": 3,
                "name": "decision",
                "description": "Loan approval/rejection decision",
                "endpoint": "POST /loan/{loan_id}/decide",
                "output": "Approval decision and loan terms"
            },
            {
                "order": 4,
                "name": "treasury",
                "description": "Fund availability verification",
                "endpoint": "GET /loan/{loan_id}/pipeline",
                "output": "Fund availability and portfolio limits"
            },
            {
                "order": 5,
                "name": "settler",
                "description": "Fund disbursement and settlement",
                "endpoint": "POST /loan/{loan_id}/disburse",
                "output": "Disbursement confirmation"
            },
            {
                "order": 6,
                "name": "auditor",
                "description": "Audit logging and compliance",
                "endpoint": "GET /loan/{loan_id}/audit-trail",
                "output": "Complete audit trail"
            }
        ]
    }


# Make app available for import
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
