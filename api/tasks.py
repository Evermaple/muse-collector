"""Task management API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import uuid
from datetime import datetime

from api.schemas import (
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    APIResponse
)
from utils.db_operations import TaskRepository
from utils.logger import log
from models.task import CrawlTask

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
task_repo = TaskRepository()


@router.post("", response_model=APIResponse)
async def create_task(request: TaskCreateRequest):
    """
    Create a new crawl task.
    
    Args:
        request: Task creation request
        
    Returns:
        APIResponse with task_id
    """
    try:
        # Generate unique task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Format sources and target IDs
        srcs_str = ','.join(request.srcs)
        target_ids_str = ','.join(request.target_ids)
        
        # Create task data
        task_data = {
            'app_id': request.app_id,
            'task_id': task_id,
            'task_type': request.task_type,
            'srcs': srcs_str,
            'target_ids': target_ids_str,
            'task_status': 1,  # Waiting
            'item_cnt': len(request.target_ids),
            'success_cnt': 0,
            'failed_reason': ''
        }
        
        # Insert into database
        task_repo.insert(task_data)
        
        log.info(f"Task created: {task_id}, type: {request.task_type}, items: {len(request.target_ids)}")
        
        return APIResponse(
            code=200,
            message="Task created successfully",
            data={'task_id': task_id}
        )
        
    except Exception as e:
        log.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.get("/{task_id}", response_model=APIResponse)
async def get_task(task_id: str):
    """
    Get task information by task ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        APIResponse with task information
    """
    try:
        task = task_repo.find_one({'task_id': task_id})
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
        
        return APIResponse(
            code=200,
            message="success",
            data=task
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@router.get("", response_model=APIResponse)
async def list_tasks(
    app_id: Optional[str] = Query(None, description="Application ID"),
    task_type: Optional[str] = Query(None, description="Task type"),
    task_status: Optional[int] = Query(None, description="Task status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    List tasks with filters and pagination.
    
    Args:
        app_id: Filter by application ID
        task_type: Filter by task type
        task_status: Filter by task status
        page: Page number
        page_size: Page size
        
    Returns:
        APIResponse with task list
    """
    try:
        # Build filter conditions
        where = {}
        if app_id:
            where['app_id'] = app_id
        if task_type:
            where['task_type'] = task_type
        if task_status is not None:
            where['task_status'] = task_status
        
        # Get total count
        total = task_repo.count(where if where else None)
        
        # Get tasks with pagination
        offset = (page - 1) * page_size
        tasks = task_repo.find_all(
            where=where if where else None,
            order_by='ctime DESC',
            limit=page_size,
            offset=offset
        )
        
        return APIResponse(
            code=200,
            message="success",
            data={
                'total': total,
                'page': page,
                'page_size': page_size,
                'tasks': tasks
            }
        )
        
    except Exception as e:
        log.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@router.put("/{task_id}/cancel", response_model=APIResponse)
async def cancel_task(task_id: str):
    """
    Cancel a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        APIResponse
    """
    try:
        # Check if task exists
        task = task_repo.find_one({'task_id': task_id})
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
        
        # Check if task can be cancelled
        current_status = task['task_status']
        if current_status in [3, 4, 5]:  # Success, Failed, or already Cancelled
            raise HTTPException(
                status_code=400,
                detail=f"Task cannot be cancelled (current status: {current_status})"
            )
        
        # Update task status to cancelled (5)
        affected = task_repo.update_task_status(
            task_id=task_id,
            status=5,
            failed_reason='Cancelled by user'
        )
        
        if affected == 0:
            raise HTTPException(status_code=500, detail="Failed to cancel task")
        
        log.info(f"Task cancelled: {task_id}")
        
        return APIResponse(
            code=200,
            message="Task cancelled successfully",
            data={'task_id': task_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to cancel task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@router.post("/{task_id}/retry", response_model=APIResponse)
async def retry_task(task_id: str):
    """
    Retry a failed task.
    
    Args:
        task_id: Task ID
        
    Returns:
        APIResponse
    """
    try:
        # Check if task exists
        task = task_repo.find_one({'task_id': task_id})
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
        
        # Check if task can be retried
        current_status = task['task_status']
        if current_status not in [4, 5]:  # Only Failed or Cancelled tasks can be retried
            raise HTTPException(
                status_code=400,
                detail=f"Task cannot be retried (current status: {current_status})"
            )
        
        # Reset task status to waiting (1)
        affected = task_repo.update_task_status(
            task_id=task_id,
            status=1,
            success_cnt=0,
            failed_reason=''
        )
        
        if affected == 0:
            raise HTTPException(status_code=500, detail="Failed to retry task")
        
        log.info(f"Task retry initiated: {task_id}")
        
        return APIResponse(
            code=200,
            message="Task retry initiated successfully",
            data={'task_id': task_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retry task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retry task: {str(e)}")
