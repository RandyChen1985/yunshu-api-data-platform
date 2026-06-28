from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from app.services.meta_service import MetaService
from app.api.v1.schemas.data import COMMON_ERROR_RESPONSES
import logging

# OpenAPI Tags
tags_metadata = [
    {
        "name": "通用查询",
        "description": "通用逻辑查询接口，支持灵活的条件筛选、分页和排序。",
    },
    {
        "name": "智服平台",
        "description": "动环系统实时指标和事件查询，以及智服平台资源（机房、机架、设备点位）。",
    },
]

async def custom_openapi(app: FastAPI):
    """
    Generate Custom OpenAPI Schema.
    Injects dynamic resources and applies global security schemes.
    """
    # Remove caching to support dynamic resources
    # if app.openapi_schema:
    #     return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    
    # 注入通用错误响应组件，供动态生成的 API 使用 $ref 引用
    if "responses" not in openapi_schema["components"]:
        openapi_schema["components"]["responses"] = {}
        
    for status, info in COMMON_ERROR_RESPONSES.items():
        openapi_schema["components"]["responses"][str(status)] = {
            "description": info["description"],
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "X-API-Key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API 密钥认证，在请求头中携带 `X-API-Key: your_api_key_here`"
        }
    }
    
    # Fetch Dynamic Resources from MetaService
    try:
        dynamic_resources = await MetaService.list_resources()
        for res in dynamic_resources:
            path_key = f"/api/v1/resources/{res.resource_key}"
            
            # 1. Define Resource Row Schema
            row_schema_name = f"ResourceRow_{res.resource_key}"
            properties = {}
            for field in res.fields_config:
                field_name = field.name
                field_label = field.label
                field_type = field.type.lower()
                
                # Map ClickHouse types to JSON types
                json_type = "string"
                if "int" in field_type or "uint" in field_type:
                    json_type = "integer"
                elif "float" in field_type or "decimal" in field_type:
                    json_type = "number"
                elif "bool" in field_type:
                    json_type = "boolean"
                
                properties[field_name] = {
                    "type": json_type,
                    "description": field_label,
                    "example": "..."
                }
            
            openapi_schema["components"]["schemas"][row_schema_name] = {
                "type": "object",
                "properties": properties,
                "description": f"{res.resource_name} 数据行模型"
            }
            
            # 2. Define Page Schema for this resource
            page_schema_name = f"DataPage_{res.resource_key}"
            openapi_schema["components"]["schemas"][page_schema_name] = {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": f"#/components/schemas/{row_schema_name}"}
                    },
                    "total": {"type": "integer", "example": 100},
                    "page": {"type": "integer", "example": 1},
                    "size": {"type": "integer", "example": 20},
                    "pages": {"type": "integer", "example": 5}
                },
                "required": ["items", "total", "page", "size", "pages"]
            }
            
            # 3. Define Response Schema for this resource
            resp_schema_name = f"Response_{res.resource_key}"
            openapi_schema["components"]["schemas"][resp_schema_name] = {
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200, "description": "业务状态码"},
                    "message": {"type": "string", "example": "success"},
                    "data": {"$ref": f"#/components/schemas/{page_schema_name}"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "trace_id": {"type": "string"}
                },
                "required": ["code", "message", "data"]
            }

            # 4. Construct Parameters
            parameters = [
                {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                {"name": "size", "in": "query", "schema": {"type": "integer", "default": 20}},
                {"name": "sort_by", "in": "query", "schema": {"type": "string"}},
                {"name": "sort_order", "in": "query", "schema": {"type": "string", "default": "DESC", "enum": ["ASC", "DESC"]}},
            ]
            
            # Add Allowed Filters with Labels
            for filt in res.allowed_filters:
                filter_name = filt.name
                # Find label in fields_config
                label = filt.label
                for f in res.fields_config:
                    if f.name == filter_name:
                        label = f.label
                        break
                        
                parameters.append({
                    "name": filter_name,
                    "in": "query",
                    "schema": {"type": "string"},
                    "description": f"过滤: {label}"
                })
                
            # 5. Construct Operation Object
            operation = {
                "tags": [res.resource_group],
                "summary": f"查询 {res.resource_name}",
                "description": f"""获取 {res.resource_name} ({res.resource_key}) 的动态数据列表。

**模式**: {res.resource_mode}
**来源**: {res.data_source}
**备注**: {getattr(res, 'remarks', None) or '无'}

> <div style="font-size: 12px; color: #555;">
> 筛选规则 / Filter Usage:
>
> 1. 单值精确匹配 (Equality):
> `key=value` (e.g. `?status=active`)
>
> 2. 多值包含查询 (IN Query):
> *   重复参数名 / Repeated Keys:
>     `?city=Beijing&city=Shanghai`
> *   JSON 数组字符串 / JSON Array (Recommended):
>     `?city=["Beijing", "Shanghai"]`
> </div>
""",
                "operationId": f"get_resource_{res.resource_key}",
                "parameters": parameters,
                "responses": {
                    "200": {
                        "description": "成功响应",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{resp_schema_name}"
                                }
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/400"},
                    "401": {"$ref": "#/components/responses/401"},
                    "403": {"$ref": "#/components/responses/403"},
                    "500": {"$ref": "#/components/responses/500"}
                },
                "security": [{"X-API-Key": []}]
            }
            
            # Inject into paths
            openapi_schema["paths"][path_key] = {
                "get": operation,
                "post": {
                    "tags": [res.resource_group],
                    "summary": f"查询 {res.resource_name} (POST)",
                    "description": f"""POST 方式查询 {res.resource_name}，支持复杂 JSON 筛选条件。
                    
**适用于**:
-当筛选条件过多(如 `IN` 查询包含大量 ID)导致 URL 超长时。
-需要结构化传递参数时。

**Body 参数说明**:
- `filters`: 筛选条件列表，格式为 `[[字段, 操作符, 值], ...]`
- `page`: 页码 (默认 1)
- `size`: 每页数量 (默认 20)
- `sort_by`: 排序字段
- `sort_order`: 排序方向 (`asc`, `desc`)

**筛选操作符**:
- `=`: 等于
- `!=`: 不等于
- `>` / `<` / `>=` / `<=`: 比较
- `LIKE`: 模糊匹配 (值包含 `%`)
- `IN`: 包含于 (值必须为列表)

**示例**:
```json
{{
  "filters": [
    ["status", "=", "active"],
    ["id", "IN", ["1001", "1002"]]
  ],
  "page": 1,
  "size": 50
}}
```
""",
                    "operationId": f"post_resource_{res.resource_key}",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ResourceQueryRequest"
                                },
                                "example": {
                                    "filters": [
                                        ["status", "=", "active"],
                                        ["id", "IN", ["1001", "1002", "1003"]]
                                    ],
                                    "page": 1,
                                    "size": 20,
                                    "sort_by": "create_time",
                                    "sort_order": "desc"
                                }
                            }
                        },
                        "required": True
                    },
                    "responses": {
                        "200": {
                            "description": "成功响应",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{resp_schema_name}"
                                    }
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/400"},
                        "401": {"$ref": "#/components/responses/401"},
                        "403": {"$ref": "#/components/responses/403"},
                        "500": {"$ref": "#/components/responses/500"}
                    },
                    "security": [{"X-API-Key": []}]
                }
            }
            
    except Exception as e:
        logging.error(f"Failed to inject dynamic docs: {e}")
        # Not including traceback here to avoid bloating logs if it's a temp DB issue

    
    # 过滤路径：只显示 /api/v1 和 /health，隐藏 /api/portal 内部管理接口
    filtered_paths = {}
    for path, path_item in openapi_schema["paths"].items():
        # 只保留 /api/v1 开头的路径和 /health
        if path.startswith("/api/v1") or path == "/health":
            # If it's the generic one, maybe skip it if we want only specific ones?
            # For now keep everything.
            filtered_paths[path] = path_item
            
            # Apply security to all endpoints except /health (redundant for dynamic ones since we added it, but safe)
            if path != "/health":
                for method in path_item.values():
                    if isinstance(method, dict) and ("parameters" in method or "requestBody" in method or "responses" in method):
                        # Don't overwrite if already set (like our dynamic ones)
                        if "security" not in method:
                            method["security"] = [{"X-API-Key": []}]
    
    openapi_schema["paths"] = filtered_paths
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
