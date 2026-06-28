# Data Adapter Spec

## MODIFIED Requirements

### Requirement: Legacy Authentication Support
The system MUST support connecting to ClickHouse instances that use legacy authentication schemes (e.g., Default user with no password).

#### Scenario: Empty Password Configuration
- GIVEN the configuration `CLICKHOUSE_PASSWORD` is set to an empty string or null
- WHEN the adapter initializes a connection
- THEN it passes the password as an empty string to the driver (not None, if driver expects string) or handles it such that authentication succeeds for the `default` user.
