-- V16: Drop deprecated log tables
-- Description: Remove unused api_access_logs and api_access_logs_ext tables

DROP TABLE IF EXISTS `api_access_logs`;
DROP TABLE IF EXISTS `api_access_logs_ext`;
