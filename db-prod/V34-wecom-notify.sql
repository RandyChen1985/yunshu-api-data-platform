-- V34: 企业微信群机器人审批通知配置
-- Date: 2026-07-01

SET NAMES utf8mb4;

INSERT IGNORE INTO sys_config (config_key, config_value, config_group, remark) VALUES
('notify.wecom.enabled', 'false', 'notify', '启用企业微信群机器人通知'),
('notify.wecom.webhook_url', '', 'notify', '企微群机器人 Webhook 地址（含 key 参数）'),
('notify.wecom.secret', '', 'notify', '企微机器人加签密钥（可选）'),
('notify.wecom.on_request', 'true', 'notify', '新权限申请时推送'),
('notify.wecom.on_result', 'true', 'notify', '审批通过/拒绝时推送');
