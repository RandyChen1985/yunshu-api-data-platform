-- 1. 系统配置项初始化 (sys_config)
INSERT INTO sys_config (config_key, config_value, config_group, remark) VALUES 
('ratelimit.enabled', 'true', 'system', 'API v1 流控总开关'),
('ratelimit.admin.limit', '1000', 'system', '管理员默认每分钟限流值'),
('ratelimit.user.limit', '100', 'system', '普通用户默认每分钟限流值')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);

-- 2. 扩展用户表和角色表
ALTER TABLE api_users ADD COLUMN rate_limit INT DEFAULT NULL COMMENT '用户自定义限流值(每分钟)，为NULL时使用角色或系统默认值';
ALTER TABLE sys_roles ADD COLUMN rate_limit INT DEFAULT NULL COMMENT '角色自定义限流值(每分钟)，为NULL时使用系统默认值';

-- 3. 统一字符集校验规则，防止 JOIN 报错 (Illegal mix of collations)
ALTER TABLE api_users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sys_roles CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE api_users MODIFY role VARCHAR(50) COLLATE utf8mb4_unicode_ci;
ALTER TABLE sys_roles MODIFY role_code VARCHAR(50) COLLATE utf8mb4_unicode_ci;
