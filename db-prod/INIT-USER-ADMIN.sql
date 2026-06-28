-- Initialize Admin User
-- Date: 2026-01-08
-- Description: Insert the default admin user with the generated API key.
-- API Key: YZnxdJLZ0Hwf7IpHXHkYDZYI-CUsTafRjGeANklakuA

INSERT INTO `api_users` (`user_name`, `api_key_encrypted`, `api_key_hash`, `role`, `remark`, `status`) 
SELECT 'admin', 'Z0FBQUFBQnBYeVdocW8yX3ZYWFVNa01WQ011TklTR1FZaGRvTlQyWHhlWUNPVUxwTS05MDJuRW1KUVF5ZlN0VnBPRlE4UTgxUUxuWnUtWTI3YzZBZW9feS1faEVTUmVVMWJyMlBIX2k0NVYyRkhiUlp4ZmlNYnY3SFB1aGhHVks4U0EwdXVXY3g3TGE=', '9a422dd05ca65b99e3db72179dff8b78e2b2458c7cce2e2980e341b53f12b331', 'admin', '系统管理员', 1
WHERE NOT EXISTS (SELECT 1 FROM `api_users` WHERE `user_name` = 'admin');
