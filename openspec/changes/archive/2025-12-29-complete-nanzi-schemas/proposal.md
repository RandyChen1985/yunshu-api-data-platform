# Change: Complete NanZi Resource Schemas

## Why
目前的 `YunshuRoomResponse`, `YunshuRackResponse`, `YunshuDevicePointResponse` 仅包含少量核心字段，无法满足业务层对全量基础数据的查询需求。我们需要根据 `CLICKHOUSE_TABLES.md` 中的定义，补全这些模型的所有字段。

## What Changes
- **MODIFIED**: `app/api/v1/schemas/data.py`
    - `YunshuRoomResponse`: 增加 `jgzs` (机柜总数), `dz` (地址), `bz` (备注) 等30+个字段。
    - `YunshuRackResponse`: 增加 `akg` (A路开关), `jjlx` (机架类型), `pdulx` (PDU类型) 等40+个字段。
    - `YunshuDevicePointResponse`: 增加 `dwmc` (点位名称), `szwz` (所在位置), `xgsb` (相关设备) 等20+个字段。
    - 所有新增字段均为 `Optional[str]`（因为底层 ClickHouse 定义多为 `Nullable(String)`）。

## Impact
- **影响范围**: `/api/v1/resources/yunshu/*` 接口的返回值结构。
- **风险**: 无逻辑风险，仅增加返回字段。
