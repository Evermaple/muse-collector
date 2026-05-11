"""API middleware for error handling and logging."""
import time
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.logger import log


async def log_requests_middleware(request: Request, call_next):
    """
    Middleware to log all API requests and responses.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response
    """
    # Generate request ID
    request_id = f"{int(time.time() * 1000)}"
    
    # Log request
    log.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"- Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        log.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        log.error(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Error: {str(e)} - Duration: {duration:.3f}s"
        )
        raise


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSONResponse
    """
    log.warning(
        f"HTTP {exc.status_code} - {request.method} {request.url.path} - {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
        
    Returns:
        JSONResponse
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "; ".join(errors)
    
    log.warning(
        f"Validation error - {request.method} {request.url.path} - {error_message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": f"Validation error: {error_message}",
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSONResponse
    """
    log.error(
        f"Unhandled exception - {request.method} {request.url.path} - {str(exc)}"
    )
    log.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": None
        }
    )
