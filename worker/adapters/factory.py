"""Data source adapter factory."""
from typing import Dict, Optional
from worker.adapters.base import DataSourceAdapter
from worker.adapters.netease import NeteaseAdapter
from config.settings import settings
from utils.logger import log


class AdapterFactory:
    """Factory for creating data source adapters."""
    
    _adapters: Dict[str, DataSourceAdapter] = {}
    
    @classmethod
    def get_adapter(cls, source: str) -> Optional[DataSourceAdapter]:
        """
        Get adapter instance for the specified data source.
        
        Args:
            source: Data source name (e.g., 'netease', 'qq', 'kugou')
            
        Returns:
            DataSourceAdapter: Adapter instance or None if not supported
        """
        # Return cached adapter if exists
        if source in cls._adapters:
            return cls._adapters[source]
        
        # Create new adapter based on source
        adapter = None
        
        if source == 'netease':
            adapter = NeteaseAdapter(
                base_url=settings.netease_base_url,
                timeout=settings.netease_timeout,
                rate_limit=settings.netease_rate_limit
            )
        else:
            log.warning(f"Unsupported data source: {source}")
            return None
        
        # Cache the adapter
        cls._adapters[source] = adapter
        log.info(f"Created adapter for data source: {source}")
        
        return adapter
    
    @classmethod
    def close_all(cls):
        """Close all adapter sessions."""
        for source, adapter in cls._adapters.items():
            try:
                adapter.close()
                log.info(f"Closed adapter for {source}")
            except Exception as e:
                log.error(f"Error closing adapter for {source}: {e}")
        
        cls._adapters.clear()
