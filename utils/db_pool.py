"""Database connection pool management using pymysql and DBUtils."""
import pymysql
from dbutils.pooled_db import PooledDB
from typing import Optional
from contextlib import contextmanager

from config.settings import settings
from utils.logger import log


class DatabasePool:
    """MySQL database connection pool manager."""
    
    _instance: Optional['DatabasePool'] = None
    _pool: Optional[PooledDB] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one pool instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the connection pool."""
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Create the database connection pool."""
        try:
            self._pool = PooledDB(
                creator=pymysql,
                maxconnections=settings.db_pool_max_size,
                mincached=settings.db_pool_min_size,
                maxcached=settings.db_pool_max_size,
                blocking=True,
                maxusage=None,
                setsession=[],
                ping=1,  # Check connection before using
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                database=settings.db_name,
                charset=settings.db_charset,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            log.info(f"Database pool initialized: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        except Exception as e:
            log.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            pymysql.Connection: Database connection
        """
        try:
            conn = self._pool.connection()
            return conn
        except Exception as e:
            log.error(f"Failed to get connection from pool: {e}")
            raise
    
    @contextmanager
    def get_cursor(self, commit=False):
        """
        Context manager for database cursor.
        
        Args:
            commit: Whether to commit after operations
            
        Yields:
            pymysql.cursors.DictCursor: Database cursor
            
        Example:
            with db_pool.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO ...")
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_query(self, sql: str, params: tuple = None):
        """
        Execute a SELECT query and return results.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            list: Query results as list of dictionaries
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    
    def execute_one(self, sql: str, params: tuple = None):
        """
        Execute a SELECT query and return one result.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            dict: Single result as dictionary or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()
    
    def execute_update(self, sql: str, params: tuple = None):
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            int: Number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            affected = cursor.execute(sql, params or ())
            return affected
    
    def execute_many(self, sql: str, params_list: list):
        """
        Execute batch INSERT/UPDATE/DELETE queries.
        
        Args:
            sql: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            int: Number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            affected = cursor.executemany(sql, params_list)
            return affected
    
    def check_health(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if connection is healthy
        """
        try:
            result = self.execute_one("SELECT 1 as health")
            return result is not None and result.get('health') == 1
        except Exception as e:
            log.error(f"Database health check failed: {e}")
            return False


# Global database pool instance
db_pool = DatabasePool()
