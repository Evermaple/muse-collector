"""Data validation utilities."""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger import log


class FieldValidator:
    """Validator for data fields."""
    
    # Required fields for different entity types
    SONG_REQUIRED_FIELDS = ['song_id', 'song_name', 'src']
    ARTIST_REQUIRED_FIELDS = ['artist_id', 'artist_name', 'src']
    
    # Date format patterns
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
        r'^\d{4}\d{2}\d{2}$',    # YYYYMMDD
    ]
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
        """
        Validate that all required fields are present and not empty.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            tuple: (is_valid, missing_fields)
        """
        missing_fields = []
        
        for field in required_fields:
            value = data.get(field)
            
            # Check if field exists and is not empty
            if value is None or value == '' or value == 0:
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    @staticmethod
    def validate_string_length(value: str, max_length: int, field_name: str = '') -> tuple[bool, str]:
        """
        Validate string length.
        
        Args:
            value: String value to validate
            max_length: Maximum allowed length
            field_name: Field name for error message
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"{field_name}: value must be string"
        
        if len(value) > max_length:
            return False, f"{field_name}: length exceeds {max_length} characters"
        
        return True, ""
    
    @staticmethod
    def validate_integer_range(value: int, min_val: int = None, max_val: int = None, 
                               field_name: str = '') -> tuple[bool, str]:
        """
        Validate integer value range.
        
        Args:
            value: Integer value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Field name for error message
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(value, int):
            return False, f"{field_name}: value must be integer"
        
        if min_val is not None and value < min_val:
            return False, f"{field_name}: value must be >= {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"{field_name}: value must be <= {max_val}"
        
        return True, ""
    
    @staticmethod
    def validate_date_format(date_str: str, field_name: str = '') -> tuple[bool, str]:
        """
        Validate date format.
        
        Args:
            date_str: Date string to validate
            field_name: Field name for error message
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not date_str or date_str == '0000-00-00':
            return True, ""  # Allow empty dates
        
        # Check against known patterns
        for pattern in FieldValidator.DATE_PATTERNS:
            if re.match(pattern, date_str):
                return True, ""
        
        return False, f"{field_name}: invalid date format (expected YYYY-MM-DD)"
    
    @staticmethod
    def normalize_date(date_str: str) -> str:
        """
        Normalize date string to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            str: Normalized date string or '0000-00-00' if invalid
        """
        if not date_str or date_str == '0000-00-00':
            return '0000-00-00'
        
        # Try to parse and reformat
        try:
            # Remove common separators and try to parse
            clean_date = date_str.replace('/', '-')
            
            # Try parsing with different formats
            for fmt in ['%Y-%m-%d', '%Y%m%d']:
                try:
                    dt = datetime.strptime(clean_date, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return '0000-00-00'
        except Exception:
            return '0000-00-00'
    
    @staticmethod
    def validate_song_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate song data.
        
        Args:
            data: Song data dictionary
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        is_valid, missing = FieldValidator.validate_required_fields(
            data, FieldValidator.SONG_REQUIRED_FIELDS
        )
        if not is_valid:
            errors.append(f"Missing required fields: {', '.join(missing)}")
        
        # Validate field lengths
        string_fields = {
            'song_name': 128,
            'artist_name': 128,
            'album_name': 128,
            'lang': 32,
            'song_type': 32,
            'lyricist': 200,
            'composer': 200,
            'keyword': 200,
            'cover_uri': 500,
        }
        
        for field, max_len in string_fields.items():
            value = data.get(field, '')
            if value:
                valid, msg = FieldValidator.validate_string_length(value, max_len, field)
                if not valid:
                    errors.append(msg)
        
        # Validate date format
        publish_dt = data.get('publish_dt', '')
        if publish_dt:
            valid, msg = FieldValidator.validate_date_format(publish_dt, 'publish_dt')
            if not valid:
                errors.append(msg)
        
        # Validate song_id
        song_id = data.get('song_id', 0)
        if song_id:
            valid, msg = FieldValidator.validate_integer_range(song_id, min_val=1, field_name='song_id')
            if not valid:
                errors.append(msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_artist_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate artist data.
        
        Args:
            data: Artist data dictionary
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        is_valid, missing = FieldValidator.validate_required_fields(
            data, FieldValidator.ARTIST_REQUIRED_FIELDS
        )
        if not is_valid:
            errors.append(f"Missing required fields: {', '.join(missing)}")
        
        # Validate field lengths
        string_fields = {
            'artist_name': 128,
            'artist_alias': 128,
            'artist_secondary_name': 128,
            'artist_country': 64,
            'debug_year': 32,
            'main_artist': 32,
            'artist_uri': 512,
        }
        
        for field, max_len in string_fields.items():
            value = data.get(field, '')
            if value:
                valid, msg = FieldValidator.validate_string_length(value, max_len, field)
                if not valid:
                    errors.append(msg)
        
        # Validate artist_id
        artist_id = data.get('artist_id', 0)
        if artist_id:
            valid, msg = FieldValidator.validate_integer_range(artist_id, min_val=1, field_name='artist_id')
            if not valid:
                errors.append(msg)
        
        # Validate gender (0, 1, or 2)
        gender = data.get('artist_gender', 0)
        if gender:
            valid, msg = FieldValidator.validate_integer_range(gender, min_val=0, max_val=2, field_name='artist_gender')
            if not valid:
                errors.append(msg)
        
        # Validate is_group (0 or 1)
        is_group = data.get('is_group', 0)
        if is_group not in [0, 1]:
            errors.append("is_group: must be 0 or 1")
        
        return len(errors) == 0, errors
