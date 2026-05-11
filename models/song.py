"""Song related models."""
from typing import Optional
from pydantic import Field
from models.base import BaseDBModel


class SongInfo(BaseDBModel):
    """Song information model."""
    
    app_id: str = Field(default="", max_length=32, description="Application ID")
    src: str = Field(default="", max_length=32, description="Data source")
    song_id: int = Field(default=0, description="Song ID")
    song_name: str = Field(default="", max_length=128, description="Song name")
    artist_name: str = Field(default="", max_length=128, description="Artist name")
    publish_dt: str = Field(default="0000-00-00", max_length=32, description="Publish date")
    song_type: str = Field(default="0", max_length=32, description="Song type")
    lang: str = Field(default="", max_length=32, description="Language")
    album_name: str = Field(default="", max_length=128, description="Album name")
    cover_uri: str = Field(default="", max_length=500, description="Cover image URI")
    lyricist: str = Field(default="", max_length=200, description="Lyricist")
    composer: str = Field(default="", max_length=200, description="Composer")
    keyword: str = Field(default="", max_length=200, description="Keywords")
    sort_tag: str = Field(default="", max_length=32, description="Sort tag")


class SongCrawlSnap(BaseDBModel):
    """
    Song crawl snapshot model.
    
    Process Status:
        0 = Initial
        1 = Waiting
        2 = Processing
        3 = Success
        4 = Failed
        5 = Skipped
    """
    
    src: str = Field(default="", max_length=32, description="Data source")
    song_id: int = Field(default=0, description="Song ID")
    song_name: str = Field(default="", max_length=128, description="Song name")
    artist_name: str = Field(default="", max_length=128, description="Artist name")
    publish_dt: str = Field(default="0000-00-00", max_length=32, description="Publish date")
    song_type: str = Field(default="0", max_length=32, description="Song type")
    lang: str = Field(default="", max_length=32, description="Language")
    album_name: str = Field(default="", max_length=128, description="Album name")
    cover_uri: str = Field(default="", max_length=500, description="Cover image URI")
    lyricist: str = Field(default="", max_length=200, description="Lyricist")
    composer: str = Field(default="", max_length=200, description="Composer")
    keyword: str = Field(default="", max_length=200, description="Keywords")
    sort_tag: str = Field(default="", max_length=32, description="Sort tag")
    search_key: str = Field(default="", max_length=200, description="Search key")
    src_uri: str = Field(default="", max_length=500, description="Source URI")
    src_id: str = Field(default="", max_length=32, description="Source ID")
    task_id: str = Field(default="", max_length=32, description="Task ID")
    process_status: int = Field(default=0, description="Process status")
    failed_reason: str = Field(default="", max_length=200, description="Failure reason")
    
    def to_song_info(self, app_id: str) -> SongInfo:
        """Convert snapshot to SongInfo."""
        return SongInfo(
            app_id=app_id,
            src=self.src,
            song_id=self.song_id,
            song_name=self.song_name,
            artist_name=self.artist_name,
            publish_dt=self.publish_dt,
            song_type=self.song_type,
            lang=self.lang,
            album_name=self.album_name,
            cover_uri=self.cover_uri,
            lyricist=self.lyricist,
            composer=self.composer,
            keyword=self.keyword,
            sort_tag=self.sort_tag
        )
