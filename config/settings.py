"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "muse_collector"
    app_env: str = "development"
    
    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "muse_collector"
    db_charset: str = "utf8mb4"
    
    # Database Pool
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    
    # Worker
    worker_poll_interval: int = 10
    worker_batch_size: int = 100
    worker_max_retry: int = 3
    worker_timeout: int = 7200
    
    # Data Source - Netease
    netease_base_url: str = "https://music.163.com/api"
    netease_rate_limit: int = 100
    netease_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_rotation: str = "500 MB"
    log_retention: str = "30 days"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
