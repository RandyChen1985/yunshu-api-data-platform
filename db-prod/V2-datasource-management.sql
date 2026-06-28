-- V4: Data Source Management
-- Date: 2025-12-30
-- Description: Create sys_data_source table for dynamic database connection management

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sys_data_source
-- ----------------------------
DROP TABLE IF EXISTS `sys_data_source`;
CREATE TABLE `sys_data_source` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `source_name` varchar(100) NOT NULL COMMENT 'Data source name (unique identifier)',
  `source_type` varchar(50) NOT NULL COMMENT 'Type: clickhouse, mysql, oracle, etc.',
  `host` varchar(255) NOT NULL COMMENT 'Database host',
  `port` int(11) NOT NULL COMMENT 'Database port',
  `database_name` varchar(100) DEFAULT NULL COMMENT 'Database/Schema name',
  `username` varchar(100) DEFAULT NULL COMMENT 'Connection username',
  `password` varchar(255) DEFAULT NULL COMMENT 'Connection password (encrypted)',
  `extra_params` json DEFAULT NULL COMMENT 'Additional connection parameters',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT 'Status: 1-Active, 0-Inactive',
  `description` text DEFAULT NULL COMMENT 'Description',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_source_name` (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Data Source Configuration';

-- ----------------------------
-- Seed initial ClickHouse data source from env
-- ----------------------------
INSERT INTO `sys_data_source` (`source_name`, `source_type`, `host`, `port`, `database_name`, `username`, `password`, `description`, `status`) VALUES
('default_clickhouse', 'clickhouse', 'localhost', 9000, 'default', 'default', '', '默认 ClickHouse 数据源', 1);

-- ----------------------------
-- Migrate existing resources to use default_clickhouse
-- ----------------------------
UPDATE `sys_resource_meta` SET `data_source` = 'default_clickhouse' WHERE `data_source` = 'clickhouse';

SET FOREIGN_KEY_CHECKS = 1;
