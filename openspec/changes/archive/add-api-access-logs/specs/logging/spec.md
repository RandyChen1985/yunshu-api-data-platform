# Spec: API Access Logging

## 1. Database Schema

### Table: `api_access_logs`

| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | BIGINT | PK, Auto Inc | Unique Log ID |
| `trace_id` | VARCHAR(64) | NOT NULL, Index | Distributed Trace ID |
| `user_id` | BIGINT | Nullable | ID of the API user (if authenticated) |
| `user_name` | VARCHAR(64) | Nullable | Username snapshot |
| `endpoint` | VARCHAR(255) | NOT NULL | API Path (e.g., `/api/v1/resources/...`) |
| `method` | VARCHAR(10) | NOT NULL | HTTP Method (GET, POST) |
| `query_params` | TEXT | Nullable | JSON string of query parameters |
| `status_code` | INT | NOT NULL | HTTP Response Code |
| `process_time_ms` | FLOAT | NOT NULL | Execution time in milliseconds |
| `client_ip` | VARCHAR(45) | Nullable | Client IP Address |
| `user_agent` | VARCHAR(255)| Nullable | User Agent string |
| `created_at` | TIMESTAMP | Default NOW() | Log timestamp |

## 2. Middleware Logic (`app.core.middleware.AccessLogMiddleware`)

### 2.1 Trace ID
-   Check `X-Trace-Id` (or configured header name) in request.
-   If missing, generate a UUID4.
-   Set `request.state.trace_id`.
-   Add `X-Trace-Id` to Response headers.

### 2.2 Logging Flow
1.  **Pre-processing**:
    -   Start timer (`start_time = time.time()`).
2.  **Call Next**:
    -   `response = await call_next(request)`
3.  **Post-processing**:
    -   End timer.
    -   Extract `user_id` from `request.state.user` (need to ensure Auth middleware/dependency populates this).
    -   Format `query_params` as JSON.
    -   Create a background task (`BackgroundTasks` or `asyncio.create_task`) to execute the SQL INSERT.
    -   **Constraint**: If `user_id` is missing (e.g., 401 Unauthorized), log with `user_id=NULL`.

## 3. Implementation Details

-   **SQL**:
    ```sql
    INSERT INTO api_access_logs 
    (trace_id, user_id, user_name, endpoint, method, query_params, status_code, process_time_ms, client_ip, user_agent)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ```
-   **Error Handling**:
    -   Logging failures must **NOT** fail the API request. Use `try...except` block within the background logging function.

## 4. Updates to Existing Components
-   **`app/main.py`**: Register the new middleware.
-   **`app/core/database.py`**: Ensure `init_db` creates the new table.
-   **`app/api/v1/endpoints/resources.py`**: Ensure Auth dependency sets `request.state.user`.
