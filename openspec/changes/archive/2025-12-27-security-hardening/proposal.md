# Proposal: System Security Hardening

## 1. Background
Recent security analysis revealed potential vulnerabilities in the system:
1.  **SQL Injection Risk**: The ClickHouse adapter manually constructs SQL strings using f-strings and basic escaping, which is prone to injection attacks.
2.  **Authentication Gaps**: Admin Portal APIs (`/api/portal/*`) rely on per-endpoint checks, which is error-prone. Documentation endpoints (`/docs`, `/redoc`) are publicly accessible.
3.  **Information Leakage**: `key.txt` is tracked by git/not ignored.

## 2. Objectives
- Eliminate SQL injection risks in the Data Adapter layer.
- Enforce "Secure by Default" authentication for all Admin APIs.
- Restrict access to API documentation.
- Prevent sensitive file leakage.

## 3. Scope of Changes

### 3.1 ClickHouse Adapter Refactoring
- **File**: `app/services/data_adapter/clickhouse.py`
- **Change**: 
    - Remove `manual_bind=True` logic.
    - Update `execute` and `execute_summary` to strictly use `cursor.execute(sql, params)`.
    - Ensure `LogicalQuery` filters are correctly mapped to ClickHouse driver parameters (e.g., `%(name)s` syntax).

### 3.2 Admin API Protection
- **File**: `app/api/portal/api.py`
- **Change**: 
    - Apply `Depends(require_admin)` (or a new `require_portal_auth`) globally to the `portal_router`.
    - Exclude `/auth` (login) from this global requirement.

### 3.3 Documentation Security
- **File**: `app/main.py`, `app/api/portal/endpoints/auth.py`
- **Change**:
    - **Auth Update**: Update `/api/portal/auth/login` to set an `httpOnly` cookie containing the access token (or a flag) upon successful login.
    - **Docs Protection**: 
        - Disable default OpenAPI URLs.
        - Create `/docs` and `/redoc` endpoints.
        - Add a dependency `get_current_user_from_cookie` to these endpoints.
        - If cookie is missing/invalid, redirect to `/login` (frontend login page).

### 3.4 Git Configuration
- **File**: `.gitignore`
- **Change**: Add `key.txt`.

### 3.5 Security Headers (Optional but Recommended)
- **File**: `app/main.py`
- **Change**: Add middleware to set `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`.

## 4. Verification Plan
- **SQL Injection**: Attempt to inject malicious SQL via the `/query` API (e.g., `' OR '1'='1`). Expect generic error or safe execution, not data dump.
- **Auth**: Try accessing `/api/portal/dashboard` without a token. Expect 401/403.
- **Docs**: Access `/docs` in incognito. Expect browser login prompt.
