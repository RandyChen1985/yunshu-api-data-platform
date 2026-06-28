# 云枢・智维・AI 平台 - API服务化系统设计文档

## 1. 文档信息

- **文档名称**：API服务化系统设计文档
- **系统名称**：云枢・数据服务平台（Yunshu Data API Platform）
- **所属项目**：云枢・智维・AI
- **版本**：v1.0
- **日期**：2025-12-25
- **作者**：系统架构团队

## 2. 系统概述

### 2.1 系统目标

构建一个高可用、高性能、可扩展的 API 服务化平台，作为统一的 Data API 层，对上为云枢 Web、AI Agent 及其他业务系统提供标准化数据访问接口，对下屏蔽 ClickHouse / HBase / MySQL 等多种数据源的差异。

### 2.2 系统范围

- API服务层：提供标准化API接口
- 认证授权层：统一认证授权机制
- 数据访问层：与ClickHouse、HBase等数据源交互
- 缓存层：提升查询性能
- 监控告警层：系统监控和告警

## 3. 架构设计

### 3.1 总体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   客户端应用     │    │   API网关       │    │   API服务       │
│                 │───▶│                 │───▶│                 │
│  (业务方系统)    │    │  (认证/限流)    │    │  (业务逻辑)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   缓存层        │    │   数据访问层     │    │   数据存储      │
│                 │───▶│                 │───▶│                 │
│  (Redis)        │    │  (数据源适配)   │    │  (ClickHouse,  │
└─────────────────┘    └─────────────────┘    │   HBase, etc.)  │
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   监控告警      │    │   日志服务       │    │   配置中心      │
│                 │    │                 │    │                 │
│  (Prometheus,  │    │  (ELK)          │    │  (Consul)       │
│   Grafana)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.2 架构分层

#### 3.2.1 表现层（Presentation Layer）

- API网关：可选的统一入口（如已存在网关可复用）；MVP 关键能力默认在服务内部实现
- API服务：处理业务逻辑，数据转换

#### 3.2.2 业务逻辑层（Business Logic Layer）

- 服务编排：协调多个数据源
- 业务规则：数据校验、权限检查
- 缓存管理：数据缓存、查询优化

#### 3.2.3 数据访问层（Data Access Layer）

- 数据源适配器：适配不同数据源
- 查询优化器：SQL优化、索引选择
- 连接池管理：数据库连接管理

#### 3.2.4 数据存储层（Data Storage Layer）

- ClickHouse：时序数据存储
- HBase：实时数据存储
- Redis：缓存数据存储

## 4. 技术选型

### 4.1 后端技术栈

- **API框架**：FastAPI（Python 3.10+）
- **异步处理**：asyncio + uvicorn
- **数据库驱动**：
  - ClickHouse：clickhouse-driver
  - HBase：happybase
  - MySQL：aiomysql 或 SQLAlchemy（根据实际选型）
  - Redis：redis-py

### 4.2 中间件

- **API网关**：Kong或自研网关
- **缓存**：Redis 7.0+
- **消息队列**：Kafka（用于异步处理）
- **监控**：Prometheus + Grafana

### 4.3 容器化与部署

- **容器化**：Docker
- **编排**：Kubernetes
- **CI/CD**：Jenkins/GitLab CI

## 5. 详细设计

### 5.1 API服务设计

#### 5.1.1 服务结构

```
api_service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/                 # API版本
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/      # API端点
│   │   │   │   ├── data.py     # 数据API
│   │   │   │   ├── auth.py     # 认证API
│   │   │   │   └── monitor.py  # 监控API
│   │   │   └── schemas/        # 数据模型
│   │   │       ├── base.py     # 基础模型
│   │   │       ├── data.py     # 数据模型
│   │   │       └── auth.py     # 认证模型
│   ├── core/                   # 核心功能
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全认证
│   │   ├── cache.py            # 缓存管理
│   │   └── exceptions.py       # 异常处理
│   ├── services/               # 业务服务
│   │   ├── data_service.py     # 数据服务
│   │   ├── auth_service.py     # 认证服务
│   │   └── cache_service.py    # 缓存服务
│   └── utils/                  # 工具类
│       ├── database.py         # 数据库工具
│       ├── validators.py       # 验证器
│       └── helpers.py          # 辅助函数
```

