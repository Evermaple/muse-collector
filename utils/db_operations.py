"""Database CRUD operations."""
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel

from utils.db_pool import db_pool
from utils.logger import log


class BaseRepository:
    """Base repository class for database operations."""
    
    def __init__(self, table_name: str):
        """
        Initialize repository.
        
        Args:
            table_name: Database table name
        """
        self.table_name = table_name
    
    def insert(self, data: Dict[str, Any]) -> int:
        """
        Insert a single record.
        
        Args:
            data: Dictionary of column-value pairs
            
        Returns:
            int: Last insert ID
        """
        if not data:
            return 0
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with db_pool.get_cursor(commit=True) as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid
    
    def insert_many(self, data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records.
        
        Args:
            data_list: List of dictionaries
            
        Returns:
            int: Number of affected rows
        """
        if not data_list:
            return 0
        
        # Use first record to get column names
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        # Convert to list of tuples
        params_list = [tuple(data.values()) for data in data_list]
        
        return db_pool.execute_many(sql, params_list)
    
    def insert_or_update(self, data: Dict[str, Any], update_fields: List[str] = None) -> int:
        """
        Insert or update on duplicate key.
        
        Args:
            data: Dictionary of column-value pairs
            update_fields: Fields to update on duplicate (if None, update all except key)
            
        Returns:
            int: Number of affected rows
        """
        if not data:
            return 0
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        
        # Build UPDATE clause
        if update_fields:
            update_clause = ', '.join([f"{field}=VALUES({field})" for field in update_fields])
        else:
            # Update all fields except those typically not updated
            skip_fields = {'id', 'ctime'}
            update_clause = ', '.join([
                f"{field}=VALUES({field})" 
                for field in data.keys() 
                if field not in skip_fields
            ])
        
        sql = f"""
            INSERT INTO {self.table_name} ({columns}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        return db_pool.execute_update(sql, tuple(data.values()))
    
    def insert_or_update_many(self, data_list: List[Dict[str, Any]], 
                             update_fields: List[str] = None) -> int:
        """
        Batch insert or update on duplicate key.
        
        Args:
            data_list: List of dictionaries
            update_fields: Fields to update on duplicate
            
        Returns:
            int: Number of affected rows
        """
        if not data_list:
            return 0
        
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        
        # Build UPDATE clause
        if update_fields:
            update_clause = ', '.join([f"{field}=VALUES({field})" for field in update_fields])
        else:
            skip_fields = {'id', 'ctime'}
            update_clause = ', '.join([
                f"{field}=VALUES({field})" 
                for field in data_list[0].keys() 
                if field not in skip_fields
            ])
        
        sql = f"""
            INSERT INTO {self.table_name} ({columns}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        params_list = [tuple(data.values()) for data in data_list]
        return db_pool.execute_many(sql, params_list)
    
    def update(self, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        Update records.
        
        Args:
            data: Dictionary of column-value pairs to update
            where: Dictionary of WHERE conditions
            
        Returns:
            int: Number of affected rows
        """
        if not data or not where:
            return 0
        
        set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
        where_clause = ' AND '.join([f"{k}=%s" for k in where.keys()])
        
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        params = tuple(list(data.values()) + list(where.values()))
        
        return db_pool.execute_update(sql, params)
    
    def delete(self, where: Dict[str, Any]) -> int:
        """
        Delete records.
        
        Args:
            where: Dictionary of WHERE conditions
            
        Returns:
            int: Number of affected rows
        """
        if not where:
            raise ValueError("WHERE clause is required for DELETE")
        
        where_clause = ' AND '.join([f"{k}=%s" for k in where.keys()])
        sql = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        
        return db_pool.execute_update(sql, tuple(where.values()))
    
    def find_one(self, where: Dict[str, Any] = None, 
                 columns: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find one record.
        
        Args:
            where: Dictionary of WHERE conditions
            columns: List of columns to select (None for all)
            
        Returns:
            dict: Record as dictionary or None
        """
        select_clause = ', '.join(columns) if columns else '*'
        
        if where:
            where_clause = ' AND '.join([f"{k}=%s" for k in where.keys()])
            sql = f"SELECT {select_clause} FROM {self.table_name} WHERE {where_clause} LIMIT 1"
            return db_pool.execute_one(sql, tuple(where.values()))
        else:
            sql = f"SELECT {select_clause} FROM {self.table_name} LIMIT 1"
            return db_pool.execute_one(sql)
    
    def find_all(self, where: Dict[str, Any] = None, 
                 columns: List[str] = None,
                 order_by: str = None,
                 limit: int = None,
                 offset: int = None) -> List[Dict[str, Any]]:
        """
        Find multiple records.
        
        Args:
            where: Dictionary of WHERE conditions
            columns: List of columns to select
            order_by: ORDER BY clause (e.g., "id DESC")
            limit: LIMIT value
            offset: OFFSET value
            
        Returns:
            list: List of records as dictionaries
        """
        select_clause = ', '.join(columns) if columns else '*'
        sql = f"SELECT {select_clause} FROM {self.table_name}"
        params = []
        
        if where:
            where_clause = ' AND '.join([f"{k}=%s" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            params.extend(where.values())
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
            if offset:
                sql += f" OFFSET {offset}"
        
        return db_pool.execute_query(sql, tuple(params) if params else None)
    
    def count(self, where: Dict[str, Any] = None) -> int:
        """
        Count records.
        
        Args:
            where: Dictionary of WHERE conditions
            
        Returns:
            int: Number of records
        """
        sql = f"SELECT COUNT(*) as cnt FROM {self.table_name}"
        
        if where:
            where_clause = ' AND '.join([f"{k}=%s" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            result = db_pool.execute_one(sql, tuple(where.values()))
        else:
            result = db_pool.execute_one(sql)
        
        return result['cnt'] if result else 0
    
    def exists(self, where: Dict[str, Any]) -> bool:
        """
        Check if record exists.
        
        Args:
            where: Dictionary of WHERE conditions
            
        Returns:
            bool: True if exists
        """
        return self.count(where) > 0


# Specific repositories
class TaskRepository(BaseRepository):
    """Repository for crawl_task table."""
    
    def __init__(self):
        super().__init__('crawl_task')
    
    def find_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find pending tasks (status=1)."""
        return self.find_all(
            where={'task_status': 1},
            order_by='ctime ASC',
            limit=limit
        )
    
    def update_task_status(self, task_id: str, status: int, 
                          success_cnt: int = None, failed_reason: str = None) -> int:
        """Update task status and statistics."""
        data = {'task_status': status}
        if success_cnt is not None:
            data['success_cnt'] = success_cnt
        if failed_reason:
            data['failed_reason'] = failed_reason
        
        return self.update(data, {'task_id': task_id})


class SongRepository(BaseRepository):
    """Repository for song_info table."""
    
    def __init__(self):
        super().__init__('song_info')


class ArtistRepository(BaseRepository):
    """Repository for artist_info table."""
    
    def __init__(self):
        super().__init__('artist_info')


class SongSnapRepository(BaseRepository):
    """Repository for song_crawl_snap table."""
    
    def __init__(self):
        super().__init__('song_crawl_snap')


class ArtistSnapRepository(BaseRepository):
    """Repository for artist_crawl_snap table."""
    
    def __init__(self):
        super().__init__('artist_crawl_snap')
