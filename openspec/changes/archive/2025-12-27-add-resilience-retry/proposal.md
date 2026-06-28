# Proposal: System Resilience & Retry Mechanism

## 1. Background
Currently, the system interacts directly with ClickHouse and MySQL without any retry logic. Transient failures (e.g., network blips, database restarts, connection pool exhaustion) cause immediate HTTP 500 errors for users.

## 2. Objectives
- Improve system stability by automatically recovering from transient errors.
- Provide graceful degradation and clear error messages when downstream services are unavailable (HTTP 503 instead of generic 500).

## 3. Tech Stack
- **Library**: `tenacity` (Robust retry library for Python).

## 4. Scope of Changes

### 4.1 Dependency Management
- **File**: `requirements.txt`
- **Change**: Add `tenacity`.

### 4.2 Database Connection Resilience
- **File**: `app/core/database.py`
- **Change**:
    - Decorate `init_db` and `init_clickhouse` with `@retry`.
    - Use `wait_exponential` (e.g., 1s, 2s, 4s) and `stop_after_attempt(3)`.
    - Log retry attempts using standard logger.

### 4.3 Query Execution Resilience
- **File**: `app/services/data_adapter/clickhouse.py`
- **Change**:
    - Decorate `execute` and `execute_summary` methods.
    - **Retry Condition**: Retry ONLY on `asynch.errors.InterfaceError` (Connection issues) or specific network errors. DO NOT retry on `ServerException` (Syntax/Data errors).

### 4.4 Global Exception Handling
- **File**: `app/main.py`
- **Change**:
    - Add a global exception handler for DB connection errors.
    - Return HTTP `503 Service Unavailable` with a "Retry-After" header when max retries are exhausted.

## 5. Verification Plan
- **Unit Test**: Mock the database driver to throw a connection error 2 times then succeed on the 3rd. Verify the operation succeeds.
- **Integration Test**: Verify that persistent connection failures eventually raise 503.
