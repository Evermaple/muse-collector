"""Crawl task model."""
from typing import Optional, List
from pydantic import Field, field_validator
from models.base import BaseDBModel


class CrawlTask(BaseDBModel):
    """
    Crawl task model.
    
    Task Status:
        1 = Waiting
        2 = Running
        3 = Success
        4 = Failed
        5 = Cancelled
    
    Task Type:
        1 = Song
        2 = Artist
    """
    
    app_id: str = Field(default="", max_length=32, description="Application ID")
    task_id: str = Field(default="", max_length=32, description="Task ID")
    task_type: str = Field(default="", max_length=16, description="Task type: 1=song, 2=artist")
    srcs: str = Field(default="", max_length=2000, description="Target data sources (comma separated)")
    target_ids: str = Field(default="", max_length=2000, description="Target IDs (comma separated)")
    task_status: int = Field(default=1, description="Task status")
    failed_reason: str = Field(default="", max_length=200, description="Failure reason")
    item_cnt: int = Field(default=0, description="Total item count")
    success_cnt: int = Field(default=0, description="Success count")
    
    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        """Validate task type."""
        if v not in ['1', '2', 'song', 'artist']:
            raise ValueError("task_type must be '1' (song) or '2' (artist)")
        return v
    
    @field_validator('task_status')
    @classmethod
    def validate_task_status(cls, v: int) -> int:
        """Validate task status."""
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError("task_status must be between 1 and 5")
        return v
    
    def get_src_list(self) -> List[str]:
        """Get list of data sources."""
        if not self.srcs:
            return []
        return [s.strip() for s in self.srcs.split(',') if s.strip()]
    
    def get_target_id_list(self) -> List[str]:
        """Get list of target IDs."""
        if not self.target_ids:
            return []
        return [tid.strip() for tid in self.target_ids.split(',') if tid.strip()]
    
    @staticmethod
    def format_src_list(src_list: List[str]) -> str:
        """Format source list to comma-separated string."""
        return ','.join(src_list)
    
    @staticmethod
    def format_target_id_list(id_list: List[str]) -> str:
        """Format target ID list to comma-separated string."""
        return ','.join(str(tid) for tid in id_list)
