"""Base model classes."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseDBModel(BaseModel):
    """Base model for database entities."""
    
    id: Optional[int] = None
    mtime: Optional[datetime] = None
    ctime: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
        }
