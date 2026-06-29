<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { useToast } from '@/composables/useToast'
import { buildPlaygroundRoute } from '@/utils/playground'

const router = useRouter()
const { showToast } = useToast()
const loading = ref(true)
const requests = ref<any[]>([])
const statusFilter = ref<number | ''>('')
const syncingKey = ref<string | null>(null)

const statusOptions = [
  { v: '' as const, l: '全部' },
  { v: 0, l: '待审批' },
  { v: 1, l: '已通过' },
  { v: 2, l: '已拒绝' },
  { v: 3, l: '已收回' },
]

const statusLabel = (status: number) => {
  const map: Record<number, string> = {
    0: '待审批',
    1: '已通过',
    2: '已拒绝',
    3: '已收回',
  }
  return map[status] || '未知'
}

const statusClass = (status: number) => {
  if (status === 0) return 'bg-amber-100 text-amber-800'
  if (status === 1) return 'bg-green-100 text-green-800'
  if (status === 2) return 'bg-gray-100 text-gray-600'
  return 'bg-red-100 text-red-700'
}

const fetchRequests = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = {}
    if (statusFilter.value !== '') params.status = statusFilter.value
    const res = await axios.get('/api/portal/catalog/access-requests/mine', { params })
    requests.value = res.data
  } catch {
    requests.value = []
  } finally {
    loading.value = false
  }
}

const syncAccess = async (productKey: string) => {
  syncingKey.value = productKey
  try {
    const res = await axios.post(`/api/portal/catalog/products/${encodeURIComponent(productKey)}/sync-access`)
    await fetchRequests()
    if (res.data.has_access) {
      showToast('权限已生效', 'success')
    } else {
      showToast('已尝试同步，如仍不可用请联系产品负责人', 'warning')
    }
  } catch (e: any) {
    showToast(e.response?.data?.detail || '权限同步失败', 'error')
  } finally {
    syncingKey.value = null
  }
}

const playgroundRoute = (req: {
  product_key: string
  primary_resource_key?: string | null
  resource_group?: string | null
}) => {
  const key = req.primary_resource_key || req.product_key
  if (!key) return null
  return buildPlaygroundRoute({ resource_key: key, resource_group: req.resource_group })
}

onMounted(fetchRequests)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">我的申请</h1>
      <p class="text-sm text-gray-500 mt-1">查看您提交的数据产品 API 访问申请及处理进度</p>
    </div>

    <div class="flex flex-wrap gap-2">
      <button
        v-for="opt in statusOptions"
        :key="String(opt.v)"
        :class="statusFilter === opt.v ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600'"
        class="px-3 py-1.5 rounded-lg text-sm font-medium"
        @click="statusFilter = opt.v; fetchRequests()"
      >
        {{ opt.l }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">加载中...</div>
    <div v-else-if="!requests.length" class="text-center py-16 text-gray-400 bg-white rounded-xl border">
      暂无申请记录。可在
      <router-link to="/dashboard/catalog" class="text-indigo-600 hover:text-indigo-800 font-medium">产品目录</router-link>
      中浏览产品并提交申请。
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="req in requests"
        :key="req.id"
        class="bg-white rounded-xl border border-gray-100 p-5 hover:border-indigo-100 transition-colors"
      >
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <button
                type="button"
                class="text-lg font-bold text-gray-900 hover:text-indigo-600 text-left"
                @click="router.push(`/dashboard/catalog/${req.product_key}`)"
              >
                {{ req.product_name || req.product_key }}
              </button>
              <span :class="statusClass(req.status)" class="text-[10px] px-2 py-0.5 rounded-full font-medium">
                {{ statusLabel(req.status) }}
              </span>
              <span
                v-if="req.status === 1 && req.access_active"
                class="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full"
              >
                权限已生效
              </span>
              <span
                v-else-if="req.status === 1 && !req.access_active"
                class="text-[10px] bg-green-50 text-green-700 px-2 py-0.5 rounded-full"
              >
                已通过，待同步
              </span>
            </div>
            <p v-if="req.message" class="text-sm text-gray-600 mt-2">申请说明：{{ req.message }}</p>
            <div class="flex flex-wrap gap-4 mt-2 text-xs text-gray-400">
              <span>提交于 {{ req.created_at }}</span>
              <span v-if="req.handled_at">处理于 {{ req.handled_at }}</span>
              <span v-if="req.handler_name">处理人 {{ req.handler_name }}</span>
            </div>
            <p v-if="req.handle_remark" class="text-xs text-gray-500 mt-1">审批备注：{{ req.handle_remark }}</p>
          </div>
          <div class="flex gap-2 shrink-0">
            <router-link
              :to="`/dashboard/catalog/${req.product_key}`"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              查看产品
            </router-link>
            <router-link
              v-if="req.status === 1 && req.access_active && playgroundRoute(req)"
              :to="playgroundRoute(req)!"
              class="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              在线试用
            </router-link>
            <button
              v-else-if="req.status === 1 && !req.access_active"
              type="button"
              class="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              :disabled="syncingKey === req.product_key"
              @click="syncAccess(req.product_key)"
            >
              {{ syncingKey === req.product_key ? '同步中...' : '刷新权限' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
