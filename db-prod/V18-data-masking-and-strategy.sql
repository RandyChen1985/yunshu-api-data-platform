-- V18: Data Masking Rules and Three-Level Strategy
-- Description: Create masking rules table and add masking_strategy to users/roles.

SET NAMES utf8mb4;

-- 1. Table: sys_masking_rules
CREATE TABLE IF NOT EXISTS `sys_masking_rules` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `rule_name` VARCHAR(100) NOT NULL COMMENT '规则名称',
    `match_field` VARCHAR(100) NOT NULL COMMENT '匹配字段名 (支持通配符 *)',
    `mask_type` VARCHAR(50) NOT NULL COMMENT '脱敏类型: PARTIAL_3_4, PARTIAL_4, EMAIL, FULL',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `description` VARCHAR(255) COMMENT '描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_match_field` (`match_field`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Add masking_strategy to sys_roles
-- Strategy: GLOBAL (Follow Global), ENABLE (Force), DISABLE (Allow Plaintext)
ALTER TABLE `sys_roles` ADD COLUMN `masking_strategy` VARCHAR(20) DEFAULT 'GLOBAL' COMMENT '脱敏策略: GLOBAL, ENABLE, DISABLE' AFTER `description`;

-- 3. Add masking_strategy to sys_users (mapped from api_users)
-- Strategy: ROLE (Follow Role), ENABLE (Force), DISABLE (Allow Plaintext)
-- Note: Our sys_users table might be named api_users in some versions, let's check sys_users existence or use the established name.
-- In V11 we used sys_users as a concept, but let's check actual table name in DB.
ALTER TABLE `api_users` ADD COLUMN `masking_strategy` VARCHAR(20) DEFAULT 'ROLE' COMMENT '脱敏策略: ROLE, ENABLE, DISABLE' AFTER `remark`;

-- 4. Initial Global Config in sys_config
INSERT IGNORE INTO `sys_config` (`config_key`, `config_value`, `config_group`, `remark`) 
VALUES ('ENABLE_DATA_MASKING', 'true', 'security', '是否启用全局数据脱敏');

-- 5. Seed Default Rules
INSERT INTO `sys_masking_rules` (`rule_name`, `match_field`, `mask_type`, `description`) VALUES
('手机号脱敏', '*phone*', 'PARTIAL_3_4', '匹配包含 phone 的字段，保留前3后4'),
('手机号脱敏(移动)', '*mobile*', 'PARTIAL_3_4', '匹配包含 mobile 的字段'),
('电子邮箱脱敏', '*email*', 'EMAIL', '匹配邮箱字段'),
('密码保护', '*password*', 'FULL', '匹配密码字段，完全遮掩'),
('密钥保护', '*secret*', 'FULL', '匹配密钥字段'),
('密钥保护(Token)', '*token*', 'FULL', '匹配 Token 字段'),
('身份证脱敏', '*id_card*', 'FULL', '匹配身份证字段');
