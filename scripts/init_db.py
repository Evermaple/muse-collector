#!/usr/bin/env python3
"""Database initialization script."""
import sys
import pymysql
from pathlib import Path
from config.settings import settings
from utils.logger import log


def read_sql_file(file_path: str) -> list:
    """
    Read SQL file and split into individual statements.
    
    Args:
        file_path: Path to SQL file
        
    Returns:
        list: List of SQL statements
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by semicolon and filter empty statements
    statements = [
        stmt.strip() 
        for stmt in content.split(';') 
        if stmt.strip() and not stmt.strip().startswith('--')
    ]
    
    return statements


def execute_sql_file(connection, file_path: str):
    """
    Execute SQL file.
    
    Args:
        connection: Database connection
        file_path: Path to SQL file
    """
    log.info(f"Reading SQL file: {file_path}")
    statements = read_sql_file(file_path)
    
    log.info(f"Found {len(statements)} SQL statements")
    
    cursor = connection.cursor()
    
    for i, statement in enumerate(statements, 1):
        try:
            # Skip comments and empty lines
            if not statement or statement.startswith('--'):
                continue
            
            log.info(f"Executing statement {i}/{len(statements)}...")
            cursor.execute(statement)
            connection.commit()
            
            # Log results if any
            if cursor.description:
                results = cursor.fetchall()
                for row in results:
                    log.info(f"  {row}")
            
        except Exception as e:
            log.error(f"Error executing statement {i}: {e}")
            log.error(f"Statement: {statement[:100]}...")
            connection.rollback()
            raise
    
    cursor.close()
    log.info("All statements executed successfully")


def main():
    """Main entry point."""
    log.info("=" * 60)
    log.info("Database Initialization")
    log.info("=" * 60)
    log.info(f"Host: {settings.db_host}:{settings.db_port}")
    log.info(f"User: {settings.db_user}")
    log.info(f"Database: {settings.db_name}")
    log.info("=" * 60)
    
    # Find SQL file
    sql_file = Path(__file__).parent / 'init_db.sql'
    
    if not sql_file.exists():
        log.error(f"SQL file not found: {sql_file}")
        return 1
    
    try:
        # Connect to MySQL server (without specifying database)
        log.info("Connecting to MySQL server...")
        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            charset=settings.db_charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        log.info("Connected successfully")
        
        # Execute SQL file
        execute_sql_file(connection, str(sql_file))
        
        # Close connection
        connection.close()
        log.info("Connection closed")
        
        log.info("=" * 60)
        log.info("Database initialization completed successfully!")
        log.info("=" * 60)
        
        return 0
        
    except Exception as e:
        log.error(f"Database initialization failed: {e}")
        import traceback
        log.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
