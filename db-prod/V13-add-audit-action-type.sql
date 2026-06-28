-- V13: Implementation via Extended Table (Non-blocking Approach)
-- Purpose: Support functional auditing without altering the massive api_access_logs table.

SET NAMES utf8mb4;

-- 1. Create the extension table
CREATE TABLE IF NOT EXISTS api_access_logs_ext (
    log_id BIGINT PRIMARY KEY COMMENT 'Link to api_access_logs.id',
    action_type VARCHAR(50) NOT NULL DEFAULT 'API_QUERY' COMMENT '功能模块',
    source_sql TEXT COMMENT '关联的原始 SQL',
    INDEX idx_ext_action_type (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. No changes required to api_access_logs.
