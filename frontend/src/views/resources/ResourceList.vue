<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import axios from '../../utils/axios'
import Toast from '../../components/Toast.vue'
import { useRouter } from 'vue-router'
import { 
  CircleStackIcon, 
  CommandLineIcon, 
  DocumentMagnifyingGlassIcon,
  ShieldCheckIcon,
  PlayIcon,
  ClockIcon,
  FolderIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const isSidebarCollapsed = ref(false)

interface Resource {
    resource_key: string;
    resource_name: string;
    resource_group?: string;
    data_source: string;
    resource_mode: string;
    created_at?: string;
    updated_at?: string;
    status: number;
    reference_count?: number;
    remarks?: string;
    cache_ttl?: number;
    custom_sql?: string;
    fields_config?: any[];
    allowed_filters?: any[];
}

const copyResourceUrl = (key: string) => {
    const url = `${window.location.origin}/api/v1/resources/${key}`
    navigator.clipboard.writeText(url)
    showToast('接口地址已复制', 'success')
}

// Batch Ops State
const selectedKeys = ref<Set<string>>(new Set())
const allSelected = computed(() => {
    return filteredResources.value.length > 0 && selectedKeys.value.size === filteredResources.value.length
})
const isIndeterminate = computed(() => {
    return selectedKeys.value.size > 0 && selectedKeys.value.size < filteredResources.value.length
})

const toggleAll = () => {
    if (allSelected.value) {
        selectedKeys.value.clear()
    } else {
        selectedKeys.value = new Set(filteredResources.value.map(r => r.resource_key))
    }
}

const toggleSelection = (key: string) => {
    if (selectedKeys.value.has(key)) {
        selectedKeys.value.delete(key)
    } else {
        selectedKeys.value.add(key)
    }
}

const batchDelete = async () => {
    if (selectedKeys.value.size === 0) return
    if (!confirm(`确定要删除选中的 ${selectedKeys.value.size} 个资源吗? 此操作无法撤销。`)) return
    
    loading.value = true
    let successCount = 0
    // Parallelize? Maybe strictly sequential is safer but slower. 
    // Let's do parallel with Promise.allSettled for speed.
    const promises = Array.from(selectedKeys.value).map(key => 
        axios.delete(`/api/portal/meta/resources/${key}`)
            .then(() => ({ status: 'fulfilled', key }))
            .catch(e => ({ status: 'rejected', key, reason: e }))
    )
    
    const results = await Promise.allSettled(promises)
    results.forEach(res => {
        if (res.status === 'fulfilled') successCount++
    })
    
    showToast(`批量删除完成: 成功 ${successCount}, 失败 ${selectedKeys.value.size - successCount}`, successCount > 0 ? 'success' : 'warning')
    selectedKeys.value.clear()
    fetchResources()
}

const batchUpdateStatus = async (status: number) => {
    if (selectedKeys.value.size === 0) return
    loading.value = true
    let successCount = 0
    const promises = Array.from(selectedKeys.value).map(key => 
        axios.put(`/api/portal/meta/resources/${key}`, { status })
            .then(() => ({ status: 'fulfilled', key }))
            .catch(e => ({ status: 'rejected', key, reason: e }))
    )
     const results = await Promise.allSettled(promises)
    results.forEach(res => {
        if (res.status === 'fulfilled') successCount++
    })
    showToast(`批量更新完成: 成功 ${successCount}, 失败 ${selectedKeys.value.size - successCount}`, successCount > 0 ? 'success' : 'warning')
    selectedKeys.value.clear()
    fetchResources()
}

// SQL Preview Logic
import { Codemirror } from 'vue-codemirror'
import { sql } from '@codemirror/lang-sql'
import { oneDark } from '@codemirror/theme-one-dark'

const showSqlPreviewModal = ref(false)
const previewSqlContent = ref('')
const extensions = [sql(), oneDark] // Shared with Edit View

const openSqlPreview = (sqlContent: string) => {
    previewSqlContent.value = sqlContent || '-- 无自定义 SQL'
    showSqlPreviewModal.value = true
}

const resources = ref<Resource[]>([])
const loading = ref(false)
const searchQuery = ref('')
const searchGroupQuery = ref('')
const statusFilter = ref<'ALL' | '1' | '0'>('ALL')
const activeTab = ref('ALL') // Replaces groupFilter
const onlyAuthorized = ref(false)
const importFile = ref<HTMLInputElement | null>(null)
const isAdmin = ref(false)

// Check user role
const userInfo = ref<any>(null)

const checkIsAdmin = () => {
    try {
        const userInfoStr = localStorage.getItem('user_info')
        if (userInfoStr) {
            userInfo.value = JSON.parse(userInfoStr)
            isAdmin.value = userInfo.value.role === 'admin'
        }
    } catch (e) {
        console.error('Failed to parse user info', e)
    }
}

const hasPerm = (code: string) => {
    if (isAdmin.value) return true
    return userInfo.value?.permissions?.elements?.includes(code)
}



// Toast State
const toast = ref({
  show: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'warning' | 'info',
  key: 0
})

const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  toast.value = { show: true, message, type, key: toast.value.key + 1 }
}
const closeToast = () => { toast.value.show = false }

const fetchResources = async () => {
    loading.value = true
    try {
        const response = await axios.get('/api/portal/meta/resources')
        resources.value = response.data
    } catch (e: any) {
        showToast(e.response?.data?.detail || 'Fetch failed', 'error')
    } finally {
        loading.value = false
    }
}

