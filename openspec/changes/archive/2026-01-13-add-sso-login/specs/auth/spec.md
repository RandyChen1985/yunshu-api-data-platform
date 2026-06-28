## ADDED Requirements
### Requirement: Users MUST be able to log in with SSO
The system MUST allow users to authenticate using Yovole Single Sign-On (SSO).

#### Scenario: SSO Login Success
- **WHEN** a user provides valid SSO credentials (username and password)
- **THEN** the system calls the Yovole SSO API for verification
- **AND** if verification succeeds, the system creates or binds the local user
- **AND** the system returns a successful authentication response with user information and API Key

#### Scenario: SSO Login Failure - Invalid Credentials
- **WHEN** a user provides invalid SSO credentials
- **THEN** the system receives a failure response from the Yovole SSO API
- **AND** the system returns a 401 Unauthorized error

#### Scenario: SSO Login Failure - API Timeout
- **WHEN** the Yovole SSO API does not respond within the configured timeout
- **THEN** the system returns a 503 Service Unavailable error
- **AND** the system suggests using alternative login methods

#### Scenario: SSO User Lookup
- **WHEN** SSO authentication succeeds
- **THEN** the system queries the local database for the user by username
- **AND** the system verifies the user status is active (status=1)
- **AND** the system returns the user information and API Key

#### Scenario: SSO User Not Found
- **WHEN** SSO authentication succeeds but the user does not exist in the local database
- **THEN** the system returns a 401 Unauthorized error
- **AND** the system suggests the user contact an administrator to create an account

#### Scenario: SSO User Disabled
- **WHEN** SSO authentication succeeds but the user is disabled in the local database
- **THEN** the system returns a 401 Unauthorized error
- **AND** the system indicates the user account is disabled

### Requirement: System MUST support SSO configuration
The system MUST allow administrators to configure SSO parameters through environment variables.

#### Scenario: SSO Configuration
- **WHEN** the system starts
- **THEN** the system loads SSO configuration from environment variables
- **AND** the configuration includes SSO API URL, Access Token, Request System, Request Business, and Timeout

### Requirement: SSO authentication MUST be secure
The system MUST ensure SSO credentials are transmitted securely and not logged.

#### Scenario: Secure SSO Transmission
- **WHEN** the system calls the Yovole SSO API
- **THEN** the system uses HTTPS in production environments
- **AND** the system does not log SSO credentials
- **AND** the system stores the Access Token in environment variables

## MODIFIED Requirements
### Requirement: System MUST reserve structure for SSO
The database schema MUST support Single Sign-On integrations with Yovole SSO.

#### Scenario: SSO Schema Support
The database schema supports storing SSO source (yovole), SSO ID, and email, allowing future SSO features without schema changes.

#### Scenario: SSO User Lookup
The system can query users by username to retrieve user information after SSO authentication succeeds.
