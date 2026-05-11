"""Main worker script for offline crawling."""
import sys
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from worker.task_listener import TaskListener
from utils.logger import log


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    log.info(f"Received signal {signum}, shutting down...")
    if listener:
        listener.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log.info("Starting muse_collector worker...")
    
    # Create and start task listener
    listener = TaskListener()
    
    try:
        listener.start()
    except Exception as e:
        log.error(f"Worker failed: {e}")
        sys.exit(1)
