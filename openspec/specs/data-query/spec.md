# data-query Specification

## Purpose
TBD - created by archiving change implement-generic-query. Update Purpose after archive.
## Requirements
### Requirement: Generic Logical Query
The system MUST provide a generic query interface allowing clients to express data requirements via a logical structure without writing SQL.
系统必须提供通用查询接口，允许客户端通过逻辑结构表达数据需求，而无需编写 SQL。

#### Scenario: Basic Query
- WHEN sending a `POST` request to `/api/v1/query` with body:
  ```json
  {
    "resource": "donghuan_real_metrics",
    "filters": [["metric_value", ">", "30"]],
    "page": 1,
    "size": 10
  }
  ```
- THEN the response status should be 200
- AND the data items should strictly match the filtering criteria (value > 30).

#### Scenario: Resource Validation
- WHEN querying a non-existent or unauthorized `resource` (e.g., "unknown_table")
- THEN the system MUST return a 400 Bad Request or 403 Forbidden error
- AND MUST NOT execute any database query.

#### Scenario: Pagination Metadata
- WHEN querying valid data
- THEN the response `data` object MUST include standard pagination fields: `total`, `page`, `size`, `pages`.

