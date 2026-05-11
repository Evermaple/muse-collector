"""Artist related models."""
from typing import Optional
from pydantic import Field
from models.base import BaseDBModel


class ArtistInfo(BaseDBModel):
    """Artist information model."""
    
    app_id: str = Field(default="", max_length=32, description="Application ID")
    src: str = Field(default="", max_length=32, description="Data source")
    artist_id: int = Field(default=0, description="Artist ID")
    artist_name: str = Field(default="", max_length=128, description="Artist name")
    artist_alias: str = Field(default="", max_length=128, description="Artist alias")
    artist_secondary_name: str = Field(default="", max_length=128, description="Artist secondary name")
    artist_gender: int = Field(default=0, description="Artist gender: 1=male, 2=female")
    artist_country: str = Field(default="", max_length=64, description="Artist country")
    debug_year: str = Field(default="0000", max_length=32, description="Debut year")
    is_group: int = Field(default=0, description="Is group: 0=no, 1=yes")
    main_artist: str = Field(default="", max_length=32, description="Main artist")
    artist_uri: str = Field(default="", max_length=512, description="Artist image URI")
    sort_tag: str = Field(default="", max_length=32, description="Sort tag")


class ArtistCrawlSnap(BaseDBModel):
    """
    Artist crawl snapshot model.
    
    Process Status:
        0 = Initial
        1 = Waiting
        2 = Processing
        3 = Success
        4 = Failed
        5 = Skipped
    """
    
    src: str = Field(default="", max_length=32, description="Data source")
    artist_id: int = Field(default=0, description="Artist ID")
    artist_name: str = Field(default="", max_length=128, description="Artist name")
    artist_alias: str = Field(default="", max_length=128, description="Artist alias")
    artist_secondary_name: str = Field(default="", max_length=128, description="Artist secondary name")
    artist_gender: int = Field(default=0, description="Artist gender: 1=male, 2=female")
    artist_country: str = Field(default="", max_length=64, description="Artist country")
    debug_year: str = Field(default="0000", max_length=32, description="Debut year")
    is_group: int = Field(default=0, description="Is group: 0=no, 1=yes")
    main_artist: str = Field(default="", max_length=32, description="Main artist")
    artist_uri: str = Field(default="", max_length=512, description="Artist image URI")
    sort_tag: str = Field(default="", max_length=32, description="Sort tag")
    search_key: str = Field(default="", max_length=200, description="Search key")
    src_uri: str = Field(default="", max_length=500, description="Source URI")
    src_id: str = Field(default="", max_length=32, description="Source ID")
    task_id: str = Field(default="", max_length=32, description="Task ID")
    process_status: int = Field(default=0, description="Process status")
    failed_reason: str = Field(default="", max_length=200, description="Failure reason")
    
    def to_artist_info(self, app_id: str) -> ArtistInfo:
        """Convert snapshot to ArtistInfo."""
        return ArtistInfo(
            app_id=app_id,
            src=self.src,
            artist_id=self.artist_id,
            artist_name=self.artist_name,
            artist_alias=self.artist_alias,
            artist_secondary_name=self.artist_secondary_name,
            artist_gender=self.artist_gender,
            artist_country=self.artist_country,
            debug_year=self.debug_year,
            is_group=self.is_group,
            main_artist=self.main_artist,
            artist_uri=self.artist_uri,
            sort_tag=self.sort_tag
        )
