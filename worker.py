#!/usr/bin/env python3
"""Main worker script for offline data collection."""
import sys
import signal
import time
from worker.worker import CrawlerWorker
from utils.logger import log
from config.settings import settings


# Global worker instance for signal handling
worker_instance = None
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    
    signal_name = signal.Signals(signum).name
    log.info(f"Received signal {signal_name}, initiating graceful shutdown...")
    
    shutdown_requested = True
    
    if worker_instance:
        worker_instance.stop()


def main():
    """Main entry point for worker."""
    global worker_instance
    
    log.info("=" * 60)
    log.info("Muse Collector Worker Starting")
    log.info("=" * 60)
    log.info(f"Environment: {settings.app_env}")
    log.info(f"Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    log.info(f"Poll Interval: {settings.worker_poll_interval}s")
    log.info(f"Batch Size: {settings.worker_batch_size}")
    log.info(f"Max Retry: {settings.worker_max_retry}")
    log.info(f"Timeout: {settings.worker_timeout}s")
    log.info("=" * 60)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command
    
    try:
        # Create and start worker
        worker_instance = CrawlerWorker(
            poll_interval=settings.worker_poll_interval,
            batch_size=settings.worker_batch_size,
            max_retry=settings.worker_max_retry,
            timeout=settings.worker_timeout
        )
        
        log.info("Worker initialized successfully")
        log.info("Starting task polling loop...")
        
        # Start the worker
        worker_instance.start()
        
        # Keep main thread alive while worker runs
        while not shutdown_requested:
            time.sleep(1)
        
        log.info("Worker shutdown complete")
        return 0
        
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received, shutting down...")
        if worker_instance:
            worker_instance.stop()
        return 0
        
    except Exception as e:
        log.error(f"Fatal error in worker: {e}")
        import traceback
        log.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
