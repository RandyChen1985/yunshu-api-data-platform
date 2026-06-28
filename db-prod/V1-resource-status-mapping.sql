-- Migration V1: User-Resource Mapping
-- Note: status column already exists in sys_resource_meta from V0

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Align parent column collation so FK columns are compatible (MySQL 8.0+)
ALTER TABLE sys_resource_meta
    MODIFY COLUMN resource_key varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Unique resource key used in API';

-- Create sys_user_resources table
CREATE TABLE IF NOT EXISTS sys_user_resources (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    resource_key varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY idx_user_resource (user_id, resource_key),
    FOREIGN KEY (user_id) REFERENCES api_users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_key) REFERENCES sys_resource_meta(resource_key) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index for counting references
CREATE INDEX idx_resource_ref ON sys_user_resources(resource_key);

SET FOREIGN_KEY_CHECKS = 1;
