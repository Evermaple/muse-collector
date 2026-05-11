"""Timeout utilities for task execution."""
import signal
import time
from typing import Callable, Any
from contextlib import contextmanager
from utils.logger import log


class TimeoutError(Exception):
    """Timeout exception."""
    pass


class TaskTimeout:
    """Task timeout manager."""
    
    def __init__(self, timeout_seconds: int):
        """
        Initialize timeout manager.
        
        Args:
            timeout_seconds: Timeout in seconds
        """
        self.timeout_seconds = timeout_seconds
        self.start_time = None
    
    def start(self):
        """Start the timeout timer."""
        self.start_time = time.time()
        log.info(f"Task timeout started: {self.timeout_seconds}s")
    
    def check(self) -> bool:
        """
        Check if timeout has been exceeded.
        
        Returns:
            bool: True if timeout exceeded
        """
        if self.start_time is None:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed > self.timeout_seconds
    
    def get_elapsed(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            float: Elapsed time
        """
        if self.start_time is None:
            return 0.0
        
        return time.time() - self.start_time
    
    def get_remaining(self) -> float:
        """
        Get remaining time in seconds.
        
        Returns:
            float: Remaining time (0 if exceeded)
        """
        if self.start_time is None:
            return self.timeout_seconds
        
        elapsed = self.get_elapsed()
        remaining = self.timeout_seconds - elapsed
        return max(0.0, remaining)
    
    def raise_if_exceeded(self):
        """Raise TimeoutError if timeout exceeded."""
        if self.check():
            elapsed = self.get_elapsed()
            raise TimeoutError(
                f"Task timeout exceeded: {elapsed:.1f}s > {self.timeout_seconds}s"
            )


@contextmanager
def timeout_context(seconds: int):
    """
    Context manager for timeout handling (Unix-like systems only).
    
    Args:
        seconds: Timeout in seconds
        
    Example:
        with timeout_context(30):
            # Your code here
            pass
    
    Note:
        This uses signal.alarm which only works on Unix-like systems.
        For cross-platform support, use TaskTimeout class instead.
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old handler and cancel the alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


class TaskExecutionMonitor:
    """Monitor task execution time and statistics."""
    
    def __init__(self, task_id: str, timeout_seconds: int = None):
        """
        Initialize execution monitor.
        
        Args:
            task_id: Task ID
            timeout_seconds: Optional timeout
        """
        self.task_id = task_id
        self.timeout = TaskTimeout(timeout_seconds) if timeout_seconds else None
        self.start_time = None
        self.end_time = None
        self.item_count = 0
        self.success_count = 0
        self.failed_count = 0
    
    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        if self.timeout:
            self.timeout.start()
        log.info(f"Task {self.task_id} execution started")
    
    def check_timeout(self):
        """Check and raise if timeout exceeded."""
        if self.timeout:
            self.timeout.raise_if_exceeded()
    
    def record_success(self):
        """Record a successful item."""
        self.success_count += 1
        self.item_count += 1
    
    def record_failure(self):
        """Record a failed item."""
        self.failed_count += 1
        self.item_count += 1
    
    def finish(self):
        """Finish monitoring."""
        self.end_time = time.time()
        duration = self.get_duration()
        
        log.info(
            f"Task {self.task_id} execution finished - "
            f"Duration: {duration:.2f}s, "
            f"Total: {self.item_count}, "
            f"Success: {self.success_count}, "
            f"Failed: {self.failed_count}"
        )
    
    def get_duration(self) -> float:
        """
        Get execution duration.
        
        Returns:
            float: Duration in seconds
        """
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def get_stats(self) -> dict:
        """
        Get execution statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            'task_id': self.task_id,
            'duration': self.get_duration(),
            'item_count': self.item_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'success_rate': self.success_count / self.item_count if self.item_count > 0 else 0.0
        }
