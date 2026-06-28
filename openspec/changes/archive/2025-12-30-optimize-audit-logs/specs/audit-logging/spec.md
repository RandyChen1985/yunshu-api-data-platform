# Audit Logging Specs

## ADDED Requirements

### Requirement: Search logs by Exact username
The system MUST allow administrators to search audit logs using exact usernames. Use exact match to avoid performance issues and ambiguity.

#### Scenario: User searches for "admin"
Given a list of existing audit logs with usernames "admin", "administrator"
When I search for logs with username "admin"
Then I should ONLY see logs for "admin"

### Requirement: Search logs by partial IP
The system MUST allow administrators to search audit logs using partial client IP addresses.

#### Scenario: User searches for subnet "192.168.1"
Given a list of existing audit logs with IPs "192.168.1.1", "192.168.1.10"
When I search for logs with IP "192.168.1"
Then I should see logs for both IPs

## ADDED Requirements

### Requirement: Show formatted JSON in log details
The system MUST format JSON fields (Request Params, Response Body) in the log detail view for better readability.

#### Scenario: Viewing a log with JSON body
Given I am viewing the audit log list
When I click on "Detail" for a log entry with JSON request params
Then I should see the request parameters formatted for readability
