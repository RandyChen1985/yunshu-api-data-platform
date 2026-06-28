-- V11: Implement RBAC and UI Permissions (Menus & Elements)
-- Purpose: Add support for Roles, Menus and Functional Elements without breaking existing Resource logic.

SET NAMES utf8mb4;

-- 1. Table: sys_roles
CREATE TABLE IF NOT EXISTS sys_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_code VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码 (如 analyst, operator)',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    description VARCHAR(255) COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Table: sys_user_role_relation
CREATE TABLE IF NOT EXISTS sys_user_role_relation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '关联 sys_users.id',
    role_id BIGINT NOT NULL COMMENT '关联 sys_roles.id',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Table: sys_ui_permissions (Specific for Menus and Elements)
-- We keep sys_user_resources separate as requested.
CREATE TABLE IF NOT EXISTS sys_ui_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT DEFAULT NULL COMMENT '直接绑定用户 (可选)',
    role_id BIGINT DEFAULT NULL COMMENT '绑定到角色 (可选)',
    perm_type VARCHAR(20) NOT NULL COMMENT '类型: menu, element',
    perm_code VARCHAR(100) NOT NULL COMMENT '逻辑编码 (如 menu:lab, element:lab:publish)',
    enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_role (role_id),
    INDEX idx_type_code (perm_type, perm_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Initial Seed: Register Menus
INSERT IGNORE INTO sys_ui_permissions (perm_type, perm_code) VALUES
('menu', 'menu:overview'),
('menu', 'menu:lab'),
('menu', 'menu:playground'),
('menu', 'menu:resources'),
('menu', 'menu:datasource'),
('menu', 'menu:audit'),
('menu', 'menu:users'),
('menu', 'menu:config'),
('menu', 'menu:system:roles');

-- Functional Elements (Buttons/Actions)
INSERT IGNORE INTO sys_ui_permissions (perm_type, perm_code) VALUES
('element', 'element:lab:generate'),
('element', 'element:lab:metadata'),
('element', 'element:lab:publish'),
('element', 'element:lab:export'),
('element', 'element:lab:analysis'),
('element', 'element:lab:mode_api'),
('element', 'element:lab:mode_analyst'),
('element', 'element:resource:edit'),
('element', 'element:resource:delete'),
('element', 'element:resource:export'),
('element', 'element:resource:manage_special'),
('element', 'element:datasource:edit'),
('element', 'element:audit:export'),
('element', 'element:audit:manage'),
('element', 'element:user:manage'),
('element', 'element:config:save'),
('element', 'element:overview:stats'),
('element', 'element:resource:create'),
('element', 'element:resource:import');