const groupTabs = computed(() => {
    // Calculate counts for each group
    const counts: Record<string, number> = {}
    let total = 0
    
    // Filter by search query FIRST (optional?? No, usually tabs show total count regardless of search, or filtered count?)
    // Tabs usually show "All Resources" count. Let's calculate based on ALL resources to show full scope.
    resources.value.forEach(r => {
        const g = r.resource_group || 'Default'
        counts[g] = (counts[g] || 0) + 1
        total++
    })
    
    const tabs = Object.keys(counts).sort().map(g => ({
        name: g,
        label: g,
        count: counts[g]
    }))
    
    // Add "All" tab
    return [
        { name: 'ALL', label: '全部资源', count: total },
        ...tabs
    ]
})

const filteredGroupTabs = computed(() => {
  if (!searchGroupQuery.value) return groupTabs.value
  return groupTabs.value.filter(t => t.label.toLowerCase().includes(searchGroupQuery.value.toLowerCase()))
})

const filteredResources = computed(() => {
    const q = searchQuery.value.toLowerCase()
    return resources.value.filter((r: Resource) => {
        const matchesSearch = 
            r.resource_key.toLowerCase().includes(q) || 
            r.resource_name.toLowerCase().includes(q) ||
            (r.resource_group || '').toLowerCase().includes(q)
        
        const matchesStatus = statusFilter.value === 'ALL' 
            ? true 
            : String(r.status) === statusFilter.value
            
        // Filter by Tab
        const groupName = r.resource_group || 'Default'
        const matchesGroup = activeTab.value === 'ALL'
            ? true
            : groupName === activeTab.value

        // Filter by Permission
        let matchesAuth = true
        if (onlyAuthorized.value && !isAdmin.value) {
            const userRes = userInfo.value?.permissions?.resources || []
            matchesAuth = userRes.includes(r.resource_key)
        }

        return matchesSearch && matchesStatus && matchesGroup && matchesAuth
    })
})

const showDeleteModal = ref(false)
const resourceToDelete = ref('')

const confirmDeleteResource = (key: string) => {
    resourceToDelete.value = key
    showDeleteModal.value = true
}

const deleteResource = async () => {
    if (!resourceToDelete.value) return
    try {
        await axios.delete(`/api/portal/meta/resources/${resourceToDelete.value}`)
        showToast('删除成功', 'success')
        showDeleteModal.value = false
        fetchResources()
    } catch (e: any) {
        showToast(e.response?.data?.detail || '删除失败', 'error')
    }
}

const toggleStatus = async (resource: Resource) => {
    const originalStatus = resource.status;
    const newStatus = originalStatus === 1 ? 0 : 1;
    
    // Optimistic update
    resource.status = newStatus;
    
    try {
        await axios.put(`/api/portal/meta/resources/${resource.resource_key}`, {
             status: newStatus
        })
        showToast(`资源已${newStatus === 1 ? '启用' : '禁用'}`, 'success')
    } catch (e: any) {
        // Revert
        resource.status = originalStatus;
        showToast(e.response?.data?.detail || '状态更新失败', 'error')
    }
}

const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    // Fix Safari compatibility & Timezone:
    // 1. Replace space with T
    // 2. Append Z to treat naive string as UTC (fixing 8h lag)
    let dateInput = typeof dateStr === 'string' ? dateStr.replace(' ', 'T') : dateStr;
    
    return new Date(dateInput).toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    })
}

const datasourcesMap = ref<Record<string, string>>({})

const fetchDatasources = async () => {
  try {
    const response = await axios.get('/api/portal/datasource/datasources?status=active')
    const map: Record<string, string> = {}
    response.data.forEach((ds: any) => {
        map[ds.source_name] = ds.description || '无描述'
    })
    datasourcesMap.value = map
    } catch (e) {
        console.error('Failed to fetch datasources', e)
    }
}

const exportResource = (res: Resource) => {
    downloadResourceConfig(res.resource_key)
}

const downloadResourceConfig = async (key: string) => {
    try {
        const response = await axios.get(`/api/portal/meta/resources`)
        const all = response.data
        const found = all.find((r: any) => r.resource_key === key)
        if (!found) throw new Error('Resource not found')
        
        const dataStr = JSON.stringify(found, null, 2)
        const blob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${key}_config.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        showToast('导出成功', 'success')
    } catch (e) {
        showToast('导出失败', 'error')
    }
}

const handleImport = (event: Event) => {
    const input = event.target as HTMLInputElement
    if (!input.files || input.files.length === 0) return
    
    const file = input.files[0]
    if (!file) return
    const reader = new FileReader()
    
    reader.onload = (e) => {
        try {
            const json = JSON.parse(e.target?.result as string)
            router.push({ 
                path: '/dashboard/resources/create',
                state: { importedData: json }
            })
        } catch (err) {
            showToast('文件解析失败，请确保是有效的 JSON', 'error')
        }
    }
    
    reader.readAsText(file)
    input.value = ''
}

// --- SQL Test Modal Logic ---
const showSqlTestModal = ref(false)
const showTtlModal = ref(false)
const editingTtl = ref(30)
const loadingTtl = ref(false)

const testSqlForm = reactive({
    dataSource: '',
    sql: 'SELECT 1',
    cacheTtl: 30
})
const testResult = ref<string>('')
const loadingTest = ref(false)
const resultViewMode = ref<'json' | 'table'>('json')
const showCodeModal = ref(false)
const codeSnippet = ref('')
const codeLanguage = ref('bash') // for highlighting

