# Refactor Interface Management Module

## Goal Description
Refactor the "Metadata Configuration" module to "Interface Management" to better reflect its purpose. Enhance the user experience by adding tooltips for resource remarks, supporting status-based filtering, and standardizing data type configuration.

## Why
- **Clarity**: "Metadata Configuration" is too technical; "Interface Management" is more business-aligned.
- **Usability**: Users need to see remarks quickly (via tooltip) without opening the edit page. Filtering by status is a common need for managing many interfaces.
- **Standardization**: Free-text data types lead to errors. constraining them to `String`, `Long`, `Date` improves consistency and documentation quality.

## What Changes

### UI Renaming
- Rename page title from "元数据配置" to "接口管理".

### Resource List Enhancements
- Add "Status" filter (Enabled/Disabled/All) to the search bar.
- Add tooltip to "Resource Name" column displaying the `remarks` field.
- Ensure `remarks` field is available in the resource list API response.
- **Export**: Add button to each row to download specific resource configuration as JSON.
- **Import**: Add "Import Resource" button next to "New Resource". Supports uploading JSON to pre-fill the creation form.

### Data Type Standardization
- In `ResourceEdit.vue` (Fields Config and Allowed Filters):
    - Change "Data Type" input from Text to Select.
    - Options: `String`, `Long`, `Date`.
    - Logic: When importing from DB, map `Nullable(String)` and similar variants to `String`.
