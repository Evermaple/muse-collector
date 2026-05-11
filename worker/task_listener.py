"""Task listener for monitoring and executing crawl tasks."""
import time
from typing import Optional, Dict, Any
from datetime import datetime

from utils.db_operations import TaskRepository
from utils.logger import log
from config.settings import settings


class TaskLock:
    """Simple database-based task lock to prevent concurrent execution."""
    
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo
    
    def acquire(self, task_id: str) -> bool:
        """
        Try to acquire lock for a task by updating status to running.
        
        Args:
            task_id: Task ID to lock
            
        Returns:
            bool: True if lock acquired successfully
        """
        try:
            # Try to update task from waiting (1) to running (2)
            # This is atomic at database level
            affected = self.task_repo.update(
                data={'task_status': 2, 'mtime': datetime.now()},
                where={'task_id': task_id, 'task_status': 1}
            )
            
            if affected > 0:
                log.info(f"Task lock acquired: {task_id}")
                return True
            else:
                log.debug(f"Task lock failed (already locked or not waiting): {task_id}")
                return False
                
        except Exception as e:
            log.error(f"Failed to acquire task lock for {task_id}: {e}")
            return False
    
    def release(self, task_id: str, status: int, success_cnt: int = 0, 
                failed_reason: str = "") -> bool:
        """
        Release lock and update task final status.
        
        Args:
            task_id: Task ID to release
            status: Final task status (3=success, 4=failed)
            success_cnt: Number of successful items
            failed_reason: Failure reason if any
            
        Returns:
            bool: True if released successfully
        """
        try:
            data = {
                'task_status': status,
                'success_cnt': success_cnt,
                'mtime': datetime.now()
            }
            
            if failed_reason:
                data['failed_reason'] = failed_reason
            
            affected = self.task_repo.update(
                data=data,
                where={'task_id': task_id}
            )
            
            if affected > 0:
                log.info(f"Task lock released: {task_id}, status={status}")
                return True
            else:
                log.warning(f"Task lock release failed: {task_id}")
                return False
                
        except Exception as e:
            log.error(f"Failed to release task lock for {task_id}: {e}")
            return False


class TaskListener:
    """
    Task listener that monitors crawl_task table and executes pending tasks.
    
    This component:
    - Polls the database for pending tasks (task_status=1)
    - Acquires lock to prevent concurrent execution
    - Updates task status to running (task_status=2)
    - Delegates actual crawling to worker
    """
    
    def __init__(self):
        self.task_repo = TaskRepository()
        self.task_lock = TaskLock(self.task_repo)
        self.running = False
        self.poll_interval = settings.worker_poll_interval
    
    def start(self):
        """Start the task listener loop."""
        self.running = True
        log.info("Task listener started")
        
        while self.running:
            try:
                self._poll_and_process()
            except KeyboardInterrupt:
                log.info("Task listener interrupted by user")
                self.stop()
                break
            except Exception as e:
                log.error(f"Error in task listener loop: {e}")
            
            # Sleep before next poll
            time.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the task listener."""
        self.running = False
        log.info("Task listener stopped")
    
    def _poll_and_process(self):
        """Poll for pending tasks and process them."""
        # Find pending tasks
        pending_tasks = self.task_repo.find_pending_tasks(limit=10)
        
        if not pending_tasks:
            log.debug("No pending tasks found")
            return
        
        log.info(f"Found {len(pending_tasks)} pending task(s)")
        
        for task_data in pending_tasks:
            task_id = task_data.get('task_id')
            
            # Try to acquire lock
            if not self.task_lock.acquire(task_id):
                log.debug(f"Skipping task {task_id} (lock not acquired)")
                continue
            
            # Process the task
            try:
                self._process_task(task_data)
            except Exception as e:
                log.error(f"Failed to process task {task_id}: {e}")
                # Release lock with failed status
                self.task_lock.release(
                    task_id=task_id,
                    status=4,  # Failed
                    failed_reason=str(e)[:200]
                )
    
    def _process_task(self, task_data: Dict[str, Any]):
        """
        Process a single task.
        
        Args:
            task_data: Task data dictionary from database
        """
        from worker.crawler import CrawlerWorker
        
        task_id = task_data.get('task_id')
        task_type = task_data.get('task_type')
        
        log.info(f"Processing task: {task_id}, type: {task_type}")
        
        try:
            # Create crawler worker
            crawler = CrawlerWorker()
            
            # Process the task
            success_cnt, item_cnt, error_msg = crawler.process_task(task_data)
            
            # Update task with item count
            self.task_repo.update(
                data={'item_cnt': item_cnt},
                where={'task_id': task_id}
            )
            
            # Determine final status
            if success_cnt == item_cnt and item_cnt > 0:
                # All items succeeded
                final_status = 3  # Success
                log.info(f"Task {task_id} completed successfully: {success_cnt}/{item_cnt}")
            elif success_cnt > 0:
                # Partial success
                final_status = 3  # Success (with some failures)
                log.warning(f"Task {task_id} partially completed: {success_cnt}/{item_cnt}")
            else:
                # All failed
                final_status = 4  # Failed
                log.error(f"Task {task_id} failed: {success_cnt}/{item_cnt}")
            
            # Release lock with final status
            self.task_lock.release(
                task_id=task_id,
                status=final_status,
                success_cnt=success_cnt,
                failed_reason=error_msg if error_msg else ""
            )
            
        except Exception as e:
            log.error(f"Exception processing task {task_id}: {e}", exc_info=True)
            # Release lock with failed status
            self.task_lock.release(
                task_id=task_id,
                status=4,  # Failed
                success_cnt=0,
                failed_reason=str(e)[:200]
            )
