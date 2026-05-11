"""Netease Cloud Music adapter."""
from typing import Dict, Any, Optional
from worker.adapters.base import DataSourceAdapter
from utils.logger import log


class NeteaseAdapter(DataSourceAdapter):
    """Adapter for Netease Cloud Music API."""
    
    def __init__(self, base_url: str = "https://music.163.com/api", 
                 timeout: int = 30, rate_limit: int = 100):
        """Initialize Netease adapter."""
        super().__init__(base_url, timeout, rate_limit)
    
    def fetch_song(self, song_id: int, search_key: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch song information from Netease.
        
        Args:
            song_id: Netease song ID
            search_key: Optional search keyword (not used for direct fetch)
            
        Returns:
            dict: Parsed song data or None
        """
        try:
            # Netease song detail API endpoint
            endpoint = "/song/detail"
            params = {
                'ids': f'[{song_id}]'
            }
            
            response = self.get(endpoint, params)
            
            # Check if response is valid
            if response.get('code') != 200:
                log.warning(f"Netease API returned error code: {response.get('code')}")
                return None
            
            songs = response.get('songs', [])
            if not songs:
                log.warning(f"Song not found: {song_id}")
                return None
            
            raw_song = songs[0]
            return self.parse_song_data(raw_song)
            
        except Exception as e:
            log.error(f"Failed to fetch song {song_id} from Netease: {e}")
            return None
    
    def fetch_artist(self, artist_id: int, search_key: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch artist information from Netease.
        
        Args:
            artist_id: Netease artist ID
            search_key: Optional search keyword (not used for direct fetch)
            
        Returns:
            dict: Parsed artist data or None
        """
        try:
            # Netease artist detail API endpoint
            endpoint = "/artist"
            params = {
                'id': artist_id
            }
            
            response = self.get(endpoint, params)
            
            # Check if response is valid
            if response.get('code') != 200:
                log.warning(f"Netease API returned error code: {response.get('code')}")
                return None
            
            artist = response.get('artist')
            if not artist:
                log.warning(f"Artist not found: {artist_id}")
                return None
            
            return self.parse_artist_data(artist)
            
        except Exception as e:
            log.error(f"Failed to fetch artist {artist_id} from Netease: {e}")
            return None
    
    def parse_song_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Netease song data to standard format.
        
        Args:
            raw_data: Raw song data from Netease API
            
        Returns:
            dict: Standardized song data
        """
        try:
            # Extract album info
            album = raw_data.get('album', {})
            album_name = album.get('name', '')
            cover_uri = album.get('picUrl', '')
            publish_time = album.get('publishTime', 0)
            
            # Convert timestamp to date string
            if publish_time:
                from datetime import datetime
                publish_dt = datetime.fromtimestamp(publish_time / 1000).strftime('%Y-%m-%d')
            else:
                publish_dt = '0000-00-00'
            
            # Extract artists
            artists = raw_data.get('artists', [])
            artist_names = [a.get('name', '') for a in artists]
            artist_name = ', '.join(artist_names) if artist_names else ''
            
            # Get song type/genre (if available)
            song_type = '0'  # Default, Netease doesn't provide direct genre in song detail
            
            # Language detection (simplified)
            lang = ''  # Would need additional logic or API call
            
            return {
                'song_id': raw_data.get('id', 0),
                'song_name': raw_data.get('name', ''),
                'artist_name': artist_name,
                'publish_dt': publish_dt,
                'song_type': song_type,
                'lang': lang,
                'album_name': album_name,
                'cover_uri': cover_uri,
                'lyricist': '',  # Would need lyrics API
                'composer': '',  # Would need lyrics API
                'keyword': '',
                'sort_tag': '',
                'src_uri': f"https://music.163.com/#/song?id={raw_data.get('id', 0)}",
                'src_id': str(raw_data.get('id', 0))
            }
        except Exception as e:
            log.error(f"Failed to parse song data: {e}")
            raise
    
    def parse_artist_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Netease artist data to standard format.
        
        Args:
            raw_data: Raw artist data from Netease API
            
        Returns:
            dict: Standardized artist data
        """
        try:
            # Extract basic info
            artist_id = raw_data.get('id', 0)
            artist_name = raw_data.get('name', '')
            artist_alias = ', '.join(raw_data.get('alias', []))
            artist_uri = raw_data.get('picUrl', '')
            
            # Gender: Netease doesn't provide this directly
            artist_gender = 0
            
            # Country/Region
            artist_country = ''
            
            # Debut year - not directly available
            debug_year = '0000'
            
            # Check if group
            is_group = 1 if raw_data.get('albumSize', 0) > 0 else 0
            
            return {
                'artist_id': artist_id,
                'artist_name': artist_name,
                'artist_alias': artist_alias,
                'artist_secondary_name': '',
                'artist_gender': artist_gender,
                'artist_country': artist_country,
                'debug_year': debug_year,
                'is_group': is_group,
                'main_artist': '',
                'artist_uri': artist_uri,
                'sort_tag': '',
                'src_uri': f"https://music.163.com/#/artist?id={artist_id}",
                'src_id': str(artist_id)
            }
        except Exception as e:
            log.error(f"Failed to parse artist data: {e}")
            raise
