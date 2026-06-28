-- V24: Add Metadata Health Score and Report fields
-- Description: Store AI Readiness score and actionable optimization items for each dataset.

ALTER TABLE `meta_datasets` 
ADD COLUMN `health_score` INT DEFAULT 0 COMMENT 'AI健康分 (0-100)',
ADD COLUMN `health_report` JSON COMMENT '健康检查报告：包含失分项、优化建议等';
