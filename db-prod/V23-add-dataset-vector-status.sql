-- V23: Add Vector Synchronization Status to Datasets
-- Description: Track whether a dataset has been vectorized and stored in Redis Stack.

SET NAMES utf8mb4;

ALTER TABLE `meta_datasets` 
ADD COLUMN `vector_status` TINYINT DEFAULT 0 COMMENT '向量同步状态: 0-未同步, 1-已同步, 2-同步中, 3-同步失败',
ADD COLUMN `last_vectorized_at` DATETIME DEFAULT NULL COMMENT '最后一次向量化时间';
