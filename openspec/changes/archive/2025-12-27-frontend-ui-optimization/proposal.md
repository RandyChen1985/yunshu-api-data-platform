# 前端 UI 体验优化

## 1. 需求背景

当前前端系统存在多个用户体验问题，需要进行系统性优化以提升整体使用体验。

## 2. 核心问题

### 2.1 导航高亮问题（Critical）
- **问题描述**：左侧导航栏存在多个菜单项同时被高亮的问题
- **影响范围**：所有页面导航
- **原因分析**：路由匹配逻辑不精确，使用了 `active-class` 但同时还有 `:class` 绑定导致冲突

### 2.2 API Key 可见性问题（Critical）
- **问题描述**：API Key 只能在创建时查看一次，关闭后无法再次复制
- **影响范围**：用户管理、个人信息
- **用户需求**：
  - 在用户列表中可以复制 API Key
  - 在左下角个人信息弹窗中可以查看和复制自己的 API Key
  - 支持重复复制，而不是一次性展示

### 2.3 退出登录缺少确认（Medium）
- **问题描述**：点击退出登录直接执行，容易误操作
- **影响范围**：所有页面的退出登录按钮
- **用户需求**：增加确认对话框

### 2.4 用户信息展示不完整（Medium）
- **问题描述**：左下角用户头像区域只能显示基本信息，无法查看详情
- **影响范围**：所有页面的左下角用户区域
- **用户需求**：
  - 点击用户区域弹出个人信息面板
  - 显示完整用户信息（用户名、角色、API Key、创建时间等）
  - 可以复制 API Key
  - 可以修改个人备注（可选）

## 3. 其他发现的优化点

### 3.1 响应式优化（Medium）
- **移动端适配不完善**：部分组件在小屏幕下显示异常
- **表格横向滚动缺失**：表格内容过多时无法横向滚动

### 3.2 交互反馈优化（Low）
- **加载状态不统一**：部分操作缺少 loading 状态
- **操作反馈延迟**：某些按钮点击后无即时反馈
- **Toast 通知位置**：多个 Toast 叠加时可能遮挡内容

### 3.3 表单验证优化（Medium）
- **实时验证缺失**：表单字段缺少实时验证提示
- **错误提示不明确**：部分错误提示信息不够具体

### 3.4 可访问性优化（Low）
- **键盘导航支持**：对话框缺少 ESC 关闭支持
- **焦点管理**：打开对话框后焦点未自动定位到第一个输入框
- **屏幕阅读器支持**：缺少 aria 标签

### 3.5 性能优化（Low）
- **图标重复加载**：SVG 图标可以提取为组件复用
- **防抖节流优化**：搜索框已有防抖，其他输入框可以增加
- **列表虚拟滚动**：数据量大时考虑虚拟滚动

### 3.6 UI 一致性（Medium）
- **按钮样式不统一**：部分页面按钮样式不一致
- **间距规范化**：页面间距使用不一致（有的用 px，有的用 rem）
- **颜色规范化**：部分颜色值硬编码，未使用 Tailwind 配置

### 3.7 错误处理优化（Medium）
- **网络错误提示**：API 调用失败时提示信息不够友好
- **401/403 统一处理**：未登录或权限不足时未统一跳转
- **错误边界**：缺少全局错误捕获机制

### 3.8 数据持久化优化（Low）
- **筛选条件保存**：刷新页面后筛选条件丢失
- **分页状态保存**：返回页面时从第 1 页开始
- **表格列宽调整**：用户调整的列宽未保存

### 3.9 国际化准备（Future）
- **文本硬编码**：所有文本直接写在模板中
- **日期格式**：日期格式固定为中文格式
- **建议**：为未来国际化做准备，提取文本到配置

### 3.10 Dark Mode 支持（Future）
- **颜色方案**：当前仅支持浅色主题
- **用户偏好**：可以考虑支持深色模式

## 4. 优化优先级

### P0 - 必须修复（本期完成）
1. ✅ 左侧导航高亮问题修复
2. ✅ API Key 支持重复查看和复制
3. ✅ 退出登录增加确认
4. ✅ 用户信息详情弹窗

