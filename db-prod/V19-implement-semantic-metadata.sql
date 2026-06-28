-- V19: Implement Semantic Metadata Management
-- Description: Replicate semantic layer (Datasets, Tables, Columns, Metrics, Relationships) for AI-enhanced Text2SQL.

SET NAMES utf8mb4;

-- 1. Table: meta_datasets (数据集/业务域)
CREATE TABLE IF NOT EXISTS `meta_datasets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '数据集物理编码，如 ops_resources',
    `display_name` VARCHAR(100) COMMENT '业务显示名称',
    `description` TEXT COMMENT '详细描述：用于辅助 AI 理解该业务域包含的内容',
    `tags` JSON COMMENT '标签列表 (JSON Array)',
    `data_source` VARCHAR(50) NOT NULL DEFAULT 'default' COMMENT '关联的数据源名称',
    `status` TINYINT DEFAULT 1 COMMENT '1:启用, 0:禁用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_dataset_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='语义元数据集表';

-- 2. Table: meta_tables (元数据表定义)
CREATE TABLE IF NOT EXISTS `meta_tables` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `dataset_id` INT NOT NULL COMMENT '归属数据集',
    `physical_name` VARCHAR(255) NOT NULL COMMENT '数据库真实表名',
    `term` VARCHAR(255) NOT NULL COMMENT '业务术语名称',
    `description` TEXT COMMENT '表用途详细描述',
    `synonyms` JSON COMMENT '同义词列表 (JSON Array)',
    `status` TINYINT DEFAULT 1 COMMENT '1:启用, 0:禁用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_table_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `meta_datasets` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_dataset_table` (`dataset_id`, `physical_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='元数据-表定义';

-- 3. Table: meta_columns (元数据字段定义)
CREATE TABLE IF NOT EXISTS `meta_columns` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_id` INT NOT NULL COMMENT '归属表ID',
    `physical_name` VARCHAR(255) NOT NULL COMMENT '物理字段名',
    `term` VARCHAR(255) NOT NULL COMMENT '字段业务术语',
    `type` VARCHAR(50) COMMENT '字段物理类型',
    `description` TEXT COMMENT '字段业务含义描述',
    `enums` JSON COMMENT '枚举值映射 (JSON Array of Objects: {value, label})',
    `synonyms` JSON COMMENT '字段级同义词 (JSON Array)',
    `examples` JSON COMMENT '示例值 (JSON Array, 用于 Few-shot)',
    `foreign_key` VARCHAR(255) COMMENT '外键关联 (格式: Table.Column)',
    `is_primary` TINYINT DEFAULT 0 COMMENT '是否主键',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_column_table` FOREIGN KEY (`table_id`) REFERENCES `meta_tables` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_table_col` (`table_id`, `physical_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='元数据-字段定义';

-- 4. Table: meta_metrics (业务指标定义)
CREATE TABLE IF NOT EXISTS `meta_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `dataset_id` INT NOT NULL COMMENT '所属数据集',
    `name` VARCHAR(100) NOT NULL COMMENT '指标物理名',
    `display_name` VARCHAR(100) NOT NULL COMMENT '指标显示名',
    `description` TEXT COMMENT '业务口径描述',
    `calculation_logic` TEXT COMMENT 'SQL计算逻辑或公式',
    `unit` VARCHAR(20) DEFAULT NULL COMMENT '单位',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_metric_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `meta_datasets` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_dataset_metric` (`dataset_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='元数据-业务指标定义';

-- 5. Table: meta_relationships (实体关联关系)
CREATE TABLE IF NOT EXISTS `meta_relationships` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `source_table_id` INT NOT NULL COMMENT '源表',
    `target_table_id` INT NOT NULL COMMENT '目标表',
    `join_condition` VARCHAR(255) NOT NULL COMMENT '关联条件 (如 source.id = target.ref_id)',
    `join_type` VARCHAR(20) DEFAULT 'LEFT' COMMENT '关联类型: LEFT, INNER, RIGHT',
    `description` TEXT COMMENT '关系描述',
    CONSTRAINT `fk_rel_source` FOREIGN KEY (`source_table_id`) REFERENCES `meta_tables` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rel_target` FOREIGN KEY (`target_table_id`) REFERENCES `meta_tables` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='元数据-实体关系定义';
