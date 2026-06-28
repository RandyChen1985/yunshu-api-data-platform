# Proposal: Add Yunshu Resources APIs (Rooms, Racks, Device Points)

## 1. Goal
Implement the remaining MVP resource APIs for "Yunshu" domain to provide standardized access to datacenter infrastructure metadata:
-   **Rooms (机房)**: `/yunshu/rooms`
-   **Racks (机架)**: `/yunshu/racks`
-   **Device Points (设备点位)**: `/yunshu/device-points`

## 2. Background
According to `architech/design/API_SERVICE_SYSTEM_DESIGN.md`, these APIs are required for the Yunshu Ops Console and AI Agent Platform. They expose data from ClickHouse tables:
-   `ck_fact_yunshu_resroom_hbase`
-   `ck_fact_yunshu_resjj_hbase`
-   `ck_fact_yunshu_devicepoint_hbase`

## 3. Scope
1.  **Schema Definition**: Add Pydantic models for Rooms, Racks, and Device Points in `app/api/v1/schemas/data.py`.
2.  **Data Adapter**: Update `ClickHouseAdapter` in `app/services/data_adapter.py` to support these new resources and their allowed fields.
3.  **API Implementation**: Add new endpoints in `app/api/v1/endpoints/resources.py`.
4.  **Testing**: Create automated tests for these new endpoints.

## 4. Technical Details

### 4.1 Schemas
-   `YunshuRoomResponse`: `rowkey`, `jfbm` (code), `jfmc` (name), `ywzx` (biz center), `gsbs` (company ID).
-   `YunshuRackResponse`: `rowkey`, `jfmc`, `jjbm`, `jjzt` (status), `kh` (customer ID), `khmc` (customer name).
-   `YunshuDevicePointResponse`: `rowkey`, `jf`, `jjbm`, `dwid`, `dwlx` (type).

### 4.2 Endpoints
-   `GET /api/v1/resources/yunshu/rooms`
-   `GET /api/v1/resources/yunshu/racks`
-   `GET /api/v1/resources/yunshu/device-points`

All endpoints will support pagination and standard filtering.

## 5. Success Criteria
-   All three new endpoints return data correctly from ClickHouse.
-   Filtering by key fields (defined in System Design) works.
-   Automated tests pass.
