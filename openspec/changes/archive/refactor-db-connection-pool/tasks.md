## 1. Implementation
- [x] 1.1 Modify `app/core/database.py` to implement `asynch.pool.Pool`
- [x] 1.2 Update `get_clickhouse_connection` to act as an async context manager
- [x] 1.3 Register pool init/shutdown in `app/main.py` lifespan
- [x] 1.4 Refactor `app/services/data_adapter.py` to use `async with` syntax
- [x] 1.5 Verify connection pooling with test script
