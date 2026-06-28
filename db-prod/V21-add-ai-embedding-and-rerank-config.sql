-- V21: Add AI Embedding and Rerank Model Configurations
-- Description: Add configuration keys for embedding and reranking models to support enhanced RAG.

SET NAMES utf8mb4;

-- 1. Initialize Embedding Model Config
INSERT INTO `sys_config` (`config_key`, `config_value`, `config_group`) 
VALUES ('ai.embed_model', 'text-embedding-3-small', 'ai')
ON DUPLICATE KEY UPDATE `config_value` = VALUES(`config_value`);

-- 2. Initialize Rerank Model Config
INSERT INTO `sys_config` (`config_key`, `config_value`, `config_group`) 
VALUES ('ai.rerank_model', 'bge-reranker-v2-m3', 'ai')
ON DUPLICATE KEY UPDATE `config_value` = VALUES(`config_value`);
