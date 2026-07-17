# Tasks: Add NanZi Resources APIs

## 1. Schema & Adapter
- [x] 1.1 Define schemas in `app/api/v1/schemas/data.py`:
    -   `YunshuRoomResponse`
    -   `YunshuRackResponse`
    -   `YunshuDevicePointResponse`
    -   `NanZiQueryParams` (if specific params needed beyond generic ones)
- [x] 1.2 Update `ClickHouseAdapter.TABLE_MAP` in `app/services/data_adapter.py`.
- [x] 1.3 Update `ClickHouseAdapter.ALLOWED_FIELDS` in `app/services/data_adapter.py`.
- [x] 1.4 Implement result mapping logic in `ClickHouseAdapter.execute`.

## 2. API Implementation
- [x] 2.1 Implement `/yunshu/rooms` endpoint.
- [x] 2.2 Implement `/yunshu/racks` endpoint.
- [x] 2.3 Implement `/yunshu/device-points` endpoint.
- [x] 2.4 Register endpoints in `app/api/v1/endpoints/resources.py`.

## 3. Testing
- [x] 3.1 Create `tests/api/v1/test_resources_nanzi.py`.
- [x] 3.2 Add test cases for Rooms (list & filter).
- [x] 3.3 Add test cases for Racks (list & filter).
- [x] 3.4 Add test cases for Device Points (list & filter).
- [x] 3.5 Run `scripts/test.sh` and verify all tests pass.
- [x] 3.6 Update `tests/CHECKLIST.md`.
