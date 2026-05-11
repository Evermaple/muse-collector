-- Muse Collector Database Initialization Script
-- This script creates all necessary tables for the muse_collector system

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS muse_collector DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE muse_collector;

-- ============================================================================
-- Table: song_info
-- Description: Main table for song information
-- ============================================================================
CREATE TABLE IF NOT EXISTS song_info (
    id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
    app_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'appid',
    src VARCHAR(32) NOT NULL DEFAULT '' COMMENT '数据来源',
    song_id BIGINT(16) NOT NULL DEFAULT 0 COMMENT '歌曲id',
    song_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌曲名称',
    artist_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手名称',
    publish_dt VARCHAR(32) NOT NULL DEFAULT '0000-00-00' COMMENT '发行时间',
    song_type VARCHAR(32) NOT NULL DEFAULT '0' COMMENT '歌曲类型',
    lang VARCHAR(32) NOT NULL DEFAULT '' COMMENT '语种',
    album_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '专辑名称',
    cover_uri VARCHAR(500) NOT NULL DEFAULT '' COMMENT '封面图片',
    lyricist VARCHAR(200) NOT NULL DEFAULT '' COMMENT '作词人',
    composer VARCHAR(200) NOT NULL DEFAULT '' COMMENT '作曲人',
    keyword VARCHAR(200) NOT NULL DEFAULT '' COMMENT '歌曲关键词',
    sort_tag VARCHAR(32) NOT NULL DEFAULT '' COMMENT '歌曲排序标签',
    mtime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uniq_song_idx (app_id, song_id, src),
    KEY idx_name (app_id, song_name, artist_name, src),
    KEY idx_create_at (ctime)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='歌曲信息表';

-- ============================================================================
-- Table: artist_info
-- Description: Main table for artist information
-- ============================================================================
CREATE TABLE IF NOT EXISTS artist_info (
    id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
    app_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'appid',
    src VARCHAR(32) NOT NULL DEFAULT '' COMMENT '数据来源',
    artist_id BIGINT(20) NOT NULL DEFAULT 0 COMMENT '歌手id',
    artist_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手名称',
    artist_alias VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手别名',
    artist_secondary_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手副名',
    artist_gender TINYINT(4) NOT NULL DEFAULT 0 COMMENT '歌手性别,1=male,2=female',
    artist_country VARCHAR(64) NOT NULL DEFAULT '' COMMENT '歌手国家',
    debug_year VARCHAR(32) NOT NULL DEFAULT '0000' COMMENT '出道年份',
    is_group TINYINT(4) NOT NULL DEFAULT 0 COMMENT '是否是组合,0=不是,1=是',
    main_artist VARCHAR(32) NOT NULL DEFAULT '' COMMENT '主唱',
    artist_uri VARCHAR(512) NOT NULL DEFAULT '' COMMENT '歌手图片',
    sort_tag VARCHAR(32) NOT NULL DEFAULT '' COMMENT '歌手排序标签',
    mtime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_artist_name (app_id, artist_name, src),
    UNIQUE KEY uniq_idx_artist (app_id, artist_id, src),
    KEY idx_create_at (ctime)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='歌手信息表';

-- ============================================================================
-- Table: song_crawl_snap
-- Description: Snapshot table for song crawling process
-- ============================================================================
CREATE TABLE IF NOT EXISTS song_crawl_snap (
    id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
    src VARCHAR(32) NOT NULL DEFAULT '' COMMENT '来源',
    song_id BIGINT(16) NOT NULL DEFAULT 0 COMMENT '歌曲id',
    song_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌曲名称',
    artist_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手名称',
    publish_dt VARCHAR(32) NOT NULL DEFAULT '0000-00-00' COMMENT '发行时间',
    song_type VARCHAR(32) NOT NULL DEFAULT '0' COMMENT '歌曲类型',
    lang VARCHAR(32) NOT NULL DEFAULT '' COMMENT '语种',
    album_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '专辑名称',
    cover_uri VARCHAR(500) NOT NULL DEFAULT '' COMMENT '封面图片',
    lyricist VARCHAR(200) NOT NULL DEFAULT '' COMMENT '作词人',
    composer VARCHAR(200) NOT NULL DEFAULT '' COMMENT '作曲人',
    keyword VARCHAR(200) NOT NULL DEFAULT '' COMMENT '歌曲关键词',
    sort_tag VARCHAR(32) NOT NULL DEFAULT '' COMMENT '歌曲排序标签',
    search_key VARCHAR(200) NOT NULL DEFAULT '' COMMENT '搜索关键词',
    src_uri VARCHAR(500) NOT NULL DEFAULT '' COMMENT '来源链接',
    src_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT '原站id',
    task_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT '任务id',
    process_status TINYINT NOT NULL DEFAULT 0 COMMENT '1=等待;2=执行中;3=成功;4=失败;5=跳过',
    failed_reason VARCHAR(200) NOT NULL DEFAULT '' COMMENT '失败原因',
    mtime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_song_id (song_id),
    KEY idx_name (song_name, artist_name, src),
    KEY idx_create_at (task_id, ctime)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='歌曲采集快照表';

-- ============================================================================
-- Table: artist_crawl_snap
-- Description: Snapshot table for artist crawling process
-- ============================================================================
CREATE TABLE IF NOT EXISTS artist_crawl_snap (
    id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
    src VARCHAR(32) NOT NULL DEFAULT '' COMMENT '来源',
    artist_id BIGINT(20) NOT NULL DEFAULT 0 COMMENT '歌手id',
    artist_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手名称',
    artist_alias VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手别名',
    artist_secondary_name VARCHAR(128) NOT NULL DEFAULT '' COMMENT '歌手副名',
    artist_gender TINYINT(4) NOT NULL DEFAULT 0 COMMENT '歌手性别,1=male,2=female',
    artist_country VARCHAR(64) NOT NULL DEFAULT '' COMMENT '歌手国家',
    debug_year VARCHAR(32) NOT NULL DEFAULT '0000' COMMENT '出道年份',
    is_group TINYINT(4) NOT NULL DEFAULT 0 COMMENT '是否是组合,0=不是,1=是',
    main_artist VARCHAR(32) NOT NULL DEFAULT '' COMMENT '主唱',
    artist_uri VARCHAR(512) NOT NULL DEFAULT '' COMMENT '歌手图片',
    sort_tag VARCHAR(32) NOT NULL DEFAULT '' COMMENT '歌手排序标签',
    search_key VARCHAR(200) NOT NULL DEFAULT '' COMMENT '搜索关键词',
    src_uri VARCHAR(500) NOT NULL DEFAULT '' COMMENT '来源链接',
    src_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT '原站id',
    task_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT '任务id',
    process_status TINYINT NOT NULL DEFAULT 0 COMMENT '1=等待;2=执行中;3=成功;4=失败;5=跳过',
    failed_reason VARCHAR(200) NOT NULL DEFAULT '' COMMENT '失败原因',
    mtime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_artist_id (artist_id),
    KEY idx_artist_name (artist_name, src),
    KEY idx_create_at (task_id, ctime)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='歌手采集快照表';

-- ============================================================================
-- Table: crawl_task
-- Description: Task management table for crawling operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS crawl_task (
    id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    app_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'appid',
    task_id VARCHAR(32) NOT NULL DEFAULT '' COMMENT '任务id',
    task_type VARCHAR(16) NOT NULL DEFAULT '' COMMENT '任务类型,1=歌曲;2=歌手;',
    srcs VARCHAR(2000) NOT NULL DEFAULT '' COMMENT '目标数据源src',
    target_ids VARCHAR(2000) NOT NULL DEFAULT '' COMMENT '目标id',
    task_status TINYINT NOT NULL DEFAULT 0 COMMENT '1=等待;2=执行中;3=成功;4=失败;5=取消',
    failed_reason VARCHAR(200) NOT NULL DEFAULT '' COMMENT '失败原因',
    item_cnt INT(10) NOT NULL DEFAULT 0 COMMENT '目标数量',
    success_cnt INT(10) NOT NULL DEFAULT 0 COMMENT '成功数量',
    mtime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_task (app_id, task_id, task_type, task_status, ctime)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='数据采集任务表';

-- ============================================================================
-- Initialization Complete
-- ============================================================================
SELECT 'Database initialization completed successfully!' AS status;
