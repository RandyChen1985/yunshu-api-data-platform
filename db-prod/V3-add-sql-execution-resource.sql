-- V5: Add system.sql.execute resource metadata (Placeholder)
-- Date: 2025-01-01
-- Description: 注册 "动态 SQL 查询" 占位符 以支持 sys_user_resources 外键约束。
-- 实际配置逻辑由 app/services/meta_service.py 硬编码接管。

REPLACE INTO `sys_resource_meta` (
    `resource_key`, 
    `resource_name`, 
    `resource_group`, 
    `data_source`, 
    `resource_mode`, 
    `status`, 
    `remarks`,
    `table_name`,
    `custom_sql`,
    `fields_config`,
    `allowed_filters`,
    `default_sort`
) VALUES (
    'system.sql.execute', 
    '动态 SQL 查询', 
    'System', 
    'default', 
    'SYSTEM', 
    1, 
    'System Built-in (Placeholder for FK)',
    NULL,
    NULL,
    '[]',
    '[]',
    ''
);
