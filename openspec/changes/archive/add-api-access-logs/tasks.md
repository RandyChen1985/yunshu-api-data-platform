# Tasks: Add API Access Logs

## 1. Database Schema
- [x] 1.1 Create `scripts/init_db_access_logs.py` (or update `init_db.py`) to create `api_access_logs` table.
- [x] 1.2 Run initialization to create the table in MySQL.

## 2. Middleware Implementation
- [x] 2.1 Create `app/core/middleware.py`.
- [x] 2.2 Implement `AccessLogMiddleware` class.
- [x] 2.3 Implement async logging function (insert into MySQL).

## 3. Integration
- [x] 3.1 Register middleware in `app/main.py`.
- [x] 3.2 Update `app/api/v1/endpoints/resources.py` (and others) to populate `request.state.user` upon successful auth.

## 4. Testing
- [x] 4.1 Create `tests/core/test_logging.py`.
- [x] 4.2 Verify logs are written to MySQL after request.
- [x] 4.3 Verify `trace_id` is returned in headers.
- [x] 4.4 Verify logging does not crash app on DB failure (mock DB failure).
