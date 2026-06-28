-- V20: Add Metadata RBAC Permissions and API Resource (Streamlined Version)
-- Date: 2026-02-03
-- Changes: Removed element:metadata:search as it is now unrestricted internally.
-- Note: External API still controlled via system.metadata.search RESOURCE permission.

SET NAMES utf8mb4;

-- 1. Register Functional Permissions (Elements)
INSERT IGNORE INTO `sys_ui_permissions` (`perm_type`, `perm_code`) VALUES
('element', 'element:metadata:view'),
('element', 'element:metadata:manage');

-- 2. Register Menus
INSERT IGNORE INTO `sys_ui_permissions` (`perm_type`, `perm_code`) VALUES
('menu', 'menu:metadata'),
('menu', 'menu:metadata:simulator');

-- 3. Register API Resource (Categorized under System group)
INSERT INTO `sys_resource_meta` (
    `resource_key`, `resource_name`, `resource_mode`, `resource_group`, 
    `remarks`, `status`, `data_source`, `fields_config`, `allowed_filters`
) VALUES (
    'system.metadata.search', 
    '语义元数据检索', 
    'SQL', 
    'System', 
    '外部 AI 系统专用：根据关键词或语义召回 RAG 上下文 (YAML)', 
    1, 
    'default',
    '[]',
    '[]'
)
ON DUPLICATE KEY UPDATE `resource_name` = VALUES(`resource_name`), `resource_group` = VALUES(`resource_group`);