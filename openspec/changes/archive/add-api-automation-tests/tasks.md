## 1. Preparation
- [x] 1.1 Add `pytest-asyncio` to `requirements.txt`
- [x] 1.2 Create `tests/` directory structure (`tests/api/v1`, `tests/core`)

## 2. Infrastructure
- [x] 2.1 Create `tests/conftest.py` with fixtures for:
    -   `event_loop` (session scope)
    -   `client` (AsyncClient for FastAPI app)
    -   `db_pool` (Mock or Real connection handling if needed)

## 3. Implementation
- [x] 3.1 Create `tests/api/v1/test_resources_donghuan.py`
    -   Test case: Get real metrics (Success 200)
    -   Test case: Filter by time range
    -   Test case: Unauthorized (401)
- [x] 3.2 Create `scripts/test.sh` for easy execution

## 4. Verification
- [x] 4.1 Run `pytest` to ensure all tests pass