#### 5.1.2 API路由设计

```
# 资源化接口（MVP 优先，首批表结构来源：architech/db-schemal/CLICKHOUSE_TABLES.md）
GET  /api/v1/resources/donghuan/real-metrics   # ck_fact_donghuan_real_metric_hbase 动环实时指标
GET  /api/v1/resources/donghuan/events         # ck_fact_donghuan_event_detail_hbase 动环事件详情
GET  /api/v1/resources/yunshu/rooms            # ck_fact_yunshu_resroom_hbase 机房
GET  /api/v1/resources/yunshu/racks            # ck_fact_yunshu_resjj_hbase 机架
GET  /api/v1/resources/yunshu/device-points    # ck_fact_yunshu_devicepoint_hbase 点位

# 通用查询接口（与资源化接口并行，独立 path，避免耦合）
POST /api/v1/query/logical                      # 统一 LogicalQuery 查询入口（按数据源能力路由）

# API Key 管理接口（服务内置管理能力）
POST /api/v1/keys                               # 创建 API Key
GET  /api/v1/keys                               # 查询 API Key 列表
POST /api/v1/keys/{key_id}/rotate               # 轮换 API Key
POST /api/v1/keys/{key_id}/disable              # 禁用 API Key
```

##### 5.1.2.1 首批资源化接口清单（基于 ClickHouse 表）

| 接口名称           | HTTP 方法 | 路径                                        | 数据源表                                 | 主要过滤条件（MVP）                                             | 默认排序           |
|--------------------|-----------|---------------------------------------------|-------------------------------------------|------------------------------------------------------------------|--------------------|
| 动环实时指标列表   | GET       | `/api/v1/resources/donghuan/real-metrics`  | `ck_fact_donghuan_real_metric_hbase`      | `c_datacenter_id`、`resource_id`、`metric_name`、`start_time/end_time` | `metric_time desc` |
| 动环事件列表       | GET       | `/api/v1/resources/donghuan/events`        | `ck_fact_donghuan_event_detail_hbase`     | `c_datacenter_id`、`event_level`、`event_type`、`resource_id`、`start_time/end_time` | `event_time desc`  |
| 机房列表           | GET       | `/api/v1/resources/yunshu/rooms`           | `ck_fact_yunshu_resroom_hbase`            | `jfbm`（机房编码）、`jfmc`（机房名称）、`ywzx`（业务中心）、`gsbs` | `rowkey asc`       |
| 机架列表           | GET       | `/api/v1/resources/yunshu/racks`           | `ck_fact_yunshu_resjj_hbase`              | `jfmc`（机房）、`jjbm`（机架编码）、`jjzt`（机架状态）、`kh/khmc` | `rowkey asc`       |
| 设备点位列表       | GET       | `/api/v1/resources/yunshu/device-points`   | `ck_fact_yunshu_devicepoint_hbase`        | `jf`（机房）、`jjbm`（机架编码）、`dwid`（点位 ID）、`dwlx`（点位类型） | `rowkey asc`       |

> 说明：
> - 上表仅列出首批 MVP 范围内需要重点支持的过滤条件，其余字段可作为附加查询条件在实现阶段按需扩展。
> - 响应字段初期可一一映射表字段，后续根据前端 / AI 平台需求收敛成更友好的字段集与命名规范。


##### 5.1.2.1 首批资源化接口清单（基于 ClickHouse 表）

| 接口名称           | HTTP 方法 | 路径                                        | 数据源表                                 | 主要过滤条件（MVP）                                             | 默认排序           |
|--------------------|-----------|---------------------------------------------|-------------------------------------------|------------------------------------------------------------------|--------------------|
| 动环实时指标列表   | GET       | `/api/v1/resources/donghuan/real-metrics`  | `ck_fact_donghuan_real_metric_hbase`      | `c_datacenter_id`、`resource_id`、`metric_name`、`start_time/end_time` | `metric_time desc` |
| 动环事件列表       | GET       | `/api/v1/resources/donghuan/events`        | `ck_fact_donghuan_event_detail_hbase`     | `c_datacenter_id`、`event_level`、`event_type`、`resource_id`、`start_time/end_time` | `event_time desc`  |
| 机房列表           | GET       | `/api/v1/resources/yunshu/rooms`           | `ck_fact_yunshu_resroom_hbase`            | `jfbm`（机房编码）、`jfmc`（机房名称）、`ywzx`（业务中心）、`gsbs` | `rowkey asc`       |
| 机架列表           | GET       | `/api/v1/resources/yunshu/racks`           | `ck_fact_yunshu_resjj_hbase`              | `jfmc`（机房）、`jjbm`（机架编码）、`jjzt`（机架状态）、`kh/khmc` | `rowkey asc`       |
| 设备点位列表       | GET       | `/api/v1/resources/yunshu/device-points`   | `ck_fact_yunshu_devicepoint_hbase`        | `jf`（机房）、`jjbm`（机架编码）、`dwid`（点位 ID）、`dwlx`（点位类型） | `rowkey asc`       |

