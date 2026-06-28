-- V8: Create Log Aggregation Table
-- Date: 2026-01-23
-- Description: Create a minute-level aggregation table for API access logs to improve dashboard performance and enable data retention policies.

SET NAMES utf8mb4;

-- ----------------------------
-- Table: api_access_stats_1m
-- ----------------------------
DROP TABLE IF EXISTS api_access_stats_1m;
CREATE TABLE api_access_stats_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    time_bucket DATETIME NOT NULL COMMENT 'Time bucket (minute level)',
    
    -- Dimensions
    user_name VARCHAR(64) DEFAULT 'ALL' COMMENT 'Username (ALL for global stats)',
    endpoint VARCHAR(255) DEFAULT 'ALL' COMMENT 'API Endpoint',
    method VARCHAR(10) DEFAULT 'ALL' COMMENT 'HTTP Method',
    status_code INT DEFAULT 0 COMMENT 'HTTP Status Code',
    
    -- Metrics
    total_calls INT NOT NULL DEFAULT 0 COMMENT 'Total calls in this bucket',
    total_error INT NOT NULL DEFAULT 0 COMMENT 'Total errors (status>=400)',
    avg_latency FLOAT NOT NULL DEFAULT 0 COMMENT 'Average latency (ms)',
    max_latency FLOAT NOT NULL DEFAULT 0 COMMENT 'Max latency (ms)',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for fast dashboard queries
    UNIQUE KEY uk_bucket_dims (time_bucket, user_name, endpoint, method, status_code),
    INDEX idx_time_stats (time_bucket),
    INDEX idx_user_stats (user_name, time_bucket)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API Access Log Minute-level Stats';
