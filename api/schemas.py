"""API request and response schemas."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TaskCreateRequest(BaseModel):
    """Request schema for creating a task."""
    app_id: str = Field(..., description="Application ID", max_length=32)
    task_type: str = Field(..., description="Task type: 1=song, 2=artist", pattern="^[12]$")
    srcs: List[str] = Field(..., description="List of data sources", min_items=1)
    target_ids: List[str] = Field(..., description="List of target IDs", min_items=1)


class TaskResponse(BaseModel):
    """Response schema for task information."""
    id: int
    app_id: str
    task_id: str
    task_type: str
    srcs: str
    target_ids: str
    task_status: int
    failed_reason: str
    item_cnt: int
    success_cnt: int
    ctime: datetime
    mtime: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response schema for task list."""
    total: int
    tasks: List[TaskResponse]


class TaskProgressResponse(BaseModel):
    """Response schema for task progress."""
    task_id: str
    task_status: int
    total: int
    processed: int
    success: int
    failed: int
    progress_percent: float
    success_rate: float


class SongResponse(BaseModel):
    """Response schema for song information."""
    id: int
    app_id: str
    src: str
    song_id: int
    song_name: str
    artist_name: str
    publish_dt: str
    song_type: str
    lang: str
    album_name: str
    cover_uri: str
    lyricist: str
    composer: str
    keyword: str
    sort_tag: str
    ctime: datetime
    mtime: datetime
    
    class Config:
        from_attributes = True


class SongListResponse(BaseModel):
    """Response schema for song list."""
    total: int
    page: int
    page_size: int
    songs: List[SongResponse]


class ArtistResponse(BaseModel):
    """Response schema for artist information."""
    id: int
    app_id: str
    src: str
    artist_id: int
    artist_name: str
    artist_alias: str
    artist_secondary_name: str
    artist_gender: int
    artist_country: str
    debug_year: str
    is_group: int
    main_artist: str
    artist_uri: str
    sort_tag: str
    ctime: datetime
    mtime: datetime
    
    class Config:
        from_attributes = True


class ArtistListResponse(BaseModel):
    """Response schema for artist list."""
    total: int
    page: int
    page_size: int
    artists: List[ArtistResponse]


class APIResponse(BaseModel):
    """Generic API response."""
    code: int = Field(default=200, description="Response code")
    message: str = Field(default="success", description="Response message")
    data: Optional[dict] = Field(default=None, description="Response data")