> 说明：
> - 上表仅列出首批 MVP 范围内需要重点支持的过滤条件，其余字段可作为附加查询条件在实现阶段按需扩展。
> - 响应字段初期可一一映射表字段，后续根据前端 / AI 平台需求收敛成更友好的字段集与命名规范。


### 5.2 认证授权设计

#### 5.2.1 认证流程

```
1. 客户端 -> API服务：携带 `X-API-Key` 调用数据接口
2. API服务：校验 API Key（建议存储哈希，避免明文落库）
3. API服务：记录审计日志/限流计数后执行业务查询
```

#### 5.2.2 权限控制

- MVP 阶段统一以 API Key 为准入条件
- 支持上游透传 `role` / `scopes`（例如通过 `X-Scopes`），MVP 阶段仅记录与透传，不做强校验与过滤
- 对敏感字段支持脱敏或拒绝访问策略（按角色配置），可作为后续增强

### 5.3 数据访问设计

#### 5.3.1 数据源适配器

```python
class DataSourceAdapter:
    """数据源适配抽象，屏蔽 ClickHouse / HBase / MySQL 等差异"""

    def type(self) -> str:
        """返回数据源类型标识，如 'clickhouse' / 'hbase' / 'mysql'"""
        raise NotImplementedError

    def capabilities(self) -> set:
        """返回该数据源支持的能力集合，如 {'point_query', 'range_query', 'aggregate'}"""
        raise NotImplementedError

    async def execute(self, logical_query: "LogicalQuery") -> "ResultSet":
        """执行标准化逻辑查询（维度、指标、过滤、聚合等），返回统一结果集结构"""
        raise NotImplementedError


class ClickHouseAdapter(DataSourceAdapter):
    """ClickHouse 数据源适配器示例"""
    ...


class HBaseAdapter(DataSourceAdapter):
    """HBase 数据源适配器示例"""
    ...
```

#### 5.3.2 查询优化

- SQL预编译
- 查询缓存
- 索引优化
- 分区策略

#### 5.3.3 SQL 执行策略（策略 A）

- 所有由上层系统触发的查询，推荐最终由 `QueryEngine + DataSourceAdapter` 执行，避免直接拼接和执行任意 SQL 字符串
- 执行前需做以下安全检查：
  - 限制时间范围：默认仅允许最近 7 天（特殊 API 可配置放宽），超过范围需显式配置白名单
  - 限制返回行数：单次查询返回记录数上限（如 10,000 行），超出要求前端分页或缩小范围
  - 限制可访问的库表与字段：仅允许访问白名单内的表/视图与字段
  - 限制执行时间：超时自动取消（例如 5 秒），并记录慢查询
- **说明（MVP）**：安全红线与白名单策略可在后续版本逐步强化，本阶段以接口可用与链路打通为主
- 支持上游透传 `role` / `scopes`（例如通过 `X-Scopes`）；MVP 阶段仅记录与透传，不做强校验与过滤
- 执行完成后记录审计信息（用户、角色、数据范围、耗时、影响行数等），供后续追踪

### 5.4 缓存设计

#### 5.4.1 缓存策略

- **热点数据缓存**：频繁访问的数据
- **查询结果缓存**：复杂查询结果
- **配置缓存**：系统配置信息

#### 5.4.2 缓存层级

```
L1: 应用内缓存（内存）
L2: Redis缓存（分布式）
L3: 数据库缓存（ClickHouse内置）
```

### 5.5 统一响应模型

