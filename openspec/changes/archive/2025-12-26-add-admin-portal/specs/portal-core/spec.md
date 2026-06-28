# 规格：门户核心功能 (Portal Core)

## ADDED Requirements

### Requirement: Portal Access
The system MUST provide a web interface accessible via API Key authentication.
系统必须提供通过 API Key 认证访问的 Web 界面。

#### Scenario: Login with Key
- WHEN a user enters a valid API Key on the login page
- THEN they MUST take into the dashboard
- AND the UI MUST adapt to their role (Admin or Regular User).

### Requirement: Self-Hosted Frontend
The system MUST serve the frontend application directly without external web servers.
系统必须直接通过 Python 服务托管前端应用，无需外部 Web 服务器。

#### Scenario: Static File Serving
- WHEN accessing the root URL `/`
- THEN the system MUST return the frontend entry point (`index.html`).
- WHEN accessing non-API paths (e.g. `/dashboard`)
- THEN the system MUST fallback to `index.html` to support SPA routing.

### Requirement: User Self-Service
Regular users MUST be able to view their own profile and access logs.
普通用户必须能够查看自己的资料和访问日志。

#### Scenario: View Audit Logs
- WHEN a user visits the "Audit Logs" page
- THEN they MUST see a paginated list of their own API calls
- AND sensitive fields (if any) MUST be masked.

### Requirement: API Playground
The portal MUST include an interactive tool for testing APIs.
门户必须包含用于测试 API 的交互式工具。

#### Scenario: Test Query API
- WHEN a user selects the "Generic Query" template in the playground
- AND clicks "Run"
- THEN the real API result MUST be displayed in JSON format.
