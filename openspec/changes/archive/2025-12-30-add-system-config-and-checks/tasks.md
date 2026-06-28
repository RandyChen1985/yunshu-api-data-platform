# Task List

- [x] **Backend: Configuration Update** <!-- id: 0 -->
    - [x] Update `app/core/config.py` to make `CLICKHOUSE_PASSWORD` optional.
    - [x] Update `app/core/database.py` to handle empty password logic for ClickHouse.
- [x] **Backend: MySQL Startup Check** <!-- id: 1 -->
    - [x] Modify `app/core/database.py`'s `init_db` to execute `SELECT 1` after connection pool creation.
    - [x] Log the result of the health check.
- [x] **Backend: System API** <!-- id: 2 -->
    - [x] Create `app/api/portal/system.py` endpoint module.
    - [x] Implement `POST /api/portal/system/test-connection/{component}` (clickhouse, redis).
    - [x] Ensure endpoints are protected by `Admin` role.
    - [x] Return structured logs in response (e.g. `{"status": "ok", "logs": ["Connecting...", "Success"]}`).
    - [x] Register new router in `app/main.py`.
- [x] **Frontend: System Config Page** <!-- id: 3 -->
    - [x] Create `frontend/src/views/SystemConfig.vue`.
    - [x] Implement UI with "Test Connection" buttons and log display console.
    - [x] Integrate with `test-connection` API.
- [x] **Frontend: Menu & Routing** <!-- id: 4 -->
    - [x] Update `frontend/src/router/index.ts` to add `/system` route (admin only).
    - [x] Update Sidebar component to show "系统配置" link for admins.
- [x] **Frontend: UI/UX Optimization** <!-- id: 6 -->
    - [x] Refactor notification system with global `useToast` and `ToastContainer`.
    - [x] Enhance User Management list with `Switch` component for status.
    - [x] Update action icons for a cleaner look.
- [x] **Testing: Automated Test Fixes** <!-- id: 7 -->
    - [x] Fix `test_system.py` assertions to match global exception handler.
    - [x] Seed `api_key_encrypted` in `conftest.py` to fix API key retrieval tests.
    - [x] Verify all 75 tests passed.

