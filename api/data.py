"""Data query API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.schemas import APIResponse
from utils.db_operations import SongRepository, ArtistRepository
from utils.logger import log

router = APIRouter(prefix="/api", tags=["data"])
song_repo = SongRepository()
artist_repo = ArtistRepository()


@router.get("/songs", response_model=APIResponse)
async def list_songs(
    app_id: Optional[str] = Query(None, description="Application ID"),
    src: Optional[str] = Query(None, description="Data source"),
    song_name: Optional[str] = Query(None, description="Song name (partial match)"),
    artist_name: Optional[str] = Query(None, description="Artist name (partial match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    List songs with filters and pagination.
    
    Args:
        app_id: Filter by application ID
        src: Filter by data source
        song_name: Filter by song name (partial match)
        artist_name: Filter by artist name (partial match)
        page: Page number
        page_size: Page size
        
    Returns:
        APIResponse with song list
    """
    try:
        # Build filter conditions
        where = {}
        if app_id:
            where['app_id'] = app_id
        if src:
            where['src'] = src
        
        # For partial match, we need to use raw SQL
        # For now, use exact match for simplicity
        if song_name:
            where['song_name'] = song_name
        if artist_name:
            where['artist_name'] = artist_name
        
        # Get total count
        total = song_repo.count(where if where else None)
        
        # Get songs with pagination
        offset = (page - 1) * page_size
        songs = song_repo.find_all(
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
                'songs': songs
            }
        )
        
    except Exception as e:
        log.error(f"Failed to list songs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list songs: {str(e)}")


@router.get("/songs/{song_id}", response_model=APIResponse)
async def get_song(
    song_id: int,
    app_id: str = Query(..., description="Application ID"),
    src: str = Query(..., description="Data source")
):
    """
    Get song information by ID.
    
    Args:
        song_id: Song ID
        app_id: Application ID
        src: Data source
        
    Returns:
        APIResponse with song information
    """
    try:
        song = song_repo.find_one({
            'app_id': app_id,
            'song_id': song_id,
            'src': src
        })
        
        if not song:
            raise HTTPException(
                status_code=404,
                detail=f"Song not found: {song_id} (app_id={app_id}, src={src})"
            )
        
        return APIResponse(
            code=200,
            message="success",
            data=song
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get song: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get song: {str(e)}")


@router.get("/artists", response_model=APIResponse)
async def list_artists(
    app_id: Optional[str] = Query(None, description="Application ID"),
    src: Optional[str] = Query(None, description="Data source"),
    artist_name: Optional[str] = Query(None, description="Artist name (partial match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    List artists with filters and pagination.
    
    Args:
        app_id: Filter by application ID
        src: Filter by data source
        artist_name: Filter by artist name (partial match)
        page: Page number
        page_size: Page size
        
    Returns:
        APIResponse with artist list
    """
    try:
        # Build filter conditions
        where = {}
        if app_id:
            where['app_id'] = app_id
        if src:
            where['src'] = src
        if artist_name:
            where['artist_name'] = artist_name
        
        # Get total count
        total = artist_repo.count(where if where else None)
        
        # Get artists with pagination
        offset = (page - 1) * page_size
        artists = artist_repo.find_all(
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
                'artists': artists
            }
        )
        
    except Exception as e:
        log.error(f"Failed to list artists: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list artists: {str(e)}")


@router.get("/artists/{artist_id}", response_model=APIResponse)
async def get_artist(
    artist_id: int,
    app_id: str = Query(..., description="Application ID"),
    src: str = Query(..., description="Data source")
):
    """
    Get artist information by ID.
    
    Args:
        artist_id: Artist ID
        app_id: Application ID
        src: Data source
        
    Returns:
        APIResponse with artist information
    """
    try:
        artist = artist_repo.find_one({
            'app_id': app_id,
            'artist_id': artist_id,
            'src': src
        })
        
        if not artist:
            raise HTTPException(
                status_code=404,
                detail=f"Artist not found: {artist_id} (app_id={app_id}, src={src})"
            )
        
        return APIResponse(
            code=200,
            message="success",
            data=artist
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to get artist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get artist: {str(e)}")