- API 服务对外返回的所有 HTTP 响应均使用统一 Envelope 结构：`{ code, message, data, timestamp, trace_id }`
- `code` 仅表示业务状态（200 为成功），与 HTTP Status 解耦；错误场景也会返回该结构
- `timestamp` 由服务端生成，`trace_id` 在网关或入口处生成并贯穿全链路，方便排查 AI 调用链路问题
- `data` 字段承载分页数据、统计结果或 ChatBI 结果结构，保持向前兼容（未来扩展字段时不影响现有客户端)

#### 5.5.1 分页响应规范（统一）

- 对于分页类接口，统一使用：
  - `data.items`
  - `data.total`
  - `data.page`
  - `data.size`
  - `data.pages`

## 6. 数据库设计

### 6.1 API服务数据库表

#### 6.1.1 API用户表 (api_users)

```sql
CREATE TABLE api_users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(64) NOT NULL UNIQUE,
    api_key VARCHAR(128) NOT NULL UNIQUE,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1
);
```

#### 6.1.2 API访问日志 (基于文件/队列的异步日志)

> **注意**：原 MySQL `api_access_logs` 表设计不适合高 QPS 场景。

- **推荐方案**: 应用层使用 `logging` 模块异步写入本地文件（JSON 格式），通过 Filebeat/Vector 采集至 ClickHouse 或 Elasticsearch。
- **ClickHouse 表结构示例** (用于日志分析，非事务型写入):

```sql
CREATE TABLE api_access_logs_local (
    trace_id String,
    user_id UInt64,
    api_endpoint String,
    request_params String, -- JSON string
    response_time_ms UInt32,
    status_code UInt16,
    timestamp DateTime64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, api_endpoint);
```

#### 6.1.3 API限流策略 (Redis)

> **注意**：原 MySQL `api_rate_limits` 表设计在高并发下会成为瓶颈，改为使用 Redis 进行实时限流。

- **Key 设计**: `rate_limit:{api_key}:{minute_timestamp}`
- **Value**: 请求计数 (Integer)
- **TTL**: 60秒
- **算法**: 固定窗口计数器 (Fixed Window) 或 滑动窗口 (Sliding Window via Lua)

```python
# Pseudo-code using redis-py
key = f"rate_limit:{api_key}:{current_minute}"
current = redis.incr(key)
if current == 1:
    redis.expire(key, 60)
if current > limit:
    raise TooManyRequests()
```

### 6.2 ClickHouse数据表（现有）

#### 6.2.1 温度数据表 (temperature_data)

```sql
CREATE TABLE temperature_data (
    id UInt64,
    device_id String,
    room_id String,
    rack_id String,
    temperature Float32,
    humidity Float32,
    timestamp DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (device_id, timestamp);
```

## 7. 安全设计

### 7.1 认证与鉴权

- MVP 阶段统一使用 **API Key** 进行服务端准入控制：
  - 客户端在请求头中携带 `X-API-Key: <api_key>`。
  - 服务端仅存储 API Key 的哈希值（例如 `SHA256(api_key)`），避免明文落库。
  - 通过 `api_users` 表管理 API Key 的生命周期（创建 / 禁用 / 轮换 / 权限）。
- 预留上游透传数据范围上下文：
  - 使用 `X-Scopes` 请求头透传 `role`、`regions`、`rooms` 等信息。
  - **MVP 阶段仅记录与透传，不做强校验与过滤**，后续版本再落地资源层权限控制。
- 所有对外接口必须校验 API Key：
  - 未携带或校验失败时返回 401（Envelope 中 `code` 置为统一业务错误码，例如 `3001`）。

> 说明：JWT / OAuth2 等更复杂的认证方案不在本次 MVP 范围内，可在后续版本引入，并在文档中补充相应子章节。

### 7.2 数据安全

- 所有外部调用通过 HTTPS 或内部零信任通道，避免明文传输。
- 数据库连接尽可能开启 TLS（ClickHouse / MySQL 等支持时）。
- 支持按字段脱敏策略（手机号、身份证等敏感字段），MVP 阶段至少在日志输出中做脱敏处理，并预留按角色脱敏策略能力。

### 7.3 访问控制与防护

