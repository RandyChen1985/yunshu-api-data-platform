export interface DataSource {
  id: number
  source_name: string
  source_type: string
  host: string
  port: number
  database_name?: string | null
  username?: string | null
  password?: string | null
  description?: string | null
  sort_order?: number
  status: number
  created_at?: string
  updated_at?: string
}

export type DataSourceType = 'clickhouse' | 'mysql' | 'oracle'

export const DATA_SOURCE_TYPE_LABELS: Record<string, string> = {
  clickhouse: 'ClickHouse',
  mysql: 'MySQL',
  oracle: 'Oracle',
}

export function dataSourceTypeClass(type: string): string {
  switch (type) {
    case 'clickhouse':
      return 'bg-amber-50 text-amber-800 ring-1 ring-amber-200'
    case 'mysql':
      return 'bg-blue-50 text-blue-800 ring-1 ring-blue-200'
    case 'oracle':
      return 'bg-red-50 text-red-800 ring-1 ring-red-200'
    default:
      return 'bg-gray-100 text-gray-700 ring-1 ring-gray-200'
  }
}

export function defaultPortForType(type: string): number {
  switch (type) {
    case 'mysql':
      return 3306
    case 'oracle':
      return 1521
    default:
      return 9000
  }
}
