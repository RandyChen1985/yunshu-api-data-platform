# 规格：管理密钥 (Admin Key Management)

## ADDED Requirements

### Requirement: API Key Creation
The system MUST allow authorized admins (系统必须允许授权管理员) to create a new API Key for a named user.

#### Scenario: Create Success
- WHEN sending a `POST` request to `/api/v1/keys` with a unique `user_name`
- THEN the response status should be 200
- AND the response body contains plain-text `api_key` and `user_name`
- AND the key works in subsequent requests (via "X-API-Key" header).

#### Scenario: Duplicate User Handling
- WHEN attempting to create a key for an existing `user_name`
- THEN the system should handle the database unique constraint gracefully.
