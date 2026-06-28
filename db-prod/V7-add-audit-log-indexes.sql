-- V7: Add Composite Indexes for Audit Log Performance
-- Date: 2026-01-23
-- Description: Add composite indexes to optimize audit log filtering and sorting on large datasets (5M+ rows).
-- Issues Addressed: Slow dashboard stats and audit log pagination.

SET NAMES utf8mb4;

-- 1. Optimize: WHERE user_name = ? ORDER BY created_at DESC
-- Used by: User's personal audit log view, User Dashboard stats
CREATE INDEX idx_user_created ON api_access_logs (user_name, created_at);

-- 2. Optimize: Global stats filtering by time and status
-- Used by: Admin Dashboard (trends, error rates)
-- Note: 'created_at' is first because range queries (>=) are common. 
-- While usually range columns go last, for 'trends' we group by date(created_at), so covering index helps.
-- A better one for specific stats might be (created_at, status_code).
CREATE INDEX idx_created_status ON api_access_logs (created_at, status_code);

-- 3. Optimize: WHERE endpoint = ? ORDER BY created_at DESC
-- Used by: Audit log filtering by endpoint
CREATE INDEX idx_endpoint_created ON api_access_logs (endpoint, created_at);
