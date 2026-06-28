-- V5: Increase resource_key length to 255
-- Date: 2026-01-08
-- Description: Alter resource_key length from 100 to 255 in sys_resource_meta and sys_user_resources.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Drop foreign key constraint from sys_user_resources
ALTER TABLE sys_user_resources DROP FOREIGN KEY sys_user_resources_ibfk_2;

-- 2. Alter sys_user_resources first (child table)
ALTER TABLE sys_user_resources
    MODIFY COLUMN resource_key varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL;

-- 3. Alter sys_resource_meta (parent table)
ALTER TABLE sys_resource_meta
    MODIFY COLUMN resource_key varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Unique resource key used in API';

-- 4. Re-add foreign key constraint
ALTER TABLE sys_user_resources ADD CONSTRAINT sys_user_resources_ibfk_2
    FOREIGN KEY (resource_key) REFERENCES sys_resource_meta(resource_key) ON DELETE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;
