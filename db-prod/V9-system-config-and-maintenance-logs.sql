-- V9: System Configuration and Maintenance Logs
-- Date: 2026-01-23

SET NAMES utf8mb4;

-- ----------------------------
-- Table: sys_config
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_group VARCHAR(50) DEFAULT 'default' COMMENT '配置分组',
    remark VARCHAR(255) COMMENT '备注',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统全局配置表';

-- 初始化默认日志配置
INSERT IGNORE INTO sys_config (config_key, config_value, config_group, remark) VALUES 
('log.retention.raw_days', '7', 'maintenance', '原始访问日志保留天数'),
('log.retention.stats_days', '90', 'maintenance', '聚合统计数据保留天数');

-- ----------------------------
-- Table: sys_maintenance_log
-- ----------------------------
CREATE TABLE IF NOT EXISTS sys_maintenance_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称 (e.g. log_purge, backfill)',
    status VARCHAR(20) NOT NULL COMMENT '状态 (SUCCESS, FAILED, RUNNING)',
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    affected_rows INT DEFAULT 0 COMMENT '影响行数',
    error_message TEXT COMMENT '错误详情',
    operator VARCHAR(64) DEFAULT 'SYSTEM' COMMENT '操作人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统运维操作日志';
