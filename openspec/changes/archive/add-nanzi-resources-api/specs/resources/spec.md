# Spec: NanZi Resources APIs

## 1. Endpoints

### 1.1 List Rooms (机房)
-   **Path**: `/api/v1/resources/yunshu/rooms`
-   **Method**: `GET`
-   **Query Parameters**:
    -   `jfbm`: Optional[str] (Filter by room code)
    -   `jfmc`: Optional[str] (Filter by room name)
    -   `ywzx`: Optional[str] (Filter by business center)
    -   `gsbs`: Optional[str] (Filter by company ID)
    -   `page`: int (Default 1)
    -   `size`: int (Default 20)
-   **Response**: `DataPageResponse[YunshuRoomResponse]`

### 1.2 List Racks (机架)
-   **Path**: `/api/v1/resources/yunshu/racks`
-   **Method**: `GET`
-   **Query Parameters**:
    -   `jfmc`: Optional[str] (Filter by room name)
    -   `jjbm`: Optional[str] (Filter by rack code)
    -   `jjzt`: Optional[str] (Filter by rack status)
    -   `khmc`: Optional[str] (Filter by customer name)
    -   `page`: int (Default 1)
    -   `size`: int (Default 20)
-   **Response**: `DataPageResponse[YunshuRackResponse]`

### 1.3 List Device Points (设备点位)
-   **Path**: `/api/v1/resources/yunshu/device-points`
-   **Method**: `GET`
-   **Query Parameters**:
    -   `jf`: Optional[str] (Filter by room)
    -   `jjbm`: Optional[str] (Filter by rack code)
    -   `dwid`: Optional[str] (Filter by point ID)
    -   `dwlx`: Optional[str] (Filter by point type)
    -   `page`: int (Default 1)
    -   `size`: int (Default 20)
-   **Response**: `DataPageResponse[YunshuDevicePointResponse]`

## 2. Data Source Mapping

| Resource | Logical Name | Table Name | Key Fields |
| :--- | :--- | :--- | :--- |
| Rooms | `yunshu_rooms` | `ck_fact_yunshu_resroom_hbase` | `jfbm`, `jfmc`, `ywzx`, `gsbs` |
| Racks | `yunshu_racks` | `ck_fact_yunshu_resjj_hbase` | `jfmc`, `jjbm`, `jjzt`, `kh`, `khmc` |
| Device Points | `yunshu_device_points` | `ck_fact_yunshu_devicepoint_hbase` | `jf`, `jjbm`, `dwid`, `dwlx` |

## 3. Implementation Logic
1.  Extend `app/api/v1/schemas/data.py` with new Pydantic models.
2.  Extend `app/services/data_adapter.py`:
    -   Add mappings to `TABLE_MAP`.
    -   Add whitelist to `ALLOWED_FIELDS`.
    -   Update `execute` method to handle result set mapping for new resources.
3.  Add new router functions in `app/api/v1/endpoints/resources.py`.
