from typing import List, Optional, Union, Any
from pydantic import BaseModel

class TableDefinition(BaseModel):
    name: str
    type: str  # 'TABLE' or 'VIEW'

class TableListResponse(BaseModel):
    tables: Union[List[str], List[TableDefinition]]

class ColumnDefinition(BaseModel):
    name: str
    type: str
    comment: Optional[str] = None

class ColumnListResponse(BaseModel):
    columns: List[ColumnDefinition]

class ColumnIntrospectRequest(BaseModel):
    data_source: str = "clickhouse"
    table_name: Optional[str] = None
    custom_sql: Optional[str] = None
    params: Optional[dict] = None
