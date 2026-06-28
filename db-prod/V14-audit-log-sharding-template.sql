-- V14: Create Template for Daily Audit Log Sharding
-- Date: 2026-01-30

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS api_access_logs_template (
    id BIGINT NOT NULL AUTO_INCREMENT,
    trace_id VARCHAR(64) NOT NULL,
    user_id BIGINT,
    user_name VARCHAR(64),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    query_params TEXT,
    status_code INT NOT NULL,
    process_time_ms FLOAT NOT NULL,
    client_ip VARCHAR(45),
    request_params TEXT COMMENT '请求参数(JSON格式)',
    response_body TEXT COMMENT '响应内容(JSON格式)',
    error_message TEXT COMMENT '错误信息',
    user_agent VARCHAR(255),
    -- 合并自 api_access_logs_ext 的字段
    action_type VARCHAR(50) NOT NULL DEFAULT 'API_QUERY' COMMENT '功能模块',
    source_sql TEXT COMMENT '关联的原始 SQL',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    -- 核心搜索索引
    INDEX idx_trace_id (trace_id),
    INDEX idx_user_created (user_name, created_at),
    INDEX idx_endpoint_created (endpoint(100), created_at),
    INDEX idx_status_created (status_code, created_at),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;