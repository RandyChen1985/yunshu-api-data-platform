-- V26: 数据产品目录模块（合并原 V26–V31，幂等可重复执行）
-- 包含：产品目录表、权限申请、UI 权限、负责人策略配置、collation 对齐、草稿种子数据
-- 新环境一次性执行本脚本即可；若已分项执行过 V26–V31，依赖下方幂等语句可安全跳过或补跑。

SET NAMES utf8mb4;

-- =============================================================================
-- 1. resource_key collation 对齐（原 V30，须在目录表 JOIN 种子数据之前）
-- =============================================================================
SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE `sys_user_resources` DROP FOREIGN KEY `sys_user_resources_ibfk_2`;

ALTER TABLE `sys_user_resources`
  MODIFY COLUMN `resource_key` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL;

ALTER TABLE `sys_resource_meta`
  MODIFY COLUMN `resource_key` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Unique resource key used in API';

ALTER TABLE `sys_user_resources`
  ADD CONSTRAINT `sys_user_resources_ibfk_2`
  FOREIGN KEY (`resource_key`) REFERENCES `sys_resource_meta` (`resource_key`) ON DELETE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- 2. 核心表（原 V26，创建时即使用 utf8mb4_unicode_ci，原 V28）
-- =============================================================================
CREATE TABLE IF NOT EXISTS `data_products` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `product_key` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '产品唯一标识',
  `display_name` VARCHAR(200) NOT NULL COMMENT '展示名称',
  `summary` VARCHAR(500) DEFAULT NULL COMMENT '一句话简介',
  `description` TEXT COMMENT '详细介绍 (Markdown)',
  `domain` VARCHAR(50) NOT NULL DEFAULT '默认域' COMMENT '业务域',
  `tags` JSON DEFAULT NULL COMMENT '标签列表',
  `owner_user_id` BIGINT DEFAULT NULL COMMENT '负责人 api_users.id',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '0草稿 1已发布 2已下线',
  `dataset_id` INT DEFAULT NULL COMMENT '可选关联 meta_datasets.id',
  `featured` TINYINT NOT NULL DEFAULT 0 COMMENT '是否精选',
  `published_at` DATETIME DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_key` (`product_key`),
  KEY `idx_domain_status` (`domain`, `status`),
  KEY `idx_status_published` (`status`, `published_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据产品目录';

CREATE TABLE IF NOT EXISTS `data_product_resources` (
  `product_id` BIGINT NOT NULL,
  `resource_key` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_primary` TINYINT NOT NULL DEFAULT 1,
  `sort_order` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`product_id`, `resource_key`),
  KEY `idx_resource_key` (`resource_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据产品关联 API 资源';

-- =============================================================================
-- 3. 权限申请表（原 V27 + V31 状态说明）
-- =============================================================================
CREATE TABLE IF NOT EXISTS `data_product_access_requests` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `product_id` BIGINT NOT NULL COMMENT 'data_products.id',
  `product_key` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` INT NOT NULL COMMENT '申请人 api_users.id',
  `user_name` VARCHAR(64) NOT NULL,
  `message` VARCHAR(500) DEFAULT NULL COMMENT '申请说明',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '0待审批 1已通过 2已拒绝 3权限已收回',
  `handled_by` INT DEFAULT NULL COMMENT '处理人 api_users.id',
  `handler_name` VARCHAR(64) DEFAULT NULL,
  `handle_remark` VARCHAR(255) DEFAULT NULL,
  `handled_at` DATETIME DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_product_status` (`product_key`, `status`),
  KEY `idx_user_status` (`user_id`, `status`),
  KEY `idx_status_created` (`status`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据产品权限申请';

-- 自旧版分项迁移升级：对齐 collation 与 status 注释（原 V28 / V31）
ALTER TABLE `data_products`
  MODIFY COLUMN `product_key` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '产品唯一标识';

ALTER TABLE `data_product_resources`
  MODIFY COLUMN `resource_key` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL;

ALTER TABLE `data_product_access_requests`
  MODIFY COLUMN `product_key` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL;

ALTER TABLE `data_product_access_requests`
  MODIFY COLUMN `status` TINYINT NOT NULL DEFAULT 0
  COMMENT '0待审批 1已通过 2已拒绝 3权限已收回';

-- =============================================================================
-- 4. UI 权限（原 V26 + V27）
-- =============================================================================
INSERT IGNORE INTO `sys_ui_permissions` (`perm_type`, `perm_code`) VALUES
('menu', 'menu:asset-panorama'),
('element', 'element:catalog:publish'),
('element', 'element:catalog:manage'),
('menu', 'menu:catalog:requests'),
('element', 'element:catalog:review');

INSERT IGNORE INTO `sys_ui_permissions` (`role_id`, `perm_type`, `perm_code`, `enabled`)
SELECT r.id, 'menu', 'menu:asset-panorama', 1
FROM `sys_roles` r;

INSERT IGNORE INTO `sys_ui_permissions` (`role_id`, `perm_type`, `perm_code`, `enabled`)
SELECT r.id, 'menu', 'menu:catalog:requests', 1
FROM `sys_roles` r;

-- =============================================================================
-- 5. 目录默认负责人策略（原 V29）
-- =============================================================================
INSERT INTO `sys_config` (`config_key`, `config_value`, `config_group`, `remark`)
VALUES
  ('catalog.default_owner_strategy', 'publisher', 'catalog', '默认负责人：publisher=发布人, group_owner=分组映射, none=不自动指定'),
  ('catalog.group_owner_map', '{}', 'catalog', '分组负责人 JSON 映射，如 {"财务域": 1}')
ON DUPLICATE KEY UPDATE
  `config_group` = VALUES(`config_group`),
  `remark` = VALUES(`remark`);

-- =============================================================================
-- 6. 从现有 API 资源种子草稿产品（原 V26，collation 已对齐后无需 COLLATE）
-- =============================================================================
INSERT INTO `data_products` (
  `product_key`, `display_name`, `summary`, `domain`, `tags`, `status`, `published_at`
)
SELECT
  m.resource_key,
  m.resource_name,
  COALESCE(NULLIF(TRIM(m.remarks), ''), CONCAT(m.resource_name, ' 数据 API')),
  COALESCE(NULLIF(TRIM(m.resource_group), ''), '默认域'),
  JSON_ARRAY(m.data_source),
  0,
  NULL
FROM `sys_resource_meta` m
WHERE m.status = 1
  AND LOWER(COALESCE(m.resource_group, '')) != 'system'
  AND m.resource_mode IN ('TABLE', 'SQL')
ON DUPLICATE KEY UPDATE
  `display_name` = IF(`data_products`.`status` = 0, VALUES(`display_name`), `data_products`.`display_name`),
  `summary` = IF(`data_products`.`status` = 0, VALUES(`summary`), `data_products`.`summary`),
  `domain` = IF(`data_products`.`status` = 0, VALUES(`domain`), `data_products`.`domain`);

INSERT IGNORE INTO `data_product_resources` (`product_id`, `resource_key`, `is_primary`, `sort_order`)
SELECT p.id, m.resource_key, 1, 0
FROM `data_products` p
INNER JOIN `sys_resource_meta` m ON m.resource_key = p.product_key;
