-- Database Migration V6
-- Add password_hash and sso fields to api_users
-- Date: 2026-01-01

USE nanzi_api_data_platform;

ALTER TABLE api_users 
ADD COLUMN password_hash VARCHAR(255) COMMENT 'Bcrypt hash of the password';

ALTER TABLE api_users 
ADD COLUMN sso_source VARCHAR(50) DEFAULT NULL COMMENT 'Source of SSO (e.g., "YES")';

ALTER TABLE api_users 
ADD COLUMN sso_id VARCHAR(255) DEFAULT NULL COMMENT 'Unique ID from the SSO provider';

ALTER TABLE api_users 
ADD COLUMN email VARCHAR(255) DEFAULT NULL COMMENT 'User email';

CREATE INDEX idx_sso ON api_users(sso_source, sso_id);
