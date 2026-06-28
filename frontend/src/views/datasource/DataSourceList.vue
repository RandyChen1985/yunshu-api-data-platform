<script setup lang="ts">
import { ref, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { useToast } from '../../composables/useToast'
import Switch from '../../components/Switch.vue'
import { 
  PencilSquareIcon, 
  TrashIcon, 
  PlayIcon,
  CircleStackIcon,
  Bars3Icon
} from '@heroicons/vue/24/outline'

const { showToast } = useToast()

// Data
const loading = ref(false)
const datasources = ref<any[]>([])

// Dialogs
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const showTestDialog = ref(false) // For connection testing result

// Form Data
const formData = ref({
  source_name: '',
  source_type: 'clickhouse',
  host: '',
  port: 9000,
  database_name: '',
  username: '',
  password: '',
  description: '',
  status: 1
})
const editingId = ref<number | null>(null)
const submitting = ref(false)
const error = ref('')

// Delete State
const itemToDelete = ref<any>(null)

// Test Connection State
const testingConnection = ref(false)
const testResult = ref<any>(null)

// Reorder State
const reordering = ref(false)

// Fetch Data Sources
const fetchDatasources = async () => {
  loading.value = true
  try {
    const apiKey = localStorage.getItem('api_key')
    const response = await fetch('/api/portal/datasource/datasources', {
      headers: { 'X-API-Key': apiKey || '' }
    })
    if (!response.ok) throw new Error('获取已配置数据源失败')
    datasources.value = await response.json()
  } catch (e: any) {
    console.error('Failed to fetch datasources:', e)
    showToast('获取数据源列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// Dialog Management
const openCreateDialog = () => {
  formData.value = {
    source_name: '',
    source_type: 'clickhouse',
    host: '',
    port: 9000,
    database_name: '',
    username: '',
    password: '',
    description: '',
    status: 1
  }
  error.value = ''
  editingId.value = null
  showCreateDialog.value = true
}

const openEditDialog = (item: any) => {
  formData.value = { ...item, password: '' } 
  error.value = ''
  editingId.value = item.id
  showEditDialog.value = true
}

const closeDialogs = () => {
  showCreateDialog.value = false
  showEditDialog.value = false
  showDeleteDialog.value = false
  showTestDialog.value = false
  testResult.value = null
  error.value = ''
}

// Update Port based on Type
const updatePort = () => {
  if (formData.value.source_type === 'clickhouse') {
    formData.value.port = 9000
  } else if (formData.value.source_type === 'mysql') {
    formData.value.port = 3306
  } else if (formData.value.source_type === 'oracle') {
    formData.value.port = 1521
  }
}

// Save Data Source
const saveDataSource = async () => {
  // Validations
  if (!formData.value.source_name) return error.value = '请输入数据源名称'
  if (!formData.value.host) return error.value = '请输入主机地址'
  if (!formData.value.port) return error.value = '请输入端口号'
  
  submitting.value = true
  error.value = ''
  
  try {
    const apiKey = localStorage.getItem('api_key')
    const url = editingId.value 
      ? `/api/portal/datasource/datasources/${editingId.value}`
      : '/api/portal/datasource/datasources'
    const method = editingId.value ? 'PUT' : 'POST'
    
    const payload: any = { ...formData.value }
    
    // 如果是编辑模式且密码为空，则不更新密码
    if (editingId.value && !payload.password) {
      delete payload.password
    }
    
    const response = await fetch(url, {
      method,
      headers: { 
        'Content-Type': 'application/json',
        'X-API-Key': apiKey || ''
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '保存失败')
    }
    
    showToast(editingId.value ? '更新成功' : '创建成功', 'success')
    closeDialogs()
    fetchDatasources()
  } catch (e: any) {
    console.error('Failed to save:', e)
    error.value = e.message || '保存失败'
  } finally {
    submitting.value = false
  }
}

// Toggle Status
const toggleStatus = async (item: any) => {
  const newStatus = item.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '启用' : '禁用'
  
  try {
    const apiKey = localStorage.getItem('api_key')
    const payload = { ...item, status: newStatus }
    
    const response = await fetch(`/api/portal/datasource/datasources/${item.id}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'X-API-Key': apiKey || ''
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) throw new Error('状态更新失败')
    
    showToast(`数据源已${action}`, 'success')
    fetchDatasources()
  } catch (e: any) {
    showToast(`${action}失败`, 'error')
  }
}

// Confirm Delete
const confirmDelete = (item: any) => {
  itemToDelete.value = item
  showDeleteDialog.value = true
}

// Execute Delete
const deleteDataSource = async () => {
  if (!itemToDelete.value) return
  
  try {
    const apiKey = localStorage.getItem('api_key')
    const response = await fetch(`/api/portal/datasource/datasources/${itemToDelete.value.id}`, {
      method: 'DELETE',
      headers: { 'X-API-Key': apiKey || '' }
    })
    
    if (!response.ok) {
      const data = await response.json()
      // API might return { message: "..." } or { detail: "..." }
      const errorMsg = data.message || data.detail || '删除失败'
      throw new Error(errorMsg)
    }
    
    showToast('删除成功', 'success')
    closeDialogs()
    fetchDatasources()
  } catch (e: any) {
    showToast(e.message || '删除失败', 'error')
  }
}

// Test Connection
const testConnection = async (item: any) => {
  testingConnection.value = true
  testResult.value = null
  showTestDialog.value = true
  
  try {
    const apiKey = localStorage.getItem('api_key')
    const response = await fetch(`/api/portal/datasource/datasources/${item.id}/test`, {
      method: 'POST',
      headers: { 'X-API-Key': apiKey || '' }
    })
    
    const data = await response.json()
    testResult.value = {
      success: data.status === 'success',
      message: data.message
    }
    
  } catch (e: any) {
    testResult.value = { success: false, message: '请求失败: ' + e.message }
      } finally {
      testingConnection.value = false
    }
  }
  
  // Save Order
  const saveReorder = async () => {
    reordering.value = true
    try {
      const apiKey = localStorage.getItem('api_key')
      const ids = datasources.value.map(ds => ds.id)
      
      const response = await fetch('/api/portal/datasource/reorder', {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': apiKey || ''
        },
        body: JSON.stringify({ ids })
      })
      
      if (!response.ok) throw new Error('保存排序失败')
      showToast('排序更新成功', 'success')
    } catch (e: any) {
      showToast(e.message || '排序更新失败', 'error')
      // Re-fetch to reset order if failed
      fetchDatasources()
    } finally {
      reordering.value = false
    }
  }
  
  onMounted(() => {
  
  fetchDatasources()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">数据源管理</h1>
      <button 
        @click="openCreateDialog" 
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新建数据源
      </button>
    </div>

    <!-- Data List -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div v-if="loading" class="p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-500">加载中...</p>
      </div>

      <div v-else-if="datasources.length === 0" class="p-12 text-center text-gray-500">
        <CircleStackIcon class="w-12 h-12 mx-auto text-gray-400 mb-2" />
        暂无数据源配置
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="w-10 px-6 py-3"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">名称 / 描述</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">连接信息</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <draggable 
            v-model="datasources" 
            tag="tbody" 
            item-key="id" 
            handle=".drag-handle"
            @change="saveReorder"
            class="bg-white divide-y divide-gray-200"
          >
            <template #item="{ element: item }">
              <tr class="hover:bg-gray-50 group">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="drag-handle cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600 transition-colors">
                    <Bars3Icon class="w-5 h-5" />
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">{{ item.source_name }}</div>
                  <div class="text-xs text-gray-500 truncate max-w-xs">{{ item.description || '-' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ item.source_type }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="font-mono text-xs">{{ item.host }}:{{ item.port }}</div>
                  <div class="text-xs text-gray-400">{{ item.database_name || 'default' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Switch 
                    :model-value="item.status === 1" 
                    @update:model-value="toggleStatus(item)"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex justify-end items-center gap-3">
                    <button @click="testConnection(item)" class="text-green-600 hover:text-green-900" title="测试连接">
                      <PlayIcon class="w-5 h-5" />
                    </button>
                    <button @click="openEditDialog(item)" class="text-blue-600 hover:text-blue-900" title="编辑">
                      <PencilSquareIcon class="w-5 h-5" />
                    </button>
                    <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900" title="删除">
                      <TrashIcon class="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </draggable>
        </table>
      </div>
    </div>

    <!-- Edit/Create Dialog -->
    <div v-if="showCreateDialog || showEditDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9990]" @click.self="closeDialogs">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-900">{{ showEditDialog ? '编辑数据源' : '新建数据源' }}</h2>
          <button @click="closeDialogs" class="text-gray-400 hover:text-gray-500">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveDataSource" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Source Name -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">数据源名称 <span class="text-red-500">*</span></label>
              <input 
                v-model="formData.source_name" 
                type="text" 
                required
                :disabled="showEditDialog"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="唯一标识，例如: prod_clickhouse"
              />
              <p v-if="showEditDialog" class="mt-1 text-xs text-gray-500">数据源名称创建后不可修改</p>
            </div>

            <!-- Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">数据源类型 <span class="text-red-500">*</span></label>
              <select 
                v-model="formData.source_type"
                @change="updatePort"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="clickhouse">ClickHouse</option>
                <option value="mysql">MySQL</option>
                <option value="oracle">Oracle</option>
              </select>
            </div>

            <!-- Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select 
                v-model.number="formData.status"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="1">启用</option>
                <option :value="0">停用</option>
              </select>
            </div>

            <!-- Host -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">主机地址 <span class="text-red-500">*</span></label>
              <input 
                v-model="formData.host" 
                type="text" 
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例如: localhost"
              />
            </div>

            <!-- Port -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">端口 <span class="text-red-500">*</span></label>
              <input 
                v-model.number="formData.port" 
                type="number" 
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- CheckBox for Params (Database) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">数据库名</label>
              <input 
                v-model="formData.database_name" 
                type="text" 
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="默认为 default"
              />
            </div>

            <!-- Auth -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <input 
                v-model="formData.username" 
                type="text" 
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
              <input 
                v-model="formData.password" 
                type="password" 
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                :placeholder="showEditDialog ? '留空则保持原密码' : ''"
              />
            </div>

            <!-- Description -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
              <textarea 
                v-model="formData.description" 
                rows="3"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              ></textarea>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-200">
            {{ error }}
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button 
              type="button" 
              @click="closeDialogs" 
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700"
            >
              取消
            </button>
            <button 
              type="submit" 
              :disabled="submitting" 
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Test Result Dialog -->
    <div v-if="showTestDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9990]" @click.self="closeDialogs">
      <div class="bg-white rounded-lg p-6 w-full max-w-sm text-center">
        <h3 class="text-lg font-bold mb-4">连接测试</h3>
        
        <div v-if="testingConnection" class="py-4">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-sm text-gray-500">正在尝试连接...</p>
        </div>

        <div v-else-if="testResult" class="py-4">
          <div v-if="testResult.success" class="text-green-600 mb-2">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <p class="font-bold">连接成功！</p>
          </div>
          <div v-else class="text-red-600 mb-2">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <p class="font-bold">连接失败</p>
            <p class="text-sm mt-1 text-gray-600 break-words">{{ testResult.message }}</p>
          </div>
        </div>

        <div class="mt-4">
          <button @click="closeDialogs" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg w-full">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Dialog -->
    <div v-if="showDeleteDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9990]" @click.self="showDeleteDialog = false">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4 text-red-600">确认删除</h2>
        <p class="text-gray-700 mb-6">确定要删除数据源 <strong>{{ itemToDelete?.source_name }}</strong> 吗？</p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteDialog = false" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            取消
          </button>
          <button @click="deleteDataSource" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
