## ADDED Requirements

### Requirement: Automated API Testing
The system MUST provide an automated testing suite to verify API behavior, data correctness, and security constraints.

#### Scenario: Verify Donghuan Real Metrics
- **WHEN** a GET request is sent to `/api/v1/resources/donghuan/real-metrics` with a valid API Key
- **THEN** the system returns HTTP 200 OK
- **AND** the response body contains a paginated list of metric data
- **AND** the data schema matches the defined `DonghuanRealMetricResponse`

#### Scenario: Unauthorized Access
- **WHEN** a request is sent without a valid `X-API-Key`
- **THEN** the system returns HTTP 401 Unauthorized

#### Scenario: Data Filtering
- **WHEN** query parameters `start_time` and `end_time` are provided
- **THEN** the returned data is strictly within the specified time range
