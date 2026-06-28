# Prevent Delete Used Datasource

## Goal
Prevent administrators from deleting a data source if it is currently being used by any API resource.

## Context
Currently, deleting a data source that is in use breaks the API resources that depend on it. This change adds a safety check.

## Scope
- Backend: `DataSourceService`
- API: `DELETE /datasources/{id}`

## Verification Plan
### Automated Tests
- Test deleting an unused datasource (should succeed).
- Test deleting a used datasource (should fail with 400).

### Manual Verification
1. Create a dummy datasource.
2. Link a dummy resource to it.
3. Try to delete the datasource (expect error).
4. Delete the resource.
5. Try to delete the datasource (expect success).
