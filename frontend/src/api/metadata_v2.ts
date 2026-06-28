import axios from '../utils/axios'

export interface Dataset {
  id: number
  name: string
  display_name: string
  description: string
  data_source: string
  tags: string[]
  status: number
  vector_status?: number // 0:未同步, 1:已同步, 2:同步中, 3:失败, 4:内容已变动(待更新)
  last_vectorized_at?: string
  table_count?: number
  metric_count?: number
  usage_count?: number
  updated_at?: string
  created_at?: string
  creator_name?: string
}

export const metadataV2Api = {
  // Datasets
  getDatasets: () => axios.get<Dataset[]>('/api/portal/meta/v2/datasets'),
  getDataset: (id: number) => axios.get<any>(`/api/portal/meta/v2/datasets/${id}`),
  createDataset: (data: any) => axios.post('/api/portal/meta/v2/datasets', data),
  updateDataset: (id: number, data: any) => axios.put(`/api/portal/meta/v2/datasets/${id}`, data),
  deleteDataset: (id: number) => axios.delete(`/api/portal/meta/v2/datasets/${id}`),
  syncVector: (id: number) => axios.post(`/api/portal/meta/v2/datasets/${id}/sync-vector`),
  
  // AI Import
  analyzeDDL: (content: string) => axios.post('/api/portal/meta/v2/datasets/analyze-ddl', { content }),
  saveTable: (datasetId: number, tableData: any) => axios.post(`/api/portal/meta/v2/datasets/${datasetId}/save-table`, tableData),
  deleteTable: (datasetId: number, tableId: number) => axios.delete(`/api/portal/meta/v2/datasets/${datasetId}/tables/${tableId}`),
  
  // Metrics & Relationships
  createMetric: (datasetId: number, data: any) => axios.post(`/api/portal/meta/v2/datasets/${datasetId}/metrics`, data),
  deleteMetric: (datasetId: number, metricId: number) => axios.delete(`/api/portal/meta/v2/datasets/${datasetId}/metrics/${metricId}`),
  recommendMetrics: (datasetId: number) => axios.post<{data: any[]}>(`/api/portal/meta/v2/datasets/${datasetId}/metrics/recommend`),
  recommendRelationships: (datasetId: number) => axios.post<{data: any[]}>(`/api/portal/meta/v2/datasets/${datasetId}/relationships/recommend`),
  createRelationship: (datasetId: number, data: any) => axios.post(`/api/portal/meta/v2/datasets/${datasetId}/relationships`, data),
  deleteRelationship: (datasetId: number, relId: number) => axios.delete(`/api/portal/meta/v2/datasets/${datasetId}/relationships/${relId}`),
  
  // Usage & Impact Analysis
  getDatasetUsage: (id: number) => axios.get<{data: any[]}>(`/api/portal/meta/v2/datasets/${id}/usage`),
  
  // Export
  getDatasetYaml: (id: number) => axios.get<{data: string}>(`/api/portal/meta/v2/datasets/${id}/yaml`),
  
  // Search & Simulator
  searchMetadata: (data: { query: string, data_source: string, search_type: string, enable_rerank?: boolean }) => 
    axios.post<{data: string, count: number, dataset_ids: number[], debug_logs: string[]}>('/api/portal/meta/v2/search', data),

  // Vector Browsing
  browseVectors: (params: { data_source?: string, dataset_id?: number, page?: number, page_size?: number }) =>
    axios.get<{ total: number, items: any[], page: number, page_size: number }>('/api/portal/meta/v2/vector/browse', { params }),
  
  getVectorDetails: (key: string) =>
    axios.get<any>('/api/portal/meta/v2/vector/details', { params: { key } })
}

/**
 * 元数据检索类型常量
 */
export const SEARCH_TYPES = {
  KEYWORD: 'keyword',
  SEMANTIC: 'semantic'
} as const;

export type SearchType = typeof SEARCH_TYPES[keyof typeof SEARCH_TYPES];

