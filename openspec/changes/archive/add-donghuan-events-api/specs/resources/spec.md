## ADDED Requirements

### Requirement: Donghuan Events Query
The system MUST provide an API to query historical environmental alarm events.

#### Scenario: List events
- **WHEN** a GET request is sent to `/api/v1/resources/donghuan/events`
- **THEN** return a paginated list of events
- **AND** data is sorted by `event_time` descending by default

#### Scenario: Filter events
- **WHEN** query parameters `event_level` or `resource_id` are provided
- **THEN** only events matching these criteria are returned
