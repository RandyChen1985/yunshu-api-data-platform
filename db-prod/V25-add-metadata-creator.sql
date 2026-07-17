-- V25: 为元数据核心表添加创建人字段
-- Description: 在数据集、表、指标和关系表中增加 created_by 字段，用于追踪创建者信息。

USE nanzi_api_data_platform;

-- 1. 为数据集表添加创建人
ALTER TABLE `meta_datasets` 
ADD COLUMN `created_by` BIGINT DEFAULT NULL COMMENT '创建人ID' AFTER `status`;

-- 2. 为元数据表定义添加创建人
ALTER TABLE `meta_tables` 
ADD COLUMN `created_by` BIGINT DEFAULT NULL COMMENT '创建人ID' AFTER `status`;

-- 3. 为业务指标定义添加创建人
ALTER TABLE `meta_metrics` 
ADD COLUMN `created_by` BIGINT DEFAULT NULL COMMENT '创建人ID' AFTER `unit`;

-- 4. 为实体关联关系添加创建人
ALTER TABLE `meta_relationships` 
ADD COLUMN `created_by` BIGINT DEFAULT NULL COMMENT '创建人ID' AFTER `description`;
