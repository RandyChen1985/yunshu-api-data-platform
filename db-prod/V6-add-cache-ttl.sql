-- Add cache_ttl column to sys_resource_meta
-- V6: Result Cache Support
-- Defines TTL in seconds (0 = disabled)

ALTER TABLE sys_resource_meta 
ADD COLUMN cache_ttl INT DEFAULT 0 COMMENT 'Cache TTL in seconds (0=Disabled)';
