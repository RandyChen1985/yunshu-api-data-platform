## ADDED Requirements

### Requirement: Full-Field Resource Response
The API MUST return all available columns from the underlying data warehouse tables for Yunshu resources (Rooms, Racks, Device Points).

#### Scenario: Complete Room Details
- **WHEN** 查询 `/yunshu/rooms` 接口。
- **THEN** 返回的 JSON 对象必须包含 `jgzs` (机柜总数), `dz` (地址), `bz` (备注) 等全量属性，而不仅仅是基础的编码和名称。

#### Scenario: Complete Rack Details
- **WHEN** 查询 `/yunshu/racks` 接口。
- **THEN** 返回的数据必须包含电力信息（`ac19`, `bzdl`）、PDU 信息（`pdulx`, `apdu`, `bpdu`）以及合同客户信息。
