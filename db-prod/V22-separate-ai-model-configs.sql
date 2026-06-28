-- V22: Separate AI Model Configurations
-- Description: Allow independent Base URL and API Key for Chat, Embedding, and Reranking models.

SET NAMES utf8mb4;

-- 1. Initialize independent config for Embedding
INSERT INTO `sys_config` (`config_key`, `config_value`, `config_group`) VALUES 
('ai.embed_base_url', 'https://api.openai.com/v1', 'ai'),
('ai.embed_api_key', '', 'ai')
ON DUPLICATE KEY UPDATE `config_value` = VALUES(`config_value`);

-- 2. Initialize independent config for Rerank
INSERT INTO `sys_config` (`config_key`, `config_value`, `config_group`) VALUES 
('ai.rerank_base_url', '', 'ai'),
('ai.rerank_api_key', '', 'ai')
ON DUPLICATE KEY UPDATE `config_value` = VALUES(`config_value`);
