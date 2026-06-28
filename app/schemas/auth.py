from typing import List, Optional, Dict
from pydantic import BaseModel

class PermissionSet(BaseModel):
    menus: List[str] = []
    elements: List[str] = []
    resources: List[str] = []
    datasources: List[str] = [] # 新增：数据源权限 (ds:name)
    data_tables: List[str] = [] # 新增：数据表权限 (ds:name:table:name)

class UserPermissionsResponse(BaseModel):
    user_id: int
    username: str
    role: str # System role: admin/user
    business_roles: List[str] = [] # Business roles from sys_roles
    permissions: PermissionSet

class RoleBase(BaseModel):
    role_code: str
    role_name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int

class UserPermissionUpdate(BaseModel):
    role_ids: List[int] = []
    direct_menus: List[str] = []
    direct_elements: List[str] = []
    resource_keys: List[str] = [] # For existing sys_user_resources
