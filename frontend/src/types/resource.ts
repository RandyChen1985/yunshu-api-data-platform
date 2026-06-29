export interface Resource {
  resource_key: string
  resource_name: string
  resource_group?: string
  data_source: string
  resource_mode: string
  created_at?: string
  updated_at?: string
  status: number
  reference_count?: number
  remarks?: string
  cache_ttl?: number
  custom_sql?: string
  fields_config?: unknown[]
  allowed_filters?: unknown[]
}

/** 系统内置资源专用分组名（数据库迁移与 meta_service 硬编码使用） */
export const SYSTEM_RESOURCE_GROUP = 'System'

export interface ResourceGroupTab {
  name: string
  label: string
  count: number
  isSystem?: boolean
}

export function isSystemResourceGroup(name?: string | null): boolean {
  return (name || '').trim().toLowerCase() === SYSTEM_RESOURCE_GROUP.toLowerCase()
}

export function sortResourceGroups(groups: string[]): string[] {
  return [...groups].sort((a, b) => {
    if (isSystemResourceGroup(a)) return -1
    if (isSystemResourceGroup(b)) return 1
    return a.localeCompare(b, 'zh-CN')
  })
}

export interface AccessLog {
  id: number
  trace_id: string
  user_name: string
  method: string
  endpoint: string
  status_code: number
  process_time_ms: number
  client_ip: string
  created_at: string
  request_params?: string
}

export type ResourceSortField = 'updated_at' | 'resource_name' | 'status' | 'resource_mode'
