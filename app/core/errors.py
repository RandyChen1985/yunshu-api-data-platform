from enum import IntEnum

class ErrorCode(IntEnum):
    """
    标准化业务错误码。
    格式说明:
    - 200: 成功响应
    - 400x: 请求错误（客户端侧）
    - 401x: 认证错误
    - 403x: 权限错误
    - 500x: 服务器错误
    """
    SUCCESS = 200  # 成功响应
    
    # 400x: 请求错误
    BAD_REQUEST = 400  # 错误的请求
    INVALID_PARAMETER = 4001  # 无效的参数
    RESOURCE_NOT_FOUND = 4004  # 资源未找到
    RESOURCE_DISABLED = 4005  # 资源已禁用
    
    # 401x: 认证错误
    UNAUTHORIZED = 401  # 未授权
    API_KEY_MISSING = 4011  # API密钥缺失
    API_KEY_INVALID = 4012  # API密钥无效
    TOKEN_EXPIRED = 4013  # Token已过期
    
    # 403x: 权限错误
    FORBIDDEN = 403  # 禁止访问
    ACCESS_DENIED = 4031  # 访问被拒绝
    ADMIN_REQUIRED = 4032  # 需要管理员权限
    
    # 429x: 速率限制
    TOO_MANY_REQUESTS = 429  # 请求过于频繁
    
    # 500x: 服务器错误
    INTERNAL_SERVER_ERROR = 500  # 服务器内部错误
    DATABASE_ERROR = 5001  # 数据库错误
    CLICKHOUSE_ERROR = 5002  # ClickHouse错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用
    DATABASE_CONNECTION_FAILED = 5031  # 数据库连接失败

# 错误码中文描述映射
ERROR_CODE_DESC = {
    ErrorCode.SUCCESS: "成功响应",
    ErrorCode.BAD_REQUEST: "错误的请求",
    ErrorCode.INVALID_PARAMETER: "无效的参数",
    ErrorCode.RESOURCE_NOT_FOUND: "资源未找到",
    ErrorCode.RESOURCE_DISABLED: "资源已禁用",
    ErrorCode.UNAUTHORIZED: "未授权",
    ErrorCode.API_KEY_MISSING: "API密钥缺失",
    ErrorCode.API_KEY_INVALID: "API密钥无效",
    ErrorCode.TOKEN_EXPIRED: "Token已过期",
    ErrorCode.FORBIDDEN: "禁止访问",
    ErrorCode.ACCESS_DENIED: "访问被拒绝",
    ErrorCode.ADMIN_REQUIRED: "需要管理员权限",
    ErrorCode.TOO_MANY_REQUESTS: "请求过于频繁",
    ErrorCode.INTERNAL_SERVER_ERROR: "服务器内部错误",
    ErrorCode.DATABASE_ERROR: "数据库错误",
    ErrorCode.CLICKHOUSE_ERROR: "ClickHouse错误",
    ErrorCode.SERVICE_UNAVAILABLE: "服务不可用",
    ErrorCode.DATABASE_CONNECTION_FAILED: "数据库连接失败",
}
