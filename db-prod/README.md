# 数据库初始化与迁移指南

本目录包含生产环境数据库的初始化脚本和版本化 SQL 迁移文件。导入脚本在目标库不存在时会自动以 `utf8mb4` 字符集创建数据库。

## 📁 文件说明

| 文件名/目录 | 用途 |
| :--- | :--- |
| `V{N}-description.sql` | 版本化的 SQL 迁移脚本（按名称排序依次执行）。 |
| `INIT-USER-ADMIN.sql` | **初始化管理员账号**。包含默认 admin 用户的 SQL 插入语句及其 API Key 备注。 |
| `apply-sql.sh` | 基于 Python (aiomysql) 的交互式数据库部署脚本。 |
| `apply-sql-native.sh` | 免 Python 依赖的原生 Shell 交互式导入脚本（仅依赖 `mysql` CLI 客户端）。 |
| `apply_sql.py` | 实际执行 SQL 导入的核心 Python 脚本（由 `apply-sql.sh` 调用）。 |

## 🚀 数据库初始化与迁移

### 选项 A：Python 脚本（推荐）

```bash
# 在项目根目录
source venv/bin/activate   # 如已创建虚拟环境
pip install -r requirements.txt
./db-prod/apply-sql.sh
```

### 选项 B：免 Python 依赖

```bash
./db-prod/apply-sql-native.sh
```

脚本会交互式提示输入 Host、Port、User、Password、目标数据库名，输入 **`YES`** 二次确认后执行。

> **幂等性说明**：脚本具备幂等性。若表、列、索引已存在，或数据已插入，会自动跳过对应错误（1007 / 1050 / 1060 / 1061 / 1062 / 1091），可安全重复执行升级迁移。

### 单独执行某个文件

```bash
./db-prod/apply-sql.sh db-prod/INIT-USER-ADMIN.sql
```

### 如何添加新的数据库变更

1. 在 `db-prod/` 目录下创建 `V{N}-{描述}.sql`。
2. 优先使用 `CREATE TABLE IF NOT EXISTS`、`ALTER TABLE ... ADD COLUMN`（配合幂等跳过）等写法。
3. 运行 `./db-prod/apply-sql.sh` 应用变更。

## 🔐 管理员账号

`INIT-USER-ADMIN.sql` 中定义的默认管理员信息：
- **用户名**: `admin`
- **API Key**: `YZnxdJLZ0Hwf7IpHXHkYDZYI-CUsTafRjGeANklakuA`

首次部署时，`apply-sql.sh` 会在迁移完成后询问是否导入该账号。

## ⚠️ 注意事项

- SQL 文件中的 `CREATE DATABASE` / `USE` 语句会被自动跳过，实际连接以你输入的目标库为准。
- `V0` 等早期脚本含 `DROP TABLE`，**请勿在已有生产数据的环境上重复执行 V0**；后续 `V1+` 增量迁移可安全重复执行。
- 看到 `Skipping (already applied)` 是正常现象，表示该步骤已应用过。

## ❓ 常见问题

### Q1: 运行脚本时报错 `ModuleNotFoundError: No module named 'aiomysql'`
**原因**：未在 Python 虚拟环境中安装依赖。  
**解决**：执行 `pip install -r requirements.txt`；或改用 `./db-prod/apply-sql-native.sh`（仅需 `mysql` 客户端）。

### Q2: 提示 `Skipping (already applied): ...`
**原因**：迁移脚本具备幂等性，表/列/索引已存在时会自动跳过。  
**解决**：这是正常现象，无需处理。

### Q3: 如何自定义创建新的管理员？
可运行 `python3 scripts/create_admin_user.py` 生成新的管理员账号与 API Key。

⚠️ **安全提示**：在任何生产环境执行数据库结构变更前，请务必提前备份数据。
