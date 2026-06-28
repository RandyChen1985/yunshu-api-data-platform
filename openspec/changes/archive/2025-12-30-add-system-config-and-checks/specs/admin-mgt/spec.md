# Admin Management Spec

## ADDED Requirements

### Requirement: System Configuration Access
The system MUST provide a "System Configuration" interface accessible ONLY to users with the `admin` role.

#### Scenario: Admin Access
- GIVEN a logged-in user with `role="admin"`
- WHEN they request the system configuration menu or API
- THEN access is granted.

#### Scenario: Non-Admin Access Denial
- GIVEN a logged-in user with `role="user"`
- WHEN they attempt to access system configuration API
- THEN the system returns `403 Forbidden`.

### Requirement: Connection Diagnostics
The system MUST provide on-demand connection testing for critical infrastructure (ClickHouse, Redis) and return detailed execution logs.

#### Scenario: Test ClickHouse Connection
- WHEN an admin triggers a ClickHouse test
- THEN the system attempts to establish a connection and execute a trivial query (e.g., `SELECT 1`).
- AND returns a log including: Host resolution (if applicable), Connection attempt, Authentication status, Query execution result.

#### Scenario: Test Redis Connection
- WHEN an admin triggers a Redis test
- THEN the system attempts to PING the Redis server.
- AND returns execution logs.
