# 提案：重构 ClickHouse 适配器与前端工程化配置优化

## 1. 背景与问题
当前项目在后端数据适配层和前端工程配置上存在两处明显的优化空间：

1.  **后端代码冗余**：`app/services/data_adapter/clickhouse.py` 中的 `execute` 方法使用了大量的 `if/elif` 硬编码来处理不同资源（Resource）的 SQL 查询和结果映射。每新增一个资源类型，都需要修改核心逻辑，违反了开闭原则（Open-Closed Principle），且容易引入 Bug。
2.  **前端路径引用繁琐**：前端 Vue 项目未配置路径别名（Path Alias），导致文件引用大量出现 `../../` 形式的相对路径，降低了代码可读性和可维护性，且在文件移动时极易出错。

## 2. 目标
1.  **后端重构**：将 `ClickHouseAdapter` 改造为配置驱动模式。通过定义资源到数据库字段的映射配置（Mapping Schema），让 `execute` 方法通用化，不再依赖硬编码判断。
2.  **前端优化**：配置 Vite 和 TypeScript 支持 `@` 别名指向 `src` 目录，统一模块导入规范。

## 3. 实施方案

### 3.1 后端重构 (Python)
- **定义映射配置**：在 `ClickHouseAdapter` 类中提取 `RESOURCE_MAPPING` 字典，包含每个资源对应的：
    - `table_name`: 目标表名
    - `fields`: 字段名映射（API 字段名 -> DB 字段名，或直接使用列表如果一致）
    - `defaults`: 默认排序字段等
- **重构 execute 方法**：
    - 移除所有针对具体 `resource` 的 `if/elif` 分支。
    - 根据 `RESOURCE_MAPPING` 动态构建 `SELECT` 语句。
    - 根据 `RESOURCE_MAPPING` 动态组装返回的 JSON 对象。

### 3.2 前端优化 (Vue/Vite)
- **修改 vite.config.ts**：引入 `path` 模块，配置 `resolve.alias` 将 `@` 指向 `./src`。
- **修改 tsconfig.json**：在 `compilerOptions` 中添加 `paths` 配置，确保 TypeScript 能够识别 `@/*` 路径。
- **验证**：修改部分组件的引用路径，验证配置生效。

## 4. 预期收益
- **可维护性提升**：新增数据资源只需在配置中添加一行定义，无需修改核心逻辑代码。
- **开发体验改善**：前端引用路径更简洁直观，减少路径错误。
- **代码质量**：消除重复代码，降低圈复杂度。
