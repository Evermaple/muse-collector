"""Base adapter interface for data sources."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import time
from utils.logger import log
from utils.retry import (
    exponential_backoff_retry, 
    NetworkError, 
    TimeoutError, 
    RateLimitError,
    DataNotFoundError
)


class DataSourceAdapter(ABC):
    """Abstract base class for data source adapters."""
    
    def __init__(self, base_url: str, timeout: int = 30, rate_limit: int = 100):
        """
        Initialize adapter.
        
        Args:
            base_url: Base URL for the data source API
            timeout: Request timeout in seconds
            rate_limit: Maximum requests per minute
        """
        self.base_url = base_url
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _rate_limit_check(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Check if rate limit exceeded
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                log.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with rate limiting and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: HTTP response
            
        Raises:
            NetworkError: For network-related errors
            TimeoutError: For timeout errors
            RateLimitError: For rate limit errors
        """
        self._rate_limit_check()
        
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting (HTTP 429)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                log.warning(f"Rate limited, retry after {retry_after}s")
                raise RateLimitError(f"Rate limited, retry after {retry_after}s")
            
            # Handle server errors (5xx) - retryable
            if 500 <= response.status_code < 600:
                log.warning(f"Server error: {response.status_code}")
                raise NetworkError(f"Server error: {response.status_code}")
            
            # Handle client errors (4xx) - not retryable except 429
            if 400 <= response.status_code < 500:
                if response.status_code == 404:
                    raise DataNotFoundError(f"Resource not found: {url}")
                log.error(f"Client error: {response.status_code}")
                response.raise_for_status()
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            log.error(f"Request timeout: {method} {url}")
            raise TimeoutError(f"Request timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            log.error(f"Connection error: {method} {url}")
            raise NetworkError(f"Connection error: {e}")
        except (RateLimitError, DataNotFoundError, NetworkError, TimeoutError):
            # Re-raise our custom exceptions
            raise
        except requests.exceptions.RequestException as e:
            log.error(f"Request failed: {method} {url}, error: {e}")
            raise NetworkError(f"Request failed: {e}")
    
    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        exceptions=(NetworkError, TimeoutError, RateLimitError)
    )
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make GET request with automatic retry.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            dict: JSON response
        """
        url = f"{self.base_url}{endpoint}"
        response = self._make_request('GET', url, params=params)
        return response.json()
    
    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        exceptions=(NetworkError, TimeoutError, RateLimitError)
    )
    def post(self, endpoint: str, data: Dict[str, Any] = None, 
             json: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make POST request with automatic retry.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            dict: JSON response
        """
        url = f"{self.base_url}{endpoint}"
        response = self._make_request('POST', url, data=data, json=json)
        return response.json()
    
    @abstractmethod
    def fetch_song(self, song_id: int, search_key: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch song information from data source.
        
        Args:
            song_id: Song ID in the data source
            search_key: Optional search keyword
            
        Returns:
            dict: Song data or None if not found
        """
        pass
    
    @abstractmethod
    def fetch_artist(self, artist_id: int, search_key: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch artist information from data source.
        
        Args:
            artist_id: Artist ID in the data source
            search_key: Optional search keyword
            
        Returns:
            dict: Artist data or None if not found
        """
        pass
    
    @abstractmethod
    def parse_song_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw song data to standard format.
        
        Args:
            raw_data: Raw data from API
            
        Returns:
            dict: Standardized song data
        """
        pass
    
    @abstractmethod
    def parse_artist_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw artist data to standard format.
        
        Args:
            raw_data: Raw data from API
            
        Returns:
            dict: Standardized artist data
        """
        pass
    
    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()
