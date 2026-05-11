"""Data processing and validation for crawler."""
from typing import Dict, Any, Optional
from utils.validator import FieldValidator
from utils.data_quality import DataQualityChecker
from utils.db_operations import SongSnapRepository, ArtistSnapRepository
from utils.logger import log


class DataProcessor:
    """Process and validate crawled data before saving."""
    
    def __init__(self):
        """Initialize data processor."""
        self.validator = FieldValidator()
        self.quality_checker = DataQualityChecker()
        self.song_snap_repo = SongSnapRepository()
        self.artist_snap_repo = ArtistSnapRepository()
    
    def process_song_data(self, raw_data: Dict[str, Any], task_id: str, 
                         src: str, search_key: str = '') -> tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Process and validate song data.
        
        Args:
            raw_data: Raw song data from adapter
            task_id: Task ID
            src: Data source
            search_key: Search keyword
            
        Returns:
            tuple: (is_valid, processed_data, error_message)
        """
        try:
            # Add metadata
            processed_data = raw_data.copy()
            processed_data['task_id'] = task_id
            processed_data['src'] = src
            processed_data['search_key'] = search_key
            processed_data['process_status'] = 1  # Waiting
            
            # Normalize date format
            if 'publish_dt' in processed_data:
                processed_data['publish_dt'] = self.validator.normalize_date(
                    processed_data['publish_dt']
                )
            
            # Validate required fields
            is_valid, errors = self.validator.validate_song_data(processed_data)
            if not is_valid:
                error_msg = '; '.join(errors)
                log.warning(f"Song validation failed: {error_msg}")
                processed_data['process_status'] = 4  # Failed
                processed_data['failed_reason'] = error_msg[:200]
                return False, processed_data, error_msg
            
            # Check data completeness
            is_complete, score, missing = self.quality_checker.check_completeness(
                processed_data, 'song'
            )
            
            if not is_complete:
                log.warning(f"Song data incomplete (score: {score:.2f}), missing: {missing}")
                # Still save but mark as incomplete
                processed_data['process_status'] = 1  # Waiting (can be improved later)
            else:
                processed_data['process_status'] = 3  # Success
            
            log.info(f"Song data processed successfully (quality score: {score:.2f})")
            return True, processed_data, ""
            
        except Exception as e:
            error_msg = f"Error processing song data: {e}"
            log.error(error_msg)
            return False, None, error_msg
    
    def process_artist_data(self, raw_data: Dict[str, Any], task_id: str, 
                           src: str, search_key: str = '') -> tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Process and validate artist data.
        
        Args:
            raw_data: Raw artist data from adapter
            task_id: Task ID
            src: Data source
            search_key: Search keyword
            
        Returns:
            tuple: (is_valid, processed_data, error_message)
        """
        try:
            # Add metadata
            processed_data = raw_data.copy()
            processed_data['task_id'] = task_id
            processed_data['src'] = src
            processed_data['search_key'] = search_key
            processed_data['process_status'] = 1  # Waiting
            
            # Validate required fields
            is_valid, errors = self.validator.validate_artist_data(processed_data)
            if not is_valid:
                error_msg = '; '.join(errors)
                log.warning(f"Artist validation failed: {error_msg}")
                processed_data['process_status'] = 4  # Failed
                processed_data['failed_reason'] = error_msg[:200]
                return False, processed_data, error_msg
            
            # Check data completeness
            is_complete, score, missing = self.quality_checker.check_completeness(
                processed_data, 'artist'
            )
            
            if not is_complete:
                log.warning(f"Artist data incomplete (score: {score:.2f}), missing: {missing}")
                processed_data['process_status'] = 1  # Waiting
            else:
                processed_data['process_status'] = 3  # Success
            
            log.info(f"Artist data processed successfully (quality score: {score:.2f})")
            return True, processed_data, ""
            
        except Exception as e:
            error_msg = f"Error processing artist data: {e}"
            log.error(error_msg)
            return False, None, error_msg
    
    def save_song_snap(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Save song data to snapshot table.
        
        Args:
            data: Processed song data
            
        Returns:
            int: Inserted ID or None if failed
        """
        try:
            # Remove fields that don't exist in snap table
            snap_data = {k: v for k, v in data.items() if k not in ['id', 'app_id', 'mtime', 'ctime']}
            
            snap_id = self.song_snap_repo.insert(snap_data)
            log.info(f"Song snap saved with ID: {snap_id}")
            return snap_id
            
        except Exception as e:
            log.error(f"Failed to save song snap: {e}")
            return None
    
    def save_artist_snap(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Save artist data to snapshot table.
        
        Args:
            data: Processed artist data
            
        Returns:
            int: Inserted ID or None if failed
        """
        try:
            # Remove fields that don't exist in snap table
            snap_data = {k: v for k, v in data.items() if k not in ['id', 'app_id', 'mtime', 'ctime']}
            
            snap_id = self.artist_snap_repo.insert(snap_data)
            log.info(f"Artist snap saved with ID: {snap_id}")
            return snap_id
            
        except Exception as e:
            log.error(f"Failed to save artist snap: {e}")
            return None
    
    def update_snap_status(self, snap_id: int, entity_type: str, 
                          status: int, failed_reason: str = '') -> bool:
        """
        Update snapshot status.
        
        Args:
            snap_id: Snapshot ID
            entity_type: 'song' or 'artist'
            status: Process status
            failed_reason: Failure reason
            
        Returns:
            bool: True if updated successfully
        """
        try:
            data = {'process_status': status}
            if failed_reason:
                data['failed_reason'] = failed_reason[:200]
            
            if entity_type == 'song':
                affected = self.song_snap_repo.update(data, {'id': snap_id})
            elif entity_type == 'artist':
                affected = self.artist_snap_repo.update(data, {'id': snap_id})
            else:
                return False
            
            return affected > 0
            
        except Exception as e:
            log.error(f"Failed to update snap status: {e}")
            return False