- IP 白名单 / 安全组控制由基础设施层（K8s Ingress / 防火墙）保障。
- 统一限流策略（基于 API Key 和接口维度），在 API 层或网关层实现：
  - 全局 QPS 上限；
  - 单 Key QPS / 并发数上限。
- 基础 SQL 防注入与安全边界：
  - 所有查询通过参数绑定或 `QueryEngine + DataSourceAdapter` 构造，不允许拼接任意 SQL 字符串。
  - 仅允许访问白名单表 / 字段，限制最大时间范围 / 返回行数，并记录慢查询。

## 8. 性能设计

### 8.1 性能优化策略

- 数据库索引优化
- 查询缓存机制
- 连接池管理
- 异步处理

### 8.2 性能指标

- API响应时间：P95 < 1秒
- 并发处理能力：1000+ QPS
- 系统可用性：99.9%

## 9. 监控设计

### 9.1 监控指标

- API请求量和响应时间
- 错误率和成功率
- 数据库连接状态
- 系统资源使用率

### 9.2 告警机制

- API响应时间告警
- 错误率告警
- 系统资源告警
- 数据库连接告警

## 10. 部署设计

### 10.1 部署架构

- 容器化部署（Docker）
- 容器编排（Kubernetes）
- 负载均衡
- 自动扩缩容

### 10.2 部署流程

1. 代码构建
2. 容器镜像制作
3. 镜像推送
4. 部署到K8s集群
5. 服务注册与发现

## 11. 扩展性设计

### 11.1 水平扩展

- 无状态服务设计
- 分布式缓存
- 数据库分片

### 11.2 垂直扩展

- 服务模块化
- 配置可调整
- 资源动态分配

## 12. 配置管理

### 12.1 配置项

- 数据库连接配置
- 缓存配置
- 限流配置
- 监控配置

### 12.2 配置管理

- 配置中心管理
- 配置热更新
- 环境隔离配置

### 12.3 环境变量约定（外部化配置）

MVP 阶段所有外部依赖（ClickHouse / MySQL / Redis 等）的连接信息一律通过环境变量注入，由配置模块统一读取，不在代码中写死任何地址或凭证。建议按以下分组规范：

- **通用应用配置**
  - `API_SERVICE_ENV`：环境标识（`dev` / `test` / `prod`）
  - `API_SERVICE_PORT`：服务端口，默认 `8000`
  - `API_SERVICE_LOG_LEVEL`：日志级别（`INFO` / `DEBUG` / `WARN`）
  - `API_SERVICE_TRACE_ID_HEADER`：链路 ID 请求头名称（默认 `X-Trace-Id`）

- **ClickHouse 配置**
  - `CLICKHOUSE_HOST`
  - `CLICKHOUSE_PORT`
  - `CLICKHOUSE_DB`
  - `CLICKHOUSE_USER`
  - `CLICKHOUSE_PASSWORD`
  - （可选）`CLICKHOUSE_READ_TIMEOUT`、`CLICKHOUSE_POOL_SIZE`

- **MySQL 配置**（承载 `api_users`、访问日志等元数据）
  - `MYSQL_HOST`
  - `MYSQL_PORT`
  - `MYSQL_DB`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - （可选）`MYSQL_POOL_SIZE`

- **Redis 配置**（缓存 & 限流，**必需**）
  - `REDIS_HOST`
  - `REDIS_PORT`
  - `REDIS_DB`
  - （可选）`REDIS_PASSWORD`
  - `REDIS_ENABLE`：默认为 `true`，如需关闭限流与缓存可设为 `false`（不推荐生产环境关闭）

- **安全与限流相关**
  - `API_SERVICE_API_KEY_HASH_ALGORITHM`：API Key 哈希算法（如 `sha256`）
  - `API_SERVICE_RATE_LIMIT_ENABLED`：是否开启限流（`true/false`）

> 说明：具体取值（主机、端口、账号等）由部署环境提供，应用只依赖变量名约定；如后续引入 MQ、对象存储等组件，可按相同命名规范扩展环境变量。

## 13. 测试策略

### 13.1 单元测试

- 服务层单元测试
- 数据访问层测试
- 工具类测试

### 13.2 集成测试

- API接口测试
- 数据库集成测试
- 缓存集成测试

### 13.3 性能测试

- 负载测试
- 压力测试
- 并发测试
