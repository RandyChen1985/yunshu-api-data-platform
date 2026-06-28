# 规格：用户管理功能

## 后端 API 规格

### 1. 获取用户列表

**接口**: `GET /api/portal/management/users`

**权限**: 仅管理员

**请求参数**:
```
page: int = 1           # 页码
size: int = 20          # 每页条数
search: str = None      # 搜索关键词（用户名）
role: str = None        # 角色筛选 (admin/user/all)
status: int = None      # 状态筛选 (1=启用, 0=禁用)
```

**响应示例**:
```json
{
  "total": 100,
  "page": 1,
  "size": 20,
  "items": [
    {
      "id": 1,
      "user_name": "admin",
      "role": "admin",
      "status": 1,
      "permissions": {"access": ["read", "write"]},
      "created_at": "2025-12-26T10:00:00",
      "updated_at": "2025-12-26T10:00:00"
    }
  ]
}
```

---

### 2. 创建用户

**接口**: `POST /api/portal/management/users`

**权限**: 仅管理员

**请求体**:
```json
{
  "user_name": "new_user",
  "role": "user",  // "admin" or "user"
  "permissions": {"access": ["read"]}
}
```

**响应示例**:
```json
{
  "id": 123,
  "user_name": "new_user",
  "role": "user",
  "api_key": "xxxxxxxxxxx",  // 完整 Key，仅此次返回
  "status": 1,
  "created_at": "2025-12-27T10:00:00"
}
```

**业务规则**:
- 用户名必须唯一
- 自动生成 API Key（32字节 URL-safe base64）
- 默认状态为启用（status=1）

---

### 3. 更新用户信息

**接口**: `PUT /api/portal/management/users/{user_id}`

**权限**: 仅管理员

**请求体**:
```json
{
  "role": "admin",  // 可选
  "permissions": {"access": ["read", "write"]}  // 可选
}
```

**响应示例**:
```json
{
  "id": 123,
  "user_name": "new_user",
  "role": "admin",
  "permissions": {"access": ["read", "write"]},
  "updated_at": "2025-12-27T11:00:00"
}
```

---

### 4. 切换用户状态

**接口**: `PATCH /api/portal/management/users/{user_id}/status`

**权限**: 仅管理员

**请求体**:
```json
{
  "status": 0  // 1=启用, 0=禁用
}
```

**业务规则**:
- 禁用后该用户的 API Key 立即失效
- 不能禁用当前登录的管理员自己

---

### 5. 删除用户

**接口**: `DELETE /api/portal/management/users/{user_id}`

**权限**: 仅管理员

**响应**:
```json
{
  "message": "User deleted successfully"
}
```

**业务规则**:
- 软删除或硬删除（建议软删除，设置 deleted_at）
- 不能删除当前登录的管理员自己
- 删除前需二次确认

---

## 前端 UI 规格

### 用户列表页面 (`/dashboard/users`)

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│  用户管理                            [+ 创建用户]         │
├─────────────────────────────────────────────────────────┤
│  搜索: [________]  角色: [全部▼]  状态: [全部▼]  [搜索] │
├─────────────────────────────────────────────────────────┤
│  ID │ 用户名     │ 角色   │ 状态   │ 创建时间    │ 操作  │
│  1  │ admin     │ 管理员 │ 启用   │ 2025-12-26 │ [编辑]│
│  2  │ demo_user │ 普通   │ 启用   │ 2025-12-26 │ [编辑]│
│                                                  [禁用]│
│                                                  [删除]│
├─────────────────────────────────────────────────────────┤
│  共 2 条         [上一页] 1 / 1 [下一页]                │
└─────────────────────────────────────────────────────────┘
```

**功能点**:
1. **搜索框**: 实时搜索用户名
2. **筛选器**: 按角色和状态筛选
3. **状态标识**: 使用颜色/图标区分启用/禁用
4. **操作按钮**: 
   - 编辑：打开编辑对话框
   - 禁用/启用：切换状态
   - 删除：弹出确认对话框

---

### 创建用户对话框

**表单字段**:
- 用户名（必填，唯一性校验）
- 角色（下拉选择：管理员/普通用户）
- 权限（多选框：读取/写入）

**创建成功**:
显示完整 API Key，并提示用户保存（仅此一次显示）

---

### 编辑用户对话框

**表单字段**:
- 用户名（只读，不可修改）
- 角色（下拉选择）
- 权限（多选框）

**重新生成 API Key**:
提供按钮，点击后生成新 Key 并显示

---

## 权限检查逻辑

### 后端依赖函数

创建统一的管理员权限检查函数：

```python
async def require_admin(user: dict = Depends(require_api_key)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user
```

所有用户管理接口使用此依赖：

```python
@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    ...
```

---

## 数据库操作

### 查询优化

- 用户列表添加索引：`user_name`, `role`, `status`
- 分页查询使用 LIMIT/OFFSET
- 搜索使用 LIKE 查询（考虑后续添加全文索引）

### 事务处理

- 创建用户：插入记录 + 生成 Key 需在同一事务
- 删除用户：如采用软删除，更新 deleted_at 字段

---

## 安全考虑

1. **API Key 保护**
   - 数据库存储 SHA256 哈希
   - 完整 Key 仅在创建时返回一次
   - 列表展示时只显示前缀（如：`vDiQ...GxY`）

2. **权限隔离**
   - 所有接口强制验证管理员权限
   - 禁止普通用户访问任何用户管理功能

3. **防护措施**
   - 禁止管理员删除或禁用自己
   - 删除操作需二次确认
   - 记录所有用户管理操作到审计日志

---

## 错误处理

| 错误码 | 场景 | 返回消息 |
|--------|------|----------|
| 400 | 用户名已存在 | "Username already exists" |
| 403 | 非管理员访问 | "Admin access required" |
| 403 | 删除自己 | "Cannot delete yourself" |
| 404 | 用户不存在 | "User not found" |
| 500 | 服务器错误 | "Internal server error" |

---

## 测试用例

### 单元测试

1. 创建用户 - 成功
2. 创建用户 - 用户名重复
3. 获取用户列表 - 分页
4. 获取用户列表 - 搜索
5. 更新用户角色 - 成功
6. 禁用用户 - 成功
7. 禁用自己 - 失败
8. 删除用户 - 成功
9. 删除自己 - 失败

### 集成测试

1. 管理员创建普通用户，验证新用户可登录
2. 管理员禁用用户，验证被禁用用户无法使用 API
3. 管理员删除用户，验证用户数据已删除

---

## 性能要求

- 用户列表查询响应时间 < 200ms
- 创建用户响应时间 < 500ms
- 支持至少 10,000 用户的系统规模
