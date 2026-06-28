-- V15: Add sort_order to sys_data_source
-- Description: Add a column to support manual sorting of data sources

ALTER TABLE `sys_data_source` ADD COLUMN `sort_order` INT NOT NULL DEFAULT 0 COMMENT 'Sorting weight (ascending)' AFTER `description`;

-- Initialize sort_order with id to maintain current default order (optional, but keeps consistency)
UPDATE `sys_data_source` SET `sort_order` = id;
