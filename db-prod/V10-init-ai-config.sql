-- V10: Initialize AI Configuration
-- Date: 2026-01-24

SET NAMES utf8mb4;

INSERT IGNORE INTO sys_config (config_key, config_value, config_group, remark) VALUES 
('ai.enabled', 'false', 'ai', '是否启用 AI 增强功能 (true/false)'),
('ai.provider', 'openai', 'ai', 'AI 服务商 (目前支持 openai 兼容协议)'),
('ai.base_url', 'https://api.openai.com/v1', 'ai', 'API 基础 URL'),
('ai.api_key', '', 'ai', 'API 密钥 (请注意加密存储安全)'),
('ai.model', 'gpt-3.5-turbo', 'ai', '默认使用的模型名称');