### P1 - 重要优化（本期完成）
5. ✅ 表格响应式优化（横向滚动）
6. ✅ 表单实时验证
7. ✅ 401/403 统一处理
8. ✅ 键盘导航支持（ESC 关闭对话框）
9. ✅ 焦点管理优化

### P2 - 体验优化（下期考虑）
10. UI 一致性规范化
11. Toast 通知位置优化
12. 错误提示友好化
13. 数据持久化（筛选、分页）

### P3 - 长期规划（未来）
14. 虚拟滚动
15. 国际化支持
16. Dark Mode

## 5. 技术方案

### 5.1 导航高亮修复

**问题根源**：
```vue
<!-- 当前代码 -->
<router-link 
  to="/dashboard" 
  active-class="bg-primary text-white shadow-md"
  :class="[
    route.path === '/dashboard' ? 'bg-primary text-white shadow-md' : '',
    ...
  ]"
>
```

**解决方案**：
- 移除 `active-class`，仅使用精确的路由匹配
- 使用 `route.path` 或 `route.name` 精确匹配
- 为 `/dashboard` 使用精确匹配（`exact`）

```vue
<!-- 修复后代码 -->
<router-link 
  to="/dashboard" 
  :class="[
    route.path === '/dashboard' || route.name === 'Overview' 
      ? 'bg-primary text-white shadow-md' 
      : 'text-gray-300 hover:bg-gray-800 hover:text-white',
    ...
  ]"
>
```

### 5.2 API Key 管理优化

**后端 API 增强**：
```python
# 新增接口：查看自己的 API Key
@router.get("/me/api-key")
async def get_my_api_key(user: dict = Depends(require_api_key)):
    """
    Get current user's API Key.
    Note: For security, return masked key with copy function
    """
    # 返回部分掩码 + 可查看完整 key 的方式
    pass

# 新增接口：管理员查看指定用户的 API Key
@router.get("/users/{user_id}/api-key")
async def get_user_api_key(
    user_id: int, 
    admin: dict = Depends(require_admin)
):
    """Admin only: Get specific user's API Key"""
    pass
```

**前端实现**：

1. **用户列表增加复制按钮**：
```vue
<!-- 在用户列表操作列增加 -->
<button @click="viewApiKey(user)" class="text-purple-600 hover:text-purple-900">
  查看密钥
</button>

<!-- API Key 显示弹窗 -->
<div v-if="showApiKeyDialog">
  <div class="flex items-center gap-2">
    <code class="flex-1">{{ displayedApiKey }}</code>
    <button @click="toggleApiKeyVisibility">
      {{ apiKeyVisible ? '隐藏' : '显示' }}
    </button>
    <button @click="copyApiKey">复制</button>
  </div>
</div>
```

2. **个人信息弹窗**：
```vue
<!-- 点击左下角用户区域 -->
<div @click="showProfileDialog = true" class="cursor-pointer hover:bg-gray-700">
  <!-- 用户头像和名称 -->
</div>

<!-- 个人信息弹窗 -->
<div v-if="showProfileDialog" class="fixed inset-0 bg-black bg-opacity-50">
  <div class="bg-white rounded-lg p-6">
    <h2>个人信息</h2>
    <div class="space-y-4">
      <div>
        <label>用户名</label>
        <p>{{ userInfo.user_name }}</p>
      </div>
      <div>
        <label>角色</label>
        <p>{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</p>
      </div>
      <div>
        <label>我的 API Key</label>
        <div class="flex items-center gap-2">
          <code>{{ apiKeyVisible ? myApiKey : '••••••••••••••••' }}</code>
          <button @click="toggleMyApiKeyVisibility">
            {{ apiKeyVisible ? '隐藏' : '显示' }}
          </button>
          <button @click="copyMyApiKey">复制</button>
        </div>
      </div>
      <div>
        <label>创建时间</label>
        <p>{{ formatDate(userInfo.created_at) }}</p>
      </div>
    </div>
  </div>
</div>
```

### 5.3 退出登录确认

