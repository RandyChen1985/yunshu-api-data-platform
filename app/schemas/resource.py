from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json

SYSTEM_RESOURCE_GROUP = "System"


def validate_user_resource_group(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip().lower() == SYSTEM_RESOURCE_GROUP.lower():
        raise ValueError("'System' 分组为系统内置，不可用于普通资源")
    return v

class FieldConfig(BaseModel):
    name: str = Field(..., description="Technical field name")
    label: str = Field(..., description="Human-readable label (CN)")
    type: str = Field(..., description="Data type (e.g. String, Float64)")

class ResourceBase(BaseModel):
    resource_key: str = Field(..., description="Unique key for the resource API")
    resource_name: str = Field(..., description="Human readable name")
    resource_group: str = Field("Default", description="Group name for categorization")
    data_source: str = Field("clickhouse", description="Data source type (clickhouse, mysql, etc.)")
    resource_mode: str = Field("TABLE", description="Mode: TABLE or SQL")
    table_name: Optional[str] = Field(None, description="Physical table name (for TABLE mode)")
    custom_sql: Optional[str] = Field(None, description="Custom SQL query (for SQL mode)")
    fields_config: List[FieldConfig] = Field(..., description="List of fields to select/return")
    allowed_filters: List[FieldConfig] = Field(default_factory=list, description="List of allowed filter fields")
    default_sort: str = Field("rowkey", description="Default sort field")
    status: int = Field(1, description="Status: 1=Enabled, 0=Disabled")
    cache_ttl: Optional[int] = Field(0, description="Cache TTL in seconds (0=Disabled)")
    remarks: Optional[str] = Field(None, description="Optional remarks or notes about the resource")

    @validator('resource_mode')
    def validate_mode(cls, v):
        if v not in ('TABLE', 'SQL', 'SYSTEM'):
            raise ValueError("resource_mode must be 'TABLE', 'SQL' or 'SYSTEM'")
        return v

class ResourceCreate(ResourceBase):
    @validator('resource_group')
    def validate_group_not_system(cls, v):
        return validate_user_resource_group(v)

class ResourceUpdate(BaseModel):
    resource_name: Optional[str] = None
    resource_group: Optional[str] = None
    data_source: Optional[str] = None
    resource_mode: Optional[str] = None
    table_name: Optional[str] = None
    custom_sql: Optional[str] = None
    fields_config: Optional[List[FieldConfig]] = None
    allowed_filters: Optional[List[FieldConfig]] = None
    default_sort: Optional[str] = None
    status: Optional[int] = None
    cache_ttl: Optional[int] = None
    remarks: Optional[str] = None

class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    created_at: datetime
    updated_at: datetime
    reference_count: Optional[int] = Field(0, description="Number of users referencing this resource")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
