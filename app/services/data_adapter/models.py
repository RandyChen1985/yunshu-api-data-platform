from typing import Any, List, Dict, Optional, Tuple
from pydantic import BaseModel, Field, field_validator

class LogicalQuery(BaseModel):
    resource: str
    filters: List[Tuple[str, str, Any]] = Field(default_factory=list) # (field, op, value)
    sort_by: str = Field(default="metric_time")
    sort_order: str = Field(default="desc")
    page: int = Field(default=1)
    size: int = Field(default=20)

    @field_validator('sort_by', mode='before')
    @classmethod
    def validate_sort_by(cls, v: Any) -> str:
        if v is None:
            return "metric_time"
        return str(v)

    @field_validator('sort_order', mode='before')
    @classmethod
    def validate_sort_order(cls, v: Any) -> str:
        if v is None:
            return "desc"
        v = str(v).lower()
        if v not in ('asc', 'desc'):
            raise ValueError('sort_order must be "asc" or "desc"')
        return v

    @field_validator('page', 'size')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Must be positive')
        return v

class ResultSet(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    size: int
    pages: int
    generated_sql: Optional[str] = None
