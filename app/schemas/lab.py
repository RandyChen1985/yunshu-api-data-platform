from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class PreviewRequest(BaseModel):
    source_id: int
    sql: str
    params: Optional[Dict[str, Any]] = None
    limit: int = 100
    unmask: bool = False

class PublishRequest(BaseModel):
    resource_key: str
    resource_name: str
    resource_group: str = "Default"
    data_source: str
    resource_mode: str = "SQL"
    custom_sql: str
    fields_config: List[Any]
    allowed_filters: List[Any]
    default_sort: str
    status: int = 1
    cache_ttl: int = 0
    remarks: Optional[str] = None

class AIRequest(BaseModel):

    sql: str

    source_type: str = Field("mysql", description="mysql or clickhouse")



class AIGenerateRequest(BaseModel):
    prompt: str
    source_id: int
    tables: Optional[List[str]] = None
    mode: Optional[str] = "api" # 'api' or 'analyst'

class AIEditRequest(BaseModel):
    sql: str
    instruction: str
    source_id: int
    tables: Optional[List[str]] = None
    mode: Optional[str] = "api"