// Log Modal State
interface AccessLog {
    id: number;
    trace_id: string;
    user_name: string;
    method: string;
    endpoint: string;
    status_code: number;
    process_time_ms: number;
    client_ip: string;
    created_at: string;
    request_params?: string;
}
const showLogModal = ref(false)
const currentLogResource = ref('')
const accessLogs = ref<AccessLog[]>([])
const loadingLogs = ref(false)
const selectedLog = ref<AccessLog | null>(null)

const openLogModal = async (resourceKey: string) => {
    currentLogResource.value = resourceKey
    showLogModal.value = true
    accessLogs.value = [] // clear previous
    selectedLog.value = null // clear detail
    await fetchAccessLogs(resourceKey)
}

const fetchAccessLogs = async (resourceKey: string) => {
    loadingLogs.value = true
    try {
        const response = await axios.get('/api/portal/logs/access', {
            params: { resource_key: resourceKey, limit: 50 }
        })
        accessLogs.value = response.data
    } catch (e: any) {
        showToast('获取日志失败', 'error')
    } finally {
        loadingLogs.value = false
    }
}

const resultTableData = computed(() => {
    try {
        const data = JSON.parse(testResult.value)
        if (Array.isArray(data)) return data
        return []
    } catch (e) { return [] }
})

const resultTableHeaders = computed(() => {
    const data = resultTableData.value
    if (data.length > 0) return Object.keys(data[0])
    return []
})

const generateCode = (type: 'curl' | 'python' | 'js') => {
    const url = `${window.location.origin}/api/v1/sql/execute`
    const apiKey = 'YOUR_API_KEY'
    const body = {
        data_source_id: testSqlForm.dataSource,
        sql: testSqlForm.sql,
        cache_ttl: testSqlForm.cacheTtl || undefined
    }

    if (type === 'curl') {
        codeLanguage.value = 'bash'
        codeSnippet.value = `curl -X POST "${url}" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(body, null, 2)}'`
    } else if (type === 'python') {
        codeLanguage.value = 'python'
        codeSnippet.value = `import requests
import json

url = "${url}"
headers = {
    "Authorization": "Bearer ${apiKey}",
    "Content-Type": "application/json"
}
data = ${JSON.stringify(body, null, 4)}

response = requests.post(url, headers=headers, json=data)
print(response.json())`
    } else if (type === 'js') {
        codeLanguage.value = 'javascript'
        codeSnippet.value = `const url = "${url}";
const headers = {
    "Authorization": "Bearer ${apiKey}",
    "Content-Type": "application/json"
};
const body = ${JSON.stringify(body, null, 4)};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(body)
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));`
    }
    showCodeModal.value = true
}

const openTtlModal = (res: Resource) => {
    editingTtl.value = res.cache_ttl || 30
    showTtlModal.value = true
}

const saveTtl = async () => {
    loadingTtl.value = true
    try {
        await axios.put('/api/portal/meta/resources/system.sql.execute', {
             cache_ttl: editingTtl.value
        })
        showToast('缓存时间设置成功', 'success')
        showTtlModal.value = false
        fetchResources() // Refresh to show new value
    } catch (e: any) {
        showToast(e.response?.data?.detail || '保存失败', 'error')
    } finally {
        loadingTtl.value = false
    }
}

const openSqlTestModal = () => {
    // Set default data source if available
    const keys = Object.keys(datasourcesMap.value)
    if (keys.length > 0 && !testSqlForm.dataSource) {
        testSqlForm.dataSource = keys[0] ?? ''
    }
    testResult.value = ''
    showSqlTestModal.value = true
}

const closeSqlTestModal = () => {
    showSqlTestModal.value = false
}

const runSqlTest = async () => {
    if (!testSqlForm.dataSource) {
        showToast('请选择数据源', 'warning')
        return
    }
    if (!testSqlForm.sql.trim()) {
        showToast('请输入 SQL 语句', 'warning')
        return
    }

    loadingTest.value = true
    testResult.value = 'Running...'

    try {
        const response = await axios.post('/api/v1/sql/execute', {
            data_source: testSqlForm.dataSource,
            sql: testSqlForm.sql,
            cache_ttl: testSqlForm.cacheTtl
        })
        // Format JSON result
        testResult.value = JSON.stringify(response.data, null, 2)
    } catch (e: any) {
        const errorDetail = e.response?.data?.detail 
            ? (typeof e.response.data.detail === 'object' ? JSON.stringify(e.response.data.detail) : e.response.data.detail)
            : e.message
        testResult.value = `Error: ${errorDetail}`
    } finally {
        loadingTest.value = false
    }
}
// ----------------------------

onMounted(() => {
    checkIsAdmin()
    if (!isAdmin.value) {
        onlyAuthorized.value = true
    }
    fetchResources()
    fetchDatasources()
})
</script>

