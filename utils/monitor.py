"""Task monitoring and statistics."""
from typing import Dict, Any, List
from datetime import datetime
from utils.db_operations import TaskRepository
from utils.logger import log


class TaskMonitor:
    """Monitor and track task execution statistics."""
    
    def __init__(self):
        """Initialize task monitor."""
        self.task_repo = TaskRepository()
        self.metrics = {}
    
    def record_task_start(self, task_id: str, item_count: int):
        """
        Record task start.
        
        Args:
            task_id: Task ID
            item_count: Number of items to process
        """
        self.metrics[task_id] = {
            'start_time': datetime.now(),
            'item_count': item_count,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }
        log.info(f"Task {task_id} started - {item_count} items to process")
    
    def record_item_success(self, task_id: str):
        """
        Record successful item processing.
        
        Args:
            task_id: Task ID
        """
        if task_id in self.metrics:
            self.metrics[task_id]['processed'] += 1
            self.metrics[task_id]['success'] += 1
    
    def record_item_failure(self, task_id: str, error_msg: str = ''):
        """
        Record failed item processing.
        
        Args:
            task_id: Task ID
            error_msg: Error message
        """
        if task_id in self.metrics:
            self.metrics[task_id]['processed'] += 1
            self.metrics[task_id]['failed'] += 1
            if error_msg:
                self.metrics[task_id]['errors'].append(error_msg)
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Get task progress.
        
        Args:
            task_id: Task ID
            
        Returns:
            dict: Progress information
        """
        if task_id not in self.metrics:
            return {}
        
        metrics = self.metrics[task_id]
        total = metrics['item_count']
        processed = metrics['processed']
        
        progress = {
            'task_id': task_id,
            'total': total,
            'processed': processed,
            'success': metrics['success'],
            'failed': metrics['failed'],
            'progress_percent': (processed / total * 100) if total > 0 else 0,
            'success_rate': (metrics['success'] / processed * 100) if processed > 0 else 0
        }
        
        if metrics.get('start_time'):
            elapsed = (datetime.now() - metrics['start_time']).total_seconds()
            progress['elapsed_seconds'] = elapsed
            
            if processed > 0:
                avg_time = elapsed / processed
                remaining = total - processed
                progress['estimated_remaining_seconds'] = avg_time * remaining
        
        return progress
    
    def log_progress(self, task_id: str):
        """
        Log task progress.
        
        Args:
            task_id: Task ID
        """
        progress = self.get_task_progress(task_id)
        if not progress:
            return
        
        log.info(
            f"Task {task_id} progress: "
            f"{progress['processed']}/{progress['total']} "
            f"({progress['progress_percent']:.1f}%) - "
            f"Success: {progress['success']}, "
            f"Failed: {progress['failed']}, "
            f"Success rate: {progress['success_rate']:.1f}%"
        )
    
    def record_task_complete(self, task_id: str, status: int, failed_reason: str = ''):
        """
        Record task completion.
        
        Args:
            task_id: Task ID
            status: Task status (3=success, 4=failed)
            failed_reason: Failure reason if failed
        """
        if task_id not in self.metrics:
            log.warning(f"Task {task_id} metrics not found")
            return
        
        metrics = self.metrics[task_id]
        duration = (datetime.now() - metrics['start_time']).total_seconds()
        
        # Update database
        try:
            self.task_repo.update_task_status(
                task_id=task_id,
                status=status,
                success_cnt=metrics['success'],
                failed_reason=failed_reason
            )
        except Exception as e:
            log.error(f"Failed to update task status: {e}")
        
        # Log summary
        log.info(
            f"Task {task_id} completed - "
            f"Status: {status}, "
            f"Duration: {duration:.2f}s, "
            f"Total: {metrics['item_count']}, "
            f"Success: {metrics['success']}, "
            f"Failed: {metrics['failed']}, "
            f"Success rate: {(metrics['success'] / metrics['item_count'] * 100) if metrics['item_count'] > 0 else 0:.1f}%"
        )
        
        # Clean up metrics
        del self.metrics[task_id]
    
    def get_all_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all active tasks with progress.
        
        Returns:
            list: List of active task progress
        """
        return [
            self.get_task_progress(task_id)
            for task_id in self.metrics.keys()
        ]
    
    def get_task_statistics(self, task_id: str) -> Dict[str, Any]:
        """
        Get detailed task statistics from database.
        
        Args:
            task_id: Task ID
            
        Returns:
            dict: Task statistics
        """
        try:
            task = self.task_repo.find_one({'task_id': task_id})
            if not task:
                return {}
            
            return {
                'task_id': task['task_id'],
                'task_type': task['task_type'],
                'task_status': task['task_status'],
                'item_count': task['item_cnt'],
                'success_count': task['success_cnt'],
                'failed_reason': task['failed_reason'],
                'created_at': task['ctime'],
                'updated_at': task['mtime']
            }
        except Exception as e:
            log.error(f"Failed to get task statistics: {e}")
            return {}


# Global monitor instance
task_monitor = TaskMonitor()