```vue
<!-- Dashboard.vue -->
<button @click="showLogoutDialog = true">退出登录</button>

<!-- 确认对话框 -->
<div v-if="showLogoutDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 w-full max-w-md">
    <h2 class="text-xl font-bold mb-4">确认退出</h2>
    <p class="text-gray-700 mb-6">确定要退出登录吗？</p>
    <div class="flex justify-end gap-3">
      <button @click="showLogoutDialog = false" class="px-4 py-2 border border-gray-300 rounded-lg">
        取消
      </button>
      <button @click="confirmLogout" class="px-4 py-2 bg-red-600 text-white rounded-lg">
        确认退出
      </button>
    </div>
  </div>
</div>

<script setup lang="ts">
const showLogoutDialog = ref(false)

const confirmLogout = () => {
  localStorage.removeItem('api_key')
  localStorage.removeItem('user_info')
  router.push('/login')
  showLogoutDialog.value = false
}
</script>
```

### 5.4 响应式优化

```vue
<!-- 表格外层增加横向滚动 -->
<div class="overflow-x-auto">
  <table class="min-w-full">
    <!-- 表格内容 -->
  </table>
</div>

<!-- 移动端优化 -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- 统计卡片 -->
</div>
```

### 5.5 键盘导航支持

```vue
<!-- 对话框组件增加键盘事件 -->
<div 
  v-if="showDialog" 
  @keydown.esc="closeDialog"
  @click.self="closeDialog"
  tabindex="-1"
  class="fixed inset-0"
>
  <div class="dialog-content" @click.stop>
    <!-- 对话框内容 -->
  </div>
</div>

<script setup lang="ts">
import { watch, nextTick } from 'vue'

watch(showDialog, async (newVal) => {
  if (newVal) {
    await nextTick()
    // 自动聚焦第一个输入框
    const firstInput = document.querySelector('.dialog-content input')
    if (firstInput) {
      (firstInput as HTMLElement).focus()
    }
  }
})
</script>
```

### 5.6 全局错误处理

```typescript
// axios 拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('api_key')
      localStorage.removeItem('user_info')
      router.push('/login')
      return Promise.reject(new Error('未登录或登录已过期'))
    }
    
    if (error.response?.status === 403) {
      showToast('无权限访问此资源', 'error')
      return Promise.reject(new Error('无权限'))
    }
    
    // 网络错误
    if (!error.response) {
      showToast('网络连接失败，请检查网络设置', 'error')
      return Promise.reject(new Error('网络错误'))
    }
    
    return Promise.reject(error)
  }
)
```

## 6. 数据库变更

### 6.1 API Key 加密存储改造（方案 1 - 双向加密）

**当前问题**：
- 数据库存储的是 SHA256 哈希值，无法解密
- 用户忘记 API Key 后无法重新查看
- 不支持"查看密钥"功能

**技术方案**：使用 Fernet 对称加密

```sql
-- 修改 api_users 表结构
ALTER TABLE api_users 
DROP COLUMN api_key,
ADD COLUMN api_key_encrypted TEXT COMMENT '加密存储的API Key（Fernet加密，可解密）',
ADD COLUMN api_key_hash VARCHAR(64) NOT NULL UNIQUE COMMENT 'SHA256哈希（用于快速验证）';

-- 开发环境直接清空重建
TRUNCATE TABLE api_users;
```

**加密实现**：

```python
from cryptography.fernet import Fernet
import base64
import hashlib
import secrets
import os

class APIKeyManager:
    def __init__(self):
        # 从环境变量读取32字节密钥
        key = os.getenv("API_KEY_ENCRYPTION_SECRET")
        if not key:
            raise ValueError("API_KEY_ENCRYPTION_SECRET not configured")
        self.cipher = Fernet(key.encode())
    
    def generate_api_key(self) -> tuple[str, str, str]:
        """生成 API Key
        Returns:
            (plaintext_key, encrypted_key, hashed_key)
        """
        # 1. 生成随机 API Key
        api_key = secrets.token_urlsafe(32)
        
        # 2. 加密存储（可解密）
        encrypted = self.cipher.encrypt(api_key.encode())
        encrypted_b64 = base64.urlsafe_b64encode(encrypted).decode()
        
        # 3. 哈希值（快速验证）
        hashed = hashlib.sha256(api_key.encode()).hexdigest()
        
        return api_key, encrypted_b64, hashed
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密 API Key"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def hash_api_key(self, api_key: str) -> str:
        """计算哈希值"""
        return hashlib.sha256(api_key.encode()).hexdigest()
```