<template>
  <div class="bg-white rounded-lg shadow h-[calc(100vh-8rem)] flex overflow-hidden border border-gray-200">
    <!-- Left Sidebar: Groups -->
    <div 
      class="bg-gray-50/50 border-r border-gray-200 flex flex-col shrink-0 transition-all duration-300 ease-in-out relative group/sidebar"
      :class="isSidebarCollapsed ? 'w-14' : 'w-64'"
    >
      <div class="p-3 border-b border-gray-200 flex items-center justify-between h-14 bg-white">
        <transition name="fade">
          <div v-if="!isSidebarCollapsed" class="w-full">
            <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">资源分组</h2>
            <div class="relative">
              <input 
                type="text" 
                v-model="searchGroupQuery"
                placeholder="搜索..." 
                class="w-full pl-7 pr-2 py-1 bg-gray-100 border-none rounded text-xs focus:ring-1 focus:ring-blue-500 transition-all outline-none"
              />
              <svg class="w-3 h-3 text-gray-400 absolute left-2 top-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
          </div>
        </transition>
        <button 
          v-if="isSidebarCollapsed" 
          @click="isSidebarCollapsed = false"
          class="mx-auto text-gray-400 hover:text-blue-600 transition-colors p-1 hover:bg-gray-100 rounded"
          title="展开"
        >
          <FolderIcon class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Collapse Toggle (Absolute) -->
      <button 
        @click="isSidebarCollapsed = !isSidebarCollapsed"
        class="absolute -right-3 top-16 bg-white border border-gray-200 rounded-full p-1 shadow-sm text-gray-400 hover:text-blue-600 z-10 opacity-0 group-hover/sidebar:opacity-100 transition-opacity"
        :title="isSidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
      >
        <component :is="isSidebarCollapsed ? ChevronDoubleRightIcon : ChevronDoubleLeftIcon" class="w-3 h-3" />
      </button>

      <div class="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
        <button
          v-for="tab in filteredGroupTabs"
          :key="tab.name"
          @click="activeTab = tab.name"
          class="w-full flex items-center rounded-md transition-all duration-200 group relative"
          :class="[
            activeTab === tab.name ? 'bg-white text-blue-600 shadow-sm ring-1 ring-gray-200' : 'text-gray-600 hover:bg-white hover:shadow-sm',
            isSidebarCollapsed ? 'justify-center py-2' : 'justify-between px-3 py-2'
          ]"
          :title="isSidebarCollapsed ? tab.label : ''"
        >
          <div class="flex items-center overflow-hidden">
            <FolderIcon 
              class="w-4 h-4 shrink-0" 
              :class="[
                activeTab === tab.name ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500',
                isSidebarCollapsed ? '' : 'mr-3'
              ]" 
            />
            <span v-if="!isSidebarCollapsed" class="truncate text-sm font-medium">{{ tab.label }}</span>
          </div>
          
          <span 
            v-if="!isSidebarCollapsed"
            :class="[
              activeTab === tab.name ? 'bg-blue-50 text-blue-600' : 'bg-gray-200 text-gray-500',
              'ml-2 py-0.5 px-1.5 rounded text-[10px] font-bold transition-colors'
            ]"
          >
            {{ tab.count }}
          </span>
          
          <!-- Collapsed Tooltip -->
          <div v-if="isSidebarCollapsed" class="absolute left-full top-1/2 -translate-y-1/2 ml-2 bg-gray-900 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-50 transition-opacity">
            {{ tab.label }} ({{ tab.count }})
          </div>
        </button>
      </div>
    </div>

    <!-- Right Content: Table & Actions -->
    <div class="flex-1 flex flex-col min-w-0 bg-white">
      <div class="p-6 space-y-6 flex-1 overflow-y-auto custom-scrollbar">
        <!-- Header -->
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ activeTab === 'ALL' ? '全部资源' : activeTab }}</h1>
            <p class="text-sm text-gray-500 mt-1">管理系统内所有的 API 资源接口。</p>
          </div>
          <div class="flex gap-2">
            <template v-if="hasPerm('element:resource:import')">
                <input type="file" ref="importFile" class="hidden" accept=".json" @change="handleImport" />
                <button @click="importFile?.click()" class="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition flex items-center gap-2 font-medium text-sm shadow-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                    导入配置
                </button>
            </template>
            <router-link v-if="hasPerm('element:resource:create')" to="/dashboard/resources/create" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2 text-sm font-medium shadow-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    新建资源
            </router-link>
            <div v-else class="text-xs font-bold text-gray-400 bg-gray-100 px-3 py-2 rounded-lg flex items-center gap-2">
                <ShieldCheckIcon class="w-4 h-4" /> 只读模式
            </div>
          </div>
        </div>

        <!-- Batch Actions Bar -->
        <div v-if="selectedKeys.size > 0 && (hasPerm('element:resource:edit') || hasPerm('element:resource:delete'))" class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between transition-all shadow-sm">
            <div class="flex items-center space-x-2">
                <span class="text-sm font-bold text-blue-700">已选择 {{ selectedKeys.size }} 项</span>
                <button @click="selectedKeys.clear()" class="text-xs text-blue-500 hover:text-blue-700 underline">取消选择</button>
            </div>
            <div class="flex items-center space-x-3">
                 <button @click="batchUpdateStatus(1)" class="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded hover:bg-green-200">批量启用</button>
                 <button @click="batchUpdateStatus(0)" class="px-3 py-1 bg-gray-200 text-gray-700 text-sm font-medium rounded hover:bg-gray-300">批量禁用</button>
                 <div class="h-4 w-px bg-gray-300 mx-2"></div>
                 <button @click="batchDelete" class="px-3 py-1 bg-red-100 text-red-700 text-sm font-medium rounded hover:bg-red-200">批量删除</button>
            </div>
        </div>

        <!-- Search / Filter Card -->
        <div class="bg-white shadow-sm border border-gray-200 rounded-lg p-4">
            <div class="flex items-center gap-4">
                <div class="flex-1 max-w-md relative text-gray-400 focus-within:text-gray-600">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </span>
                    <input 
                        v-model="searchQuery" 
                        type="text" 
                        placeholder="搜索资源 Key、名称..." 
                        class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent sm:text-sm"
                    />
                </div>
                
                <!-- Status Filter -->
                <select v-model="statusFilter" class="block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border ml-2 w-32">
                    <option value="ALL">全部状态</option>
                    <option value="1">已启用</option>
                    <option value="0">已禁用</option>
                </select>

                <div v-if="!isAdmin" class="ml-4 flex items-center">
                    <input id="auth-filter" type="checkbox" v-model="onlyAuthorized" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                    <label for="auth-filter" class="ml-2 block text-sm text-gray-700">
                        仅显示我有权限的
                    </label>
                </div>

                <div class="text-sm text-gray-500 ml-auto">
                    本组共 {{ filteredResources.length }} 个资源
                </div>
            </div>
        </div>

        <!-- Table Card -->
        <div class="bg-white shadow-sm border border-gray-200 rounded-lg overflow-hidden flex-1">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th v-if="hasPerm('element:resource:edit') || hasPerm('element:resource:delete')" class="px-6 py-4 text-left w-10">
                      <input type="checkbox" :checked="allSelected" :indeterminate="isIndeterminate" @change="toggleAll" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" />
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-widest">资源详情</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-widest">模式 & 数据源</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-widest">配置统计</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-widest">状态</th>
                  <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-widest">更新时间</th>
                  <th class="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-widest">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-if="loading">
                   <td colspan="7" class="px-6 py-20 text-center text-gray-500">
                      <div class="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4"></div>
                      <p class="text-sm font-medium">深度扫描资源中...</p>
                   </td>
                </tr>
                <tr v-else-if="filteredResources.length === 0">
                   <td colspan="7" class="px-6 py-20 text-center text-gray-400 italic">
                      <svg class="mx-auto h-12 w-12 text-gray-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                      暂无匹配的资源接口
                   </td>
                </tr>
                <tr v-for="res in filteredResources" :key="res.resource_key" 
                    class="hover:bg-gray-50/80 transition-all duration-200 group" 
                    :class="{'bg-blue-50/50': selectedKeys.has(res.resource_key)}"
                >
                  <td v-if="hasPerm('element:resource:edit') || hasPerm('element:resource:delete')" class="px-6 py-4">
                      <input 
                        type="checkbox" 
                        :checked="selectedKeys.has(res.resource_key)" 
                        @change="toggleSelection(res.resource_key)"
                        class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" 
                      />
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center">
                        <!-- Status Glow -->
                        <div 
                          class="w-2 h-2 rounded-full mr-4 flex-shrink-0 transition-all duration-500"
                          :class="res.status === 1 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-gray-300'"
                        ></div>
                        
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-0.5">
                                <span v-if="res.resource_mode === 'SYSTEM'" class="text-xs" title="系统内置">⚡️</span>
                                <div class="text-sm font-bold text-gray-900 truncate max-w-[12rem] tracking-tight">{{ res.resource_name }}</div>
                                <span v-if="res.resource_key === 'system.sql.execute'" 
                                      class="px-1.5 py-0.5 text-[10px] font-black rounded-md bg-red-100 text-red-700 border border-red-200 uppercase tracking-tighter shadow-sm whitespace-nowrap"
                                      title="允许执行任意 SQL，属于高危系统接口">
                                   ROOT 权限
                                </span>
                            </div>
                            <div class="text-[11px] text-gray-400 font-mono tracking-tight flex items-center gap-1 group-hover:text-blue-500 transition-colors">
                                {{ res.resource_key }}
                                <button @click.stop="copyResourceUrl(res.resource_key)" class="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-blue-100 rounded">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                  </td>

                  <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex flex-col gap-1.5">
                          <div class="flex items-center">
                            <span v-if="res.resource_mode === 'SYSTEM'" class="bg-gray-100 text-gray-600 text-[10px] font-black px-1.5 py-0.5 rounded border border-gray-200">SYSTEM</span>
                            <span v-else :class="res.resource_mode === 'SQL' ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-emerald-100 text-emerald-700 border-emerald-200'" class="text-[10px] font-black px-1.5 py-0.5 rounded border">
                                {{ res.resource_mode }}
                            </span>
                            <button v-if="res.resource_mode === 'SQL'" @click="openSqlPreview(res.custom_sql || '')" class="ml-2 text-gray-400 hover:text-amber-600 transition-colors"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg></button>
                          </div>
                          <div class="text-[11px] text-gray-500 font-bold bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100 inline-flex items-center w-fit">
                            <CircleStackIcon class="w-3 h-3 mr-1 text-gray-400" />
                            {{ res.data_source }}
                          </div>
                      </div>
                  </td>

                  <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center gap-3 text-xs">
                          <div class="text-center bg-gray-50 rounded-lg p-1 min-w-[3rem] border border-gray-100">
                              <div class="text-[9px] text-gray-400 uppercase font-black tracking-tighter">Fields</div>
                              <div class="font-mono font-bold text-gray-700">{{ Array.isArray(res.fields_config) ? res.fields_config.length : 0 }}</div>
                          </div>
                          <div class="text-center bg-gray-50 rounded-lg p-1 min-w-[3rem] border border-gray-100">
                              <div class="text-[9px] text-gray-400 uppercase font-black tracking-tighter">Filters</div>
                              <div class="font-mono font-bold text-gray-700">{{ Array.isArray(res.allowed_filters) ? res.allowed_filters.length : 0 }}</div>
                          </div>
                      </div>
                  </td>

                  <td class="px-6 py-4 whitespace-nowrap">
                       <button 
                          :disabled="res.resource_mode === 'SYSTEM' || !hasPerm('element:resource:edit')"
                          @click="toggleStatus(res)" 
                          :class="[res.status === 1 ? 'bg-green-500' : 'bg-gray-200', (res.resource_mode === 'SYSTEM' || !hasPerm('element:resource:edit')) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer shadow-inner']"
                          class="relative inline-flex h-5 w-10 flex-shrink-0 rounded-full border-2 border-transparent transition-all duration-300 ease-in-out focus:outline-none"
                        >
                          <span :class="res.status === 1 ? 'translate-x-5' : 'translate-x-0'" class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md transition duration-300 ease-in-out"></span>
                        </button>
                  </td>


                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-[11px] font-bold text-gray-500 tabular-nums uppercase leading-tight">
                        {{ formatDate(res.updated_at || res.created_at).split(' ')[0] }}
                        <br/>
                        <span class="text-[10px] text-gray-300 font-normal">{{ formatDate(res.updated_at || res.created_at).split(' ')[1] }}</span>
                    </div>
                  </td>

                  <td class="px-6 py-4 whitespace-nowrap text-right">
                    <div class="flex items-center justify-end space-x-1.5 opacity-40 group-hover:opacity-100 transition-opacity duration-300">
                        <!-- Special Actions for system.sql.execute -->
                        <template v-if="res.resource_key === 'system.sql.execute' && hasPerm('element:resource:manage_special')">
                            <button @click="openTtlModal(res)" class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" title="设置 TTL">
                                <ClockIcon class="w-4 h-4" />
                            </button>
                            <button @click="openSqlTestModal" class="p-1.5 text-indigo-500 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-all" title="SQL 测试">
                                <PlayIcon class="w-4 h-4" />
                            </button>
                        </template>

                        <!-- Standard Actions -->
                        <button @click="openLogModal(res.resource_key)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" title="查看调用日志">
                            <DocumentMagnifyingGlassIcon class="w-4 h-4" />
                        </button>
                        <button v-if="hasPerm('element:resource:export')" @click="exportResource(res)" class="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all" title="导出配置">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4-4m0 0l-4 4m4-4v12" /></svg>
                        </button>
                        
                        <router-link v-if="res.resource_key !== 'system.sql.execute'" :to="`/dashboard/playground?resource=${res.resource_key}`" class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all" title="去调试工具">
                            <CommandLineIcon class="w-4 h-4" />
                        </router-link>
                        
                        <div v-if="res.resource_key !== 'system.sql.execute'" class="w-px h-4 bg-gray-200 mx-1"></div>
                        
                        <router-link v-if="res.resource_key !== 'system.sql.execute'" :to="`/dashboard/resources/${res.resource_key}`" class="p-1.5 rounded-lg transition-all text-gray-400 hover:text-blue-600 hover:bg-blue-50" :title="hasPerm('element:resource:edit') ? '编辑配置' : '查看详情'">
                            <svg v-if="hasPerm('element:resource:edit')" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        </router-link>
                        <button v-if="hasPerm('element:resource:delete') && res.resource_mode !== 'SYSTEM'" @click="confirmDeleteResource(res.resource_key)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" title="彻底删除">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        </button>
                    </div>
                  </td>


                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Teleported Toast -->
    <teleport to="body">
      <Toast v-if="toast.show" :key="toast.key" :message="toast.message" :type="toast.type" @close="closeToast" />

      <!-- SQL Test Modal -->
      <div v-if="showSqlTestModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeSqlTestModal"></div>

          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                    SQL 在线测试 (仅管理员)
                  </h3>
                  <div class="mt-4 space-y-4">
                      <!-- Data Source -->
                      <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">选择数据源</label>
                          <select v-model="testSqlForm.dataSource" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border">
                              <option v-for="(desc, name) in datasourcesMap" :key="name" :value="name">
                                  {{ name }} ({{ desc }})
                              </option>
                          </select>
                      </div>
                      
                      <!-- SQL Input -->
                      <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">SQL 语句</label>
                          <textarea 
                              v-model="testSqlForm.sql" 
                              rows="4" 
                              class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono bg-gray-50"
                              placeholder="SELECT * FROM table LIMIT 10"
                          ></textarea>
                          <p class="text-xs text-gray-500 mt-1">仅支持 SELECT 查询，系统会自动添加 LIMIT。</p>
                      </div>

                      <!-- Cache TTL -->
                      <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">缓存时间 (TTL 秒)</label>
                          <input 
                              v-model.number="testSqlForm.cacheTtl" 
                              type="number" 
                              min="0"
                              class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                              placeholder="30"
                          />
                          <p class="text-xs text-gray-500 mt-1">本次测试使用的临时 TTL（不影响系统默认设置）。0 表示不缓存。</p>
                      </div>

                      <!-- Result -->
                      <div v-if="testResult">
                          <div class="flex items-center justify-between mb-2">
                              <label class="block text-sm font-medium text-gray-700">执行结果</label>
                              <div class="flex space-x-2 bg-gray-100 p-0.5 rounded-lg text-xs">
                                  <button @click="resultViewMode = 'json'" :class="{'bg-white shadow': resultViewMode === 'json', 'text-gray-500 hover:text-gray-900': resultViewMode !== 'json'}" class="px-3 py-1 rounded-md transition-all">JSON</button>
                                  <button @click="resultViewMode = 'table'" :class="{'bg-white shadow': resultViewMode === 'table', 'text-gray-500 hover:text-gray-900': resultViewMode !== 'table'}" class="px-3 py-1 rounded-md transition-all">表格</button>
                              </div>
                          </div>
                          
                          <div v-if="resultViewMode === 'json'" class="bg-gray-800 rounded-md p-4 overflow-x-auto max-h-96">
                              <pre class="text-green-400 text-xs font-mono whitespace-pre-wrap">{{ testResult }}</pre>
                          </div>
                          <div v-else class="border border-gray-200 rounded-md overflow-x-auto max-h-96">
                              <table v-if="resultTableData.length > 0" class="min-w-full divide-y divide-gray-200">
                                  <thead class="bg-gray-50">
                                      <tr>
                                          <th v-for="h in resultTableHeaders" :key="h" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky top-0 bg-gray-50">{{ h }}</th>
                                      </tr>
                                  </thead>
                                  <tbody class="bg-white divide-y divide-gray-200">
                                      <tr v-for="(row, idx) in resultTableData" :key="idx">
                                          <td v-for="h in resultTableHeaders" :key="h" class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">{{ row[h] }}</td>
                                      </tr>
                                  </tbody>
                              </table>
                              <div v-else class="p-8 text-center text-gray-400 text-sm">
                                  无法解析为表格数据 (非数组或空)
                              </div>
                          </div>
                      </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse justify-between items-center">
              <div class="flex flex-row-reverse space-x-reverse space-x-3">
                  <button 
                      type="button" 
                      :disabled="loadingTest"
                      @click="runSqlTest"
                      class="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:w-auto sm:text-sm"
                      :class="{'opacity-50 cursor-not-allowed': loadingTest}"
                  >
                    <span v-if="loadingTest" class="mr-2">Executing...</span>
                    <span v-else>执行查询</span>
                  </button>
                  <button 
                      type="button" 
                      @click="closeSqlTestModal"
                      class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
                  >
                    关闭
                  </button>
              </div>
              <div class="flex space-x-2 mt-3 sm:mt-0">
                  <span class="text-xs text-gray-400 self-center mr-2">生成代码:</span>
                  <button @click="generateCode('curl')" class="text-xs text-blue-600 hover:text-blue-800 font-medium">cURL</button>
                  <span class="text-gray-300">|</span>
                  <button @click="generateCode('python')" class="text-xs text-blue-600 hover:text-blue-800 font-medium">Python</button>
                  <span class="text-gray-300">|</span>
                  <button @click="generateCode('js')" class="text-xs text-blue-600 hover:text-blue-800 font-medium">Node.js</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TTL Config Modal -->
      <div v-if="showTtlModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showTtlModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-sm sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                      <h3 class="text-lg leading-6 font-medium text-gray-900">
                          设置默认缓存时间 (TTL)
                      </h3>
                      <div class="mt-4">
                          <label class="block text-sm font-medium text-gray-700 mb-1">系统默认 TTL (秒)</label>
                          <input 
                              v-model.number="editingTtl" 
                              type="number" 
                              min="0"
                              class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                          />
                          <p class="text-xs text-gray-500 mt-2">
                              所有未指定 TTL 的 [system.sql.execute] 请求将使用此默认值。
                          </p>
                      </div>
                  </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  :disabled="loadingTtl"
                  @click="saveTtl"
                  class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  :class="{'opacity-50 cursor-not-allowed': loadingTtl}"
              >
                {{ loadingTtl ? 'Saving...' : '保存设置' }}
              </button>
              <button 
                  type="button" 
                  @click="showTtlModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SQL Preview Modal -->
      <div v-if="showSqlPreviewModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-preview-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showSqlPreviewModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                      <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                          SQL 预览
                      </h3>
                      <div class="border border-gray-300 rounded-md shadow-sm overflow-hidden bg-gray-900">
                          <codemirror
                              v-model="previewSqlContent"
                              :disabled="true"
                              :style="{ height: '400px' }"
                              :extensions="extensions"
                          />
                      </div>
                  </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  @click="showSqlPreviewModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Code Snippet Modal -->
      <div v-if="showCodeModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-code-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCodeModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                      <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">调用代码示例</h3>
                      <div class="border border-gray-300 rounded-md shadow-sm overflow-hidden bg-gray-900">
                          <codemirror
                              v-model="codeSnippet"
                              :disabled="true"
                              :style="{ height: '300px' }"
                              :extensions="extensions"
                          />
                      </div>
                  </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  @click="showCodeModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Log Modal -->
      <div v-if="showLogModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-log-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showLogModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                      <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                          资源访问日志: {{ currentLogResource }}
                      </h3>
                      
                      <div class="border border-gray-200 rounded-md overflow-x-auto max-h-[60vh]">
                          <table class="min-w-full divide-y divide-gray-200">
                              <thead class="bg-gray-50 sticky top-0">
                                  <tr>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方法</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">耗时</th>
                                      <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trace ID</th>
                                  </tr>
                              </thead>
                              <tbody class="bg-white divide-y divide-gray-200">
                                  <tr v-if="loadingLogs">
                                      <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                                          <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
                                          加载中...
                                      </td>
                                  </tr>
                                  <tr v-else-if="accessLogs.length === 0">
                                      <td colspan="7" class="px-6 py-8 text-center text-gray-500 italic">暂无最近访问记录</td>
                                  </tr>
                                  <tr v-for="log in accessLogs" :key="log.id" 
                                      @click="selectedLog = log"
                                      class="hover:bg-gray-50 text-xs cursor-pointer transition-colors"
                                      :class="{'bg-blue-50 ring-1 ring-inset ring-blue-200': selectedLog?.id === log.id}">
                                      <td class="px-3 py-2 whitespace-nowrap text-gray-500">{{ formatDate(log.created_at) }}</td>
                                      <td class="px-3 py-2 whitespace-nowrap font-medium text-gray-900">{{ log.user_name }}</td>
                                      <td class="px-3 py-2 whitespace-nowrap text-gray-500">{{ log.client_ip }}</td>
                                      <td class="px-3 py-2 whitespace-nowrap">
                                          <span :class="{'text-green-600': log.method === 'GET', 'text-blue-600': log.method === 'POST'}" class="font-bold">{{ log.method }}</span>
                                      </td>
                                      <td class="px-3 py-2 whitespace-nowrap">
                                          <span :class="log.status_code >= 400 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'" class="px-2 py-0.5 rounded-full text-xs font-medium">
                                              {{ log.status_code }}
                                          </span>
                                      </td>
                                      <td class="px-3 py-2 whitespace-nowrap text-gray-500">{{ log.process_time_ms.toFixed(2) }}ms</td>
                                      <td class="px-3 py-2 whitespace-nowrap text-gray-400 font-mono">{{ log.trace_id.substring(0, 8) }}...</td>
                                  </tr>
                              </tbody>
                          </table>
                      </div>
                  </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  @click="showLogModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                关闭
              </button>
              <button 
                  type="button" 
                  @click="fetchAccessLogs(currentLogResource)"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                刷新
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Log Detail Modal (Level 2) -->
      <div v-if="selectedLog" class="fixed inset-0 z-[60] overflow-y-auto" aria-labelledby="modal-log-detail-title" role="dialog" aria-modal="true">
        <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="selectedLog = null"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-2xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4 flex justify-between items-center" id="modal-log-detail-title">
                    <span>日志详情</span>
                    <span class="text-xs font-mono text-gray-400 bg-gray-100 px-2 py-1 rounded">{{ selectedLog.trace_id }}</span>
                  </h3>
                  <div class="space-y-4 text-sm">
                      <div class="grid grid-cols-2 gap-4">
                          <div class="bg-gray-50 p-3 rounded border border-gray-100">
                              <span class="block text-xs text-gray-500 mb-1">请求方法 & 路径</span>
                              <div class="font-bold break-all">{{ selectedLog.method }} {{ selectedLog.endpoint }}</div>
                          </div>
                          <div class="bg-gray-50 p-3 rounded border border-gray-100">
                              <span class="block text-xs text-gray-500 mb-1">客户端 IP & 用户</span>
                              <div class="font-bold">{{ selectedLog.client_ip }} <span class="text-gray-400">/</span> {{ selectedLog.user_name }}</div>
                          </div>
                      </div>
                      
                      <div>
                          <span class="block text-xs text-gray-500 mb-1 font-medium">Request Params (JSON)</span>
                          <div class="bg-gray-900 rounded-md p-3 overflow-x-auto max-h-60 border border-gray-700">
                              <pre class="text-green-400 text-xs font-mono whitespace-pre-wrap break-all">{{ (() => { try { return JSON.stringify(JSON.parse(selectedLog.request_params || '{}'), null, 2) } catch { return selectedLog.request_params } })() }}</pre>
                          </div>
                      </div>

                      <div class="grid grid-cols-3 gap-4 text-center">
                          <div class="p-2 bg-blue-50 rounded">
                              <div class="text-xs text-blue-500">状态码</div>
                              <div class="font-bold text-blue-700">{{ selectedLog.status_code }}</div>
                          </div>
                          <div class="p-2 bg-blue-50 rounded">
                              <div class="text-xs text-blue-500">耗时</div>
                              <div class="font-bold text-blue-700">{{ selectedLog.process_time_ms.toFixed(2) }}ms</div>
                          </div>
                          <div class="p-2 bg-blue-50 rounded">
                              <div class="text-xs text-blue-500">时间</div>
                              <div class="font-bold text-blue-700 text-xs mt-1">{{ formatDate(selectedLog.created_at) }}</div>
                          </div>
                      </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  @click="selectedLog = null"
                  class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>


      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-delete-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                      <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                  </div>
                  <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                      <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-delete-title">
                          确认删除资源?
                      </h3>
                      <div class="mt-2">
                          <p class="text-sm text-gray-500">
                              即将删除资源 <span class="font-mono font-bold text-gray-800">{{ resourceToDelete }}</span>。
                              <br/>此操作无法撤销，由该资源提供的 API 服务将立即停止。
                          </p>
                      </div>
                  </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                  type="button" 
                  @click="deleteResource"
                  class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                确认删除
              </button>
              <button 
                  type="button" 
                  @click="showDeleteModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.custom-tooltip {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.custom-tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 150%;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(31, 41, 55, 0.95);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  width: max-content;
  max-width: 300px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 9999;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  pointer-events: none;
  font-weight: normal;
}

.custom-tooltip::before {
  content: '';
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(31, 41, 55, 0.95) transparent transparent transparent;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 9999;
}

.custom-tooltip:hover::after {
  opacity: 1;
  visibility: visible;
  bottom: 160%;
}

.custom-tooltip:hover::before {
  opacity: 1;
  visibility: visible;
  bottom: 130%;
}
</style>
