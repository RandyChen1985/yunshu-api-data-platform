# Design: User Authentication Architecture

## Database Schema Changes

### Table: `api_users` (Modified)
We will extend the existing `api_users` table to support password and SSO.

```sql
ALTER TABLE api_users
ADD COLUMN password_hash VARCHAR(255) COMMENT 'Bcrypt hash of the password',
ADD COLUMN sso_source VARCHAR(50) DEFAULT NULL COMMENT 'Source of SSO (e.g., "YES")',
ADD COLUMN sso_id VARCHAR(255) DEFAULT NULL COMMENT 'Unique ID from the SSO provider',
ADD COLUMN email VARCHAR(255) DEFAULT NULL COMMENT 'User email for notifications/recovery',
ADD INDEX idx_sso (sso_source, sso_id);
```

## Architecture

### Authentication Service (`AuthService`)
- **New Method**: `verify_password(username, password)` -> `User`
- **New Method**: `login_with_sso(sso_source, sso_data)` -> `User` (Reserved)
- **Update**: `create_user` to accept optional password.

### API Layer
- **New Router**: `LoginRouter` mounted at `/api/portal/auth`.
- **Endpoints**:
    - `POST /login`: Authenticate with username/password.
    - `POST /logout`: Clear session.
    - `GET /me`: Get current user info.

## Security Considerations
- **Password Hashes**: Use `bcrypt` (via `passlib` or similar) with appropriate work factor.
- **Session Tokens**: Use secure, HttpOnly cookies for session tokens if applicable, or return JWTs.
