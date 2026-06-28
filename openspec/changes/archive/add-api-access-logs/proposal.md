# Proposal: API Access Logging (MySQL)

## 1. Goal
Implement a comprehensive API access logging system that stores request/response metadata in the MySQL metadata database. This will provide audit trails, debugging capabilities, and basic usage analytics.

## 2. Background
Currently, the system lacks persistent logging of API requests. While transient logs might exist in stdout, structured storage is required for:
-   Security auditing (who accessed what).
-   Performance monitoring (slow queries).
-   Debugging (traceability via `trace_id`).
-   Usage statistics (QPS per user/endpoint).

The user explicitly requested storing these logs in **MySQL**.

## 3. Scope
1.  **Database Schema**: Create `api_access_logs` table in MySQL.
2.  **Middleware**: Implement a FastAPI Middleware to capture request lifecycle events.
3.  **Traceability**: Ensure `trace_id` generation and propagation.
4.  **Asynchronous Writing**: Ensure logging does not block the main request loop significantly.

## 4. Technical Approach
-   **Schema**:
    -   `id` (PK), `trace_id`, `user_id`, `endpoint`, `method`, `status_code`, `process_time`, `client_ip`, `created_at`.
-   **Middleware**:
    -   Intercepts request.
    -   Starts timer.
    -   Generates `trace_id`.
    -   Awaits response.
    -   Calculates duration.
    -   Extracts user context (from `request.state` populated by Auth).
    -   Spawns a background task to write to MySQL via `aiomysql`.

## 5. Success Criteria
-   Every API request results in a row in `api_access_logs`.
-   `trace_id` is returned in response headers.
-   Performance impact is negligible (< 10ms overhead).
