"""Data quality checking utilities."""
from typing import Dict, Any, List, Optional
from utils.db_operations import SongRepository, ArtistRepository
from utils.logger import log


class DataQualityChecker:
    """Checker for data quality and integrity."""
    
    def __init__(self):
        """Initialize quality checker."""
        self.song_repo = SongRepository()
        self.artist_repo = ArtistRepository()
    
    def check_completeness(self, data: Dict[str, Any], entity_type: str) -> tuple[bool, float, List[str]]:
        """
        Check data completeness.
        
        Args:
            data: Data dictionary to check
            entity_type: 'song' or 'artist'
            
        Returns:
            tuple: (is_complete, completeness_score, missing_fields)
        """
        if entity_type == 'song':
            important_fields = [
                'song_id', 'song_name', 'artist_name', 'src',
                'album_name', 'publish_dt', 'cover_uri'
            ]
        elif entity_type == 'artist':
            important_fields = [
                'artist_id', 'artist_name', 'src',
                'artist_country', 'artist_uri'
            ]
        else:
            return False, 0.0, []
        
        missing_fields = []
        filled_count = 0
        
        for field in important_fields:
            value = data.get(field)
            if value and value != '' and value != 0 and value != '0000-00-00':
                filled_count += 1
            else:
                missing_fields.append(field)
        
        completeness_score = filled_count / len(important_fields)
        is_complete = completeness_score >= 0.7  # At least 70% complete
        
        return is_complete, completeness_score, missing_fields
    
    def check_duplicate(self, data: Dict[str, Any], entity_type: str) -> tuple[bool, Optional[int]]:
        """
        Check if data already exists in database.
        
        Args:
            data: Data dictionary to check
            entity_type: 'song' or 'artist'
            
        Returns:
            tuple: (is_duplicate, existing_id)
        """
        try:
            if entity_type == 'song':
                # Check by app_id, song_id, and src
                existing = self.song_repo.find_one({
                    'app_id': data.get('app_id', ''),
                    'song_id': data.get('song_id', 0),
                    'src': data.get('src', '')
                })
            elif entity_type == 'artist':
                # Check by app_id, artist_id, and src
                existing = self.artist_repo.find_one({
                    'app_id': data.get('app_id', ''),
                    'artist_id': data.get('artist_id', 0),
                    'src': data.get('src', '')
                })
            else:
                return False, None
            
            if existing:
                return True, existing.get('id')
            
            return False, None
            
        except Exception as e:
            log.error(f"Error checking duplicate: {e}")
            return False, None
    
    def check_artist_exists(self, artist_name: str, app_id: str, src: str) -> bool:
        """
        Check if artist exists in database.
        
        Args:
            artist_name: Artist name to check
            app_id: Application ID
            src: Data source
            
        Returns:
            bool: True if artist exists
        """
        try:
            existing = self.artist_repo.find_one({
                'app_id': app_id,
                'artist_name': artist_name,
                'src': src
            })
            return existing is not None
        except Exception as e:
            log.error(f"Error checking artist existence: {e}")
            return False
    
    def validate_relationships(self, song_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate relationships between song and artist.
        
        Args:
            song_data: Song data dictionary
            
        Returns:
            tuple: (is_valid, warnings)
        """
        warnings = []
        
        artist_name = song_data.get('artist_name', '')
        app_id = song_data.get('app_id', '')
        src = song_data.get('src', '')
        
        if not artist_name:
            warnings.append("Song has no artist name")
            return False, warnings
        
        # Check if artist exists (optional warning, not blocking)
        if not self.check_artist_exists(artist_name, app_id, src):
            warnings.append(f"Artist '{artist_name}' not found in database")
        
        # This is just a warning, not a validation failure
        return True, warnings
    
    def calculate_data_score(self, data: Dict[str, Any], entity_type: str) -> float:
        """
        Calculate overall data quality score (0-100).
        
        Args:
            data: Data dictionary
            entity_type: 'song' or 'artist'
            
        Returns:
            float: Quality score (0-100)
        """
        score = 0.0
        
        # Completeness (50 points)
        is_complete, completeness, _ = self.check_completeness(data, entity_type)
        score += completeness * 50
        
        # Has valid ID (20 points)
        if entity_type == 'song':
            if data.get('song_id', 0) > 0:
                score += 20
        elif entity_type == 'artist':
            if data.get('artist_id', 0) > 0:
                score += 20
        
        # Has source (10 points)
        if data.get('src', ''):
            score += 10
        
        # Has name (20 points)
        if entity_type == 'song':
            if data.get('song_name', ''):
                score += 20
        elif entity_type == 'artist':
            if data.get('artist_name', ''):
                score += 20
        
        return min(score, 100.0)
    
    def should_skip_duplicate(self, existing_data: Dict[str, Any], 
                             new_data: Dict[str, Any], 
                             entity_type: str) -> bool:
        """
        Determine if duplicate should be skipped or updated.
        
        Args:
            existing_data: Existing data in database
            new_data: New data to insert
            entity_type: 'song' or 'artist'
            
        Returns:
            bool: True if should skip (existing is better), False if should update
        """
        # Calculate quality scores
        existing_score = self.calculate_data_score(existing_data, entity_type)
        new_score = self.calculate_data_score(new_data, entity_type)
        
        # Update if new data has better quality
        if new_score > existing_score:
            log.info(f"New data has better quality ({new_score:.1f} vs {existing_score:.1f}), will update")
            return False
        
        # Skip if existing data is better or equal
        log.info(f"Existing data is better or equal ({existing_score:.1f} vs {new_score:.1f}), will skip")
        return True
