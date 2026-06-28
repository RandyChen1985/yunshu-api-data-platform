# 提案：实现基于资源的细粒度权限控制

## 1. 背景
当前系统使用 API Key 进行认证，区分 `admin` 和 `user` 两种角色。
- `admin`：拥有所有权限。
- `user`：默认也拥有所有 API 访问权限（现状）。

需求是：**普通用户（user）不应默认访问所有接口，必须经过显式授权才能访问特定的数据资源。** 管理员（admin）保持全量权限。

## 2. 目标
1.  **权限模型定义**：利用 `api_users` 表现有的 `permissions` JSON 字段，定义 `allowed_resources` 列表。
2.  **后端鉴权逻辑**：
    - 对于 `admin`，跳过检查。
    - 对于 `user`，检查请求的目标资源（如 `donghuan_real_metrics`）是否在 `allowed_resources` 列表中。
3.  **覆盖范围**：
    - `/api/v1/resources/*` 下的所有具体资源接口。
    - `/api/v1/query` 通用查询接口。

## 3. 实施方案

### 3.1 数据模型
在 `api_users.permissions` 字段中存储如下结构：
```json
{
  "allowed_resources": [
    "donghuan_real_metrics", 
    "donghuan_events",
    "yunshu_rooms"
  ]
}
```
若列表为空，则无权访问任何资源。

### 3.2 代码变更
1.  **`app/core/dependencies.py`**:
    - 新增 `verify_resource_access(user, resource_name)` 函数。
    - 新增 `check_resource_permission(resource_name)` 依赖工厂，用于路由装饰器。

2.  **`app/api/v1/endpoints/resources.py`**:
    - 在每个 `@router.get` 装饰器或函数参数中添加 `Depends(check_resource_permission("resource_name"))`。

3.  **`app/api/v1/endpoints/query.py`**:
    - 在函数体内部调用 `verify_resource_access(user, query_in.resource)`，因为资源名在请求体中，无法在路由依赖阶段直接获取。

### 3.3 测试计划
- 新增测试用例：
    - 创建一个只有 `donghuan_real_metrics` 权限的用户。
    - 验证该用户访问 `donghuan_events` 返回 403 Forbidden。
    - 验证该用户访问 `donghuan_real_metrics` 返回 200 OK。
    - 验证 admin 用户访问任意资源返回 200 OK。

## 4. 影响范围
- 仅影响 `api/v1` 数据接口，不影响管理后台 API。
- 需要通知管理员后续创建用户时需指定资源权限。
