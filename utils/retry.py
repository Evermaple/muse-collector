"""Retry utilities with exponential backoff."""
import time
import functools
from typing import Callable, Type, Tuple
from utils.logger import log


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        exceptions: Tuple of exceptions to catch and retry
        
    Example:
        @exponential_backoff_retry(max_retries=3, base_delay=1.0)
        def fetch_data():
            # Your code here
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        log.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    log.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    
                    time.sleep(delay)
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class RetryableError(Exception):
    """Base exception for retryable errors."""
    pass


class NetworkError(RetryableError):
    """Network related errors."""
    pass


class TimeoutError(RetryableError):
    """Timeout errors."""
    pass


class RateLimitError(RetryableError):
    """Rate limit errors."""
    pass


class DataSourceError(Exception):
    """Base exception for data source errors."""
    pass


class DataNotFoundError(DataSourceError):
    """Data not found in source."""
    pass


class ParseError(DataSourceError):
    """Error parsing data from source."""
    pass
