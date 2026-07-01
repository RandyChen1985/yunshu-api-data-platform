-- V35: 品牌个性化 — 登录页底部版权信息
-- Date: 2026-07-01

SET NAMES utf8mb4;

INSERT IGNORE INTO sys_config (config_key, config_value, config_group, remark) VALUES
('branding.copyright_text', '', 'branding', '登录页底部版权文案（启用品牌个性化后展示）');
