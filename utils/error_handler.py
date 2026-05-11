"""Centralized error handling for crawler."""
from typing import Optional, Callable, Any
import traceback
from utils.logger import log
from utils.retry import (
    NetworkError,
    TimeoutError,
    RateLimitError,
    DataNotFoundError,
    ParseError
)


class ErrorHandler:
    """Centralized error handler for crawler operations."""
    
    @staticmethod
    def handle_crawl_error(error: Exception, context: str = '') -> tuple[bool, str]:
        """
        Handle crawling errors and determine if retry is needed.
        
        Args:
            error: Exception that occurred
            context: Context information (e.g., "fetching song 12345")
            
        Returns:
            tuple: (should_retry, error_message)
        """
        error_msg = str(error)
        full_context = f"{context}: {error_msg}" if context else error_msg
        
        # Network errors - should retry
        if isinstance(error, (NetworkError, TimeoutError)):
            log.warning(f"Network error (retryable): {full_context}")
            return True, f"Network error: {error_msg}"
        
        # Rate limit errors - should retry with backoff
        if isinstance(error, RateLimitError):
            log.warning(f"Rate limit error (retryable): {full_context}")
            return True, f"Rate limited: {error_msg}"
        
        # Data not found - should not retry
        if isinstance(error, DataNotFoundError):
            log.info(f"Data not found (not retryable): {full_context}")
            return False, f"Data not found: {error_msg}"
        
        # Parse errors - should not retry
        if isinstance(error, ParseError):
            log.error(f"Parse error (not retryable): {full_context}")
            return False, f"Parse error: {error_msg}"
        
        # JSON decode errors - should not retry
        if isinstance(error, ValueError) and 'JSON' in str(error):
            log.error(f"JSON parse error (not retryable): {full_context}")
            return False, f"Invalid JSON response: {error_msg}"
        
        # Unknown errors - log and don't retry
        log.error(f"Unknown error (not retryable): {full_context}")
        log.error(traceback.format_exc())
        return False, f"Unknown error: {error_msg}"
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str = '') -> tuple[bool, str]:
        """
        Handle database errors and determine if retry is needed.
        
        Args:
            error: Exception that occurred
            operation: Database operation description
            
        Returns:
            tuple: (should_retry, error_message)
        """
        error_msg = str(error)
        full_context = f"{operation}: {error_msg}" if operation else error_msg
        
        # Connection errors - should retry
        if 'connection' in error_msg.lower() or 'lost connection' in error_msg.lower():
            log.warning(f"Database connection error (retryable): {full_context}")
            return True, f"DB connection error: {error_msg}"
        
        # Deadlock errors - should retry
        if 'deadlock' in error_msg.lower():
            log.warning(f"Database deadlock (retryable): {full_context}")
            return True, f"DB deadlock: {error_msg}"
        
        # Duplicate key errors - should not retry (handle specially)
        if 'duplicate' in error_msg.lower() or 'unique constraint' in error_msg.lower():
            log.info(f"Duplicate key (not retryable): {full_context}")
            return False, f"Duplicate entry: {error_msg}"
        
        # Other database errors - log and don't retry
        log.error(f"Database error (not retryable): {full_context}")
        log.error(traceback.format_exc())
        return False, f"DB error: {error_msg}"
    
    @staticmethod
    def safe_execute(func: Callable, *args, context: str = '', **kwargs) -> tuple[bool, Any, str]:
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            context: Context description
            **kwargs: Keyword arguments
            
        Returns:
            tuple: (success, result, error_message)
        """
        try:
            result = func(*args, **kwargs)
            return True, result, ""
        except Exception as e:
            should_retry, error_msg = ErrorHandler.handle_crawl_error(e, context)
            return False, None, error_msg
    
    @staticmethod
    def format_error_for_db(error_msg: str, max_length: int = 200) -> str:
        """
        Format error message for database storage.
        
        Args:
            error_msg: Error message
            max_length: Maximum length
            
        Returns:
            str: Formatted error message
        """
        if not error_msg:
            return ""
        
        # Truncate if too long
        if len(error_msg) > max_length:
            return error_msg[:max_length - 3] + "..."
        
        return error_msg
    
    @staticmethod
    def log_task_error(task_id: str, error: Exception, context: str = ''):
        """
        Log task-level error with full context.
        
        Args:
            task_id: Task ID
            error: Exception
            context: Additional context
        """
        log.error(f"Task {task_id} error - {context}")
        log.error(f"Error type: {type(error).__name__}")
        log.error(f"Error message: {str(error)}")
        log.error(f"Traceback:\n{traceback.format_exc()}")
