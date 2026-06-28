# Proposal: Refine User Management Logic

## Goal
Optimize user management security and usability by protecting the system admin account and ensuring API key operations are isolated.

## Context
The system has a built-in `admin` account initialized by scripts. Currently, it is possible for an admin to accidentally delete this super-admin account, which would lock out system management. Additionally, the user wants to explicitly ensure that resetting an API key never impacts identity fields like the username.

## Changes
1.  **Backend Protection**: Update `DELETE /users/{id}` to strictly forbid deleting the user with `user_name="admin"`.
2.  **Frontend UX**: In the User Management list, disable the "Delete" action for the `admin` user to prevent accidental clicks.
3.  **API Key Isolation**: Verify and ensure the `reset-api-key` flow stays strictly isolated from user profile updates (current architecture supports this, will lock it down with tests/specs).

## Risk
Low. This is a restrictive change (preventing actions) rather than an expansive one.
