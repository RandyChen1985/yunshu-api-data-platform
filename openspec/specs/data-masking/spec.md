# Data Masking Spec

## Purpose
To protect sensitive data from unauthorized exposure by automatically masking field values based on configurable rules and role-based policies.

## Requirements

### Requirement: Three-Level Strategy
The system SHALL determine whether to apply masking based on a priority-based strategy: User Settings > Role Settings > Global Settings.

#### Scenario: User override role
- **WHEN** a user's role is set to "Force Masking" but the user's personal setting is "Allow Plaintext"
- **THEN** the system SHALL return unmasked data (if they have the permission)

#### Scenario: Role override global
- **WHEN** global setting is "Masking ON" but the user's role is "Allow Plaintext"
- **THEN** the system SHALL return unmasked data

### Requirement: Dynamic Rule Matching
The system SHALL recursively scan all API response data (dicts and lists) and apply masking rules based on field names matching configured patterns.

#### Scenario: Field matching with wildcards
- **WHEN** a response contains "personal_phone" and a rule exists for "*phone*"
- **THEN** the value SHALL be masked using the assigned algorithm

### Requirement: Management and Guidance
The configuration UI SHALL provide examples and a preview of masking effects.

#### Scenario: Rule configuration preview
- **WHEN** an admin selects "Mobile Mask" algorithm
- **THEN** the UI SHALL show a preview like "13800138000 -> 138****8000"