**环境变量配置**：

```bash
# .env 文件
API_KEY_ENCRYPTION_SECRET=your-fernet-key-here
```

生成密钥：
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
# 输出示例: b'your-fernet-key-here'
```

### 6.2 数据库迁移脚本

```python
# scripts/migrate_api_key_encryption.py
import asyncio
from app.core.database import get_db_connection
from app.services.auth_service import APIKeyManager

async def migrate():
    print("⚠️  开发环境 - 清空现有数据")
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # 1. 删除旧字段
            await cursor.execute("ALTER TABLE api_users DROP COLUMN api_key")
            
            # 2. 添加新字段
            await cursor.execute("""
                ALTER TABLE api_users 
                ADD COLUMN api_key_encrypted TEXT COMMENT '加密存储的API Key',
                ADD COLUMN api_key_hash VARCHAR(64) NOT NULL UNIQUE COMMENT 'SHA256哈希'
            """)
            
            # 3. 清空数据
            await cursor.execute("TRUNCATE TABLE api_users")
            
    print("✅ 迁移完成！请使用 init_db.py 重新创建管理员账号")

if __name__ == "__main__":
    asyncio.run(migrate())
```

### 6.3 更新初始化脚本

```python
# scripts/init_db.py（更新）
from app.services.auth_service import AuthService

# 创建管理员（自动使用新的加密机制）
api_key = await AuthService.generate_api_key("admin", role="admin", remark="系统管理员")
print(f"管理员 API Key: {api_key}")
print("请保存此 API Key，后续可通过前端查看")
```

## 7. 安全考虑

### 7.1 API Key 显示安全
- **默认隐藏**：API Key 默认以 `••••••••` 形式显示
- **点击显示**：需要用户主动点击"显示"按钮
- **自动隐藏**：离开页面或 30 秒后自动隐藏
- **复制记录**：记录 API Key 复制操作到审计日志

### 7.2 权限控制
- **普通用户**：只能查看自己的 API Key
- **管理员**：可以查看所有用户的 API Key
- **日志记录**：所有查看/复制操作记录到审计日志

## 8. 测试计划

### 8.1 功能测试
- [ ] 导航高亮：切换不同页面验证高亮状态
- [ ] API Key 复制：用户列表、个人信息多次复制验证
- [ ] 退出登录：点击退出、确认、取消流程
- [ ] 个人信息：弹窗显示、API Key 显示/隐藏、复制
- [ ] 键盘导航：ESC 关闭对话框
- [ ] 响应式：不同屏幕尺寸测试

### 8.2 兼容性测试
- [ ] Chrome 最新版
- [ ] Safari 最新版
- [ ] Firefox 最新版
- [ ] Edge 最新版
- [ ] 移动端 Safari/Chrome

### 8.3 性能测试
- [ ] 大数据量列表渲染
- [ ] 多个 Toast 同时显示
- [ ] 频繁切换页面

## 9. 实施步骤

### Phase 1: 核心问题修复（1-2天）
1. 修复导航高亮问题
2. 退出登录确认对话框
3. 键盘导航支持（ESC 关闭）

### Phase 2: API Key 功能增强（2-3天）
1. 后端 API 开发（查看 API Key 接口）
2. 用户列表增加查看密钥功能
3. 个人信息弹窗开发
4. 审计日志记录

### Phase 3: 体验优化（1-2天）
1. 响应式优化
2. 表单验证优化
3. 全局错误处理
4. UI 一致性调整

### Phase 4: 测试和修复（1天）
1. 功能测试
2. 兼容性测试
3. Bug 修复

**总计：5-8 个工作日**

## 10. 成功标准

- ✅ 导航栏不再出现多个高亮项
- ✅ API Key 可以随时查看和复制
- ✅ 退出登录有确认提示，减少误操作
- ✅ 个人信息弹窗功能完善
- ✅ 所有对话框支持 ESC 关闭
- ✅ 移动端显示正常无遮挡
- ✅ 所有功能测试通过
- ✅ 用户满意度提升
