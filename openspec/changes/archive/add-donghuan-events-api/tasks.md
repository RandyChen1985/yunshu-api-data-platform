## 1. Schema & Adapter
- [x] 1.1 Define `DonghuanEventResponse` schema in `app/api/v1/schemas/data.py`
- [x] 1.2 Update `ClickHouseAdapter.TABLE_MAP` and `ALLOWED_FIELDS` in `app/services/data_adapter.py`

## 2. API Implementation
- [x] 2.1 Implement `/donghuan/events` endpoint in `app/api/v1/endpoints/resources.py`
- [x] 2.2 Add filtering logic for `event_level`, `event_type`, `event_status`

## 3. Testing
- [x] 3.1 Create `tests/api/v1/test_resources_donghuan_events.py`
- [x] 3.2 Verify tests pass
- [x] 3.3 Update `tests/CHECKLIST.md`
