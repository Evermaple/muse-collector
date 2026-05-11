"""Crawler worker for fetching song and artist data."""
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.task import CrawlTask
from models.song import SongCrawlSnap
from models.artist import ArtistCrawlSnap
from utils.db_operations import (
    TaskRepository, SongRepository, ArtistRepository,
    SongSnapRepository, ArtistSnapRepository
)
from utils.logger import log
from worker.adapters import AdapterRegistry
from config.settings import settings


class CrawlerWorker:
    """
    Worker for crawling song and artist data from external sources.
    
    This worker:
    - Reads target IDs from business database
    - Fetches data from configured data sources
    - Saves data to snap tables
    - Updates task statistics
    """
    
    def __init__(self):
        self.task_repo = TaskRepository()
        self.song_repo = SongRepository()
        self.artist_repo = ArtistRepository()
        self.song_snap_repo = SongSnapRepository()
        self.artist_snap_repo = ArtistSnapRepository()
    
    def process_task(self, task_data: Dict[str, Any]) -> tuple[int, int, str]:
        """
        Process a crawl task.
        
        Args:
            task_data: Task data from database
            
        Returns:
            tuple: (success_count, total_count, error_message)
        """
        task = CrawlTask(**task_data)
        
        log.info(f"Processing task {task.task_id}, type={task.task_type}")
        
        # Determine task type and delegate
        if task.task_type in ['1', 'song']:
            return self._process_song_task(task)
        elif task.task_type in ['2', 'artist']:
            return self._process_artist_task(task)
        else:
            error_msg = f"Unknown task type: {task.task_type}"
            log.error(error_msg)
            return 0, 0, error_msg
    
    def _process_song_task(self, task: CrawlTask) -> tuple[int, int, str]:
        """
        Process song crawling task.
        
        Args:
            task: CrawlTask instance
            
        Returns:
            tuple: (success_count, total_count, error_message)
        """
        target_ids = task.get_target_id_list()
        srcs = task.get_src_list()
        
        if not target_ids:
            return 0, 0, "No target IDs provided"
        
        if not srcs:
            return 0, 0, "No data sources provided"
        
        log.info(f"Crawling {len(target_ids)} songs from {len(srcs)} source(s)")
        
        success_count = 0
        total_count = len(target_ids) * len(srcs)
        errors = []
        
        # For each target song ID
        for target_id in target_ids:
            # Read basic song info from business database (if exists)
            song_info = self._read_song_from_business_db(task.app_id, target_id)
            search_key = song_info.get('song_name', '') if song_info else target_id
            
            # Crawl from each data source
            for src in srcs:
                try:
                    result = self._crawl_song(
                        task_id=task.task_id,
                        app_id=task.app_id,
                        src=src,
                        song_id=int(target_id),
                        search_key=str(search_key)
                    )
                    
                    if result:
                        success_count += 1
                        log.debug(f"Successfully crawled song {target_id} from {src}")
                    else:
                        errors.append(f"Failed to crawl song {target_id} from {src}")
                        
                except Exception as e:
                    error_msg = f"Error crawling song {target_id} from {src}: {e}"
                    log.error(error_msg)
                    errors.append(error_msg)
        
        # Prepare error summary
        error_summary = "; ".join(errors[:5])  # Limit to first 5 errors
        if len(errors) > 5:
            error_summary += f" ... and {len(errors) - 5} more errors"
        
        log.info(f"Song task completed: {success_count}/{total_count} successful")
        
        return success_count, total_count, error_summary
    
    def _process_artist_task(self, task: CrawlTask) -> tuple[int, int, str]:
        """
        Process artist crawling task.
        
        Args:
            task: CrawlTask instance
            
        Returns:
            tuple: (success_count, total_count, error_message)
        """
        target_ids = task.get_target_id_list()
        srcs = task.get_src_list()
        
        if not target_ids:
            return 0, 0, "No target IDs provided"
        
        if not srcs:
            return 0, 0, "No data sources provided"
        
        log.info(f"Crawling {len(target_ids)} artists from {len(srcs)} source(s)")
        
        success_count = 0
        total_count = len(target_ids) * len(srcs)
        errors = []
        
        # For each target artist ID
        for target_id in target_ids:
            # Read basic artist info from business database (if exists)
            artist_info = self._read_artist_from_business_db(task.app_id, target_id)
            search_key = artist_info.get('artist_name', '') if artist_info else target_id
            
            # Crawl from each data source
            for src in srcs:
                try:
                    result = self._crawl_artist(
                        task_id=task.task_id,
                        app_id=task.app_id,
                        src=src,
                        artist_id=int(target_id),
                        search_key=str(search_key)
                    )
                    
                    if result:
                        success_count += 1
                        log.debug(f"Successfully crawled artist {target_id} from {src}")
                    else:
                        errors.append(f"Failed to crawl artist {target_id} from {src}")
                        
                except Exception as e:
                    error_msg = f"Error crawling artist {target_id} from {src}: {e}"
                    log.error(error_msg)
                    errors.append(error_msg)
        
        # Prepare error summary
        error_summary = "; ".join(errors[:5])
        if len(errors) > 5:
            error_summary += f" ... and {len(errors) - 5} more errors"
        
        log.info(f"Artist task completed: {success_count}/{total_count} successful")
        
        return success_count, total_count, error_summary
    
    def _read_song_from_business_db(self, app_id: str, song_id: str) -> Optional[Dict[str, Any]]:
        """
        Read song basic info from business database.
        
        Args:
            app_id: Application ID
            song_id: Song ID
            
        Returns:
            dict: Song info or None
        """
        try:
            # Try to find existing song info
            song = self.song_repo.find_one(
                where={'app_id': app_id, 'song_id': int(song_id)}
            )
            return song
        except Exception as e:
            log.warning(f"Failed to read song {song_id} from business DB: {e}")
            return None
    
    def _read_artist_from_business_db(self, app_id: str, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Read artist basic info from business database.
        
        Args:
            app_id: Application ID
            artist_id: Artist ID
            
        Returns:
            dict: Artist info or None
        """
        try:
            # Try to find existing artist info
            artist = self.artist_repo.find_one(
                where={'app_id': app_id, 'artist_id': int(artist_id)}
            )
            return artist
        except Exception as e:
            log.warning(f"Failed to read artist {artist_id} from business DB: {e}")
            return None
    
    def _crawl_song(self, task_id: str, app_id: str, src: str, 
                    song_id: int, search_key: str) -> bool:
        """
        Crawl song data from a specific source.
        
        Args:
            task_id: Task ID
            app_id: Application ID
            src: Data source name
            song_id: Song ID
            search_key: Search key
            
        Returns:
            bool: True if successful
        """
        # Get adapter for this source
        adapter = AdapterRegistry.get(src)
        
        if not adapter:
            log.warning(f"No adapter found for source: {src}")
            # Save failed snap
            self._save_song_snap_failed(
                task_id=task_id,
                src=src,
                song_id=song_id,
                search_key=search_key,
                failed_reason=f"No adapter for source: {src}"
            )
            return False
        
        try:
            # Fetch data from adapter
            song_data = adapter.fetch_song(song_id, search_key)
            
            if not song_data:
                log.warning(f"No data returned for song {song_id} from {src}")
                self._save_song_snap_failed(
                    task_id=task_id,
                    src=src,
                    song_id=song_id,
                    search_key=search_key,
                    failed_reason="No data returned from source"
                )
                return False
            
            # Map response to SongCrawlSnap model
            snap = self._map_to_song_snap(
                task_id=task_id,
                src=src,
                song_id=song_id,
                search_key=search_key,
                data=song_data
            )
            
            # Save to snap table
            self._save_song_snap(snap)
            
            # Also save/update to song_info table
            self._save_song_info(app_id, snap)
            
            return True
            
        except Exception as e:
            log.error(f"Failed to crawl song {song_id} from {src}: {e}")
            self._save_song_snap_failed(
                task_id=task_id,
                src=src,
                song_id=song_id,
                search_key=search_key,
                failed_reason=str(e)[:200]
            )
            return False

    def _crawl_artist(self, task_id: str, app_id: str, src: str,
                     artist_id: int, search_key: str) -> bool:
        """
        Crawl artist data from a specific source.
        
        Args:
            task_id: Task ID
            app_id: Application ID
            src: Data source name
            artist_id: Artist ID
            search_key: Search key
            
        Returns:
            bool: True if successful
        """
        # Get adapter for this source
        adapter = AdapterRegistry.get(src)
        
        if not adapter:
            log.warning(f"No adapter found for source: {src}")
            # Save failed snap
            self._save_artist_snap_failed(
                task_id=task_id,
                src=src,
                artist_id=artist_id,
                search_key=search_key,
                failed_reason=f"No adapter for source: {src}"
            )
            return False
        
        try:
            # Fetch data from adapter
            artist_data = adapter.fetch_artist(artist_id, search_key)
            
            if not artist_data:
                log.warning(f"No data returned for artist {artist_id} from {src}")
                self._save_artist_snap_failed(
                    task_id=task_id,
                    src=src,
                    artist_id=artist_id,
                    search_key=search_key,
                    failed_reason="No data returned from source"
                )
                return False
            
            # Map response to ArtistCrawlSnap model
            snap = self._map_to_artist_snap(
                task_id=task_id,
                src=src,
                artist_id=artist_id,
                search_key=search_key,
                data=artist_data
            )
            
            # Save to snap table
            self._save_artist_snap(snap)
            
            # Also save/update to artist_info table
            self._save_artist_info(app_id, snap)
            
            return True
            
        except Exception as e:
            log.error(f"Failed to crawl artist {artist_id} from {src}: {e}")
            self._save_artist_snap_failed(
                task_id=task_id,
                src=src,
                artist_id=artist_id,
                search_key=search_key,
                failed_reason=str(e)[:200]
            )
            return False
    
    def _map_to_song_snap(self, task_id: str, src: str, song_id: int,
                         search_key: str, data: Dict[str, Any]) -> SongCrawlSnap:
        """
        Map raw data to SongCrawlSnap model.
        
        Args:
            task_id: Task ID
            src: Data source
            song_id: Song ID
            search_key: Search key
            data: Raw data from adapter
            
        Returns:
            SongCrawlSnap: Mapped snapshot
        """
        return SongCrawlSnap(
            task_id=task_id,
            src=src,
            song_id=song_id,
            search_key=search_key,
            song_name=data.get('song_name', ''),
            artist_name=data.get('artist_name', ''),
            publish_dt=data.get('publish_dt', '0000-00-00'),
            song_type=data.get('song_type', '0'),
            lang=data.get('lang', ''),
            album_name=data.get('album_name', ''),
            cover_uri=data.get('cover_uri', ''),
            lyricist=data.get('lyricist', ''),
            composer=data.get('composer', ''),
            keyword=data.get('keyword', ''),
            sort_tag=data.get('sort_tag', ''),
            src_uri=data.get('src_uri', ''),
            src_id=data.get('src_id', str(song_id)),
            process_status=3,  # Success
            failed_reason=''
        )
    
    def _map_to_artist_snap(self, task_id: str, src: str, artist_id: int,
                           search_key: str, data: Dict[str, Any]) -> ArtistCrawlSnap:
        """
        Map raw data to ArtistCrawlSnap model.
        
        Args:
            task_id: Task ID
            src: Data source
            artist_id: Artist ID
            search_key: Search key
            data: Raw data from adapter
            
        Returns:
            ArtistCrawlSnap: Mapped snapshot
        """
        return ArtistCrawlSnap(
            task_id=task_id,
            src=src,
            artist_id=artist_id,
            search_key=search_key,
            artist_name=data.get('artist_name', ''),
            artist_alias=data.get('artist_alias', ''),
            artist_secondary_name=data.get('artist_secondary_name', ''),
            artist_gender=data.get('artist_gender', 0),
            artist_country=data.get('artist_country', ''),
            debug_year=data.get('debug_year', '0000'),
            is_group=data.get('is_group', 0),
            main_artist=data.get('main_artist', ''),
            artist_uri=data.get('artist_uri', ''),
            sort_tag=data.get('sort_tag', ''),
            src_uri=data.get('src_uri', ''),
            src_id=data.get('src_id', str(artist_id)),
            process_status=3,  # Success
            failed_reason=''
        )
    
    def _save_song_snap(self, snap: SongCrawlSnap):
        """Save song snapshot to database."""
        snap_dict = snap.model_dump(exclude={'id', 'ctime', 'mtime'})
        self.song_snap_repo.insert(snap_dict)
        log.debug(f"Saved song snap: {snap.song_id} from {snap.src}")
    
    def _save_song_snap_failed(self, task_id: str, src: str, song_id: int,
                              search_key: str, failed_reason: str):
        """Save failed song snapshot."""
        snap = SongCrawlSnap(
            task_id=task_id,
            src=src,
            song_id=song_id,
            search_key=search_key,
            process_status=4,  # Failed
            failed_reason=failed_reason
        )
        snap_dict = snap.model_dump(exclude={'id', 'ctime', 'mtime'})
        self.song_snap_repo.insert(snap_dict)
        log.debug(f"Saved failed song snap: {song_id} from {src}")
    
    def _save_artist_snap(self, snap: ArtistCrawlSnap):
        """Save artist snapshot to database."""
        snap_dict = snap.model_dump(exclude={'id', 'ctime', 'mtime'})
        self.artist_snap_repo.insert(snap_dict)
        log.debug(f"Saved artist snap: {snap.artist_id} from {snap.src}")
    
    def _save_artist_snap_failed(self, task_id: str, src: str, artist_id: int,
                                search_key: str, failed_reason: str):
        """Save failed artist snapshot."""
        snap = ArtistCrawlSnap(
            task_id=task_id,
            src=src,
            artist_id=artist_id,
            search_key=search_key,
            process_status=4,  # Failed
            failed_reason=failed_reason
        )
        snap_dict = snap.model_dump(exclude={'id', 'ctime', 'mtime'})
        self.artist_snap_repo.insert(snap_dict)
        log.debug(f"Saved failed artist snap: {artist_id} from {src}")
    
    def _save_song_info(self, app_id: str, snap: SongCrawlSnap):
        """
        Save or update song info to song_info table.
        Uses INSERT ON DUPLICATE KEY UPDATE.
        
        Args:
            app_id: Application ID
            snap: Song snapshot
        """
        song_info = snap.to_song_info(app_id)
        song_dict = song_info.model_dump(exclude={'id', 'ctime', 'mtime'})
        
        # Use insert_or_update which handles duplicates
        self.song_repo.insert_or_update(song_dict)
        log.debug(f"Saved/updated song info: {snap.song_id} from {snap.src}")
    
    def _save_artist_info(self, app_id: str, snap: ArtistCrawlSnap):
        """
        Save or update artist info to artist_info table.
        Uses INSERT ON DUPLICATE KEY UPDATE.
        
        Args:
            app_id: Application ID
            snap: Artist snapshot
        """
        artist_info = snap.to_artist_info(app_id)
        artist_dict = artist_info.model_dump(exclude={'id', 'ctime', 'mtime'})
        
        # Use insert_or_update which handles duplicates
        self.artist_repo.insert_or_update(artist_dict)
        log.debug(f"Saved/updated artist info: {snap.artist_id} from {snap.src}")
