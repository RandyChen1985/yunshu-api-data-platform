<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { useToast } from '@/composables/useToast'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const { showToast } = useToast()
const refreshCatalogBadge = inject<(() => Promise<void>) | undefined>('refreshCatalogBadge')
const loading = ref(true)
const requests = ref<any[]>([])
const statusFilter = ref<number | ''>(0)
const remark = ref('')
const handlingId = ref<number | null>(null)
const currentUserId = ref<number | null>(null)

const confirmDialog = ref({
  show: false,
  title: '',
  message: '',
  type: 'warning' as 'danger' | 'warning' | 'info',
  confirmText: '确认',
  onConfirm: () => {},
})

const openConfirm = (opts: {
  title: string
  message: string
  type?: 'danger' | 'warning' | 'info'
  confirmText?: string
  onConfirm: () => void
}) => {
  confirmDialog.value = {
    show: true,
    title: opts.title,
    message: opts.message,
    type: opts.type ?? 'warning',
    confirmText: opts.confirmText ?? '确认',
    onConfirm: opts.onConfirm,
  }
}

const onConfirmDialog = () => {
  confirmDialog.value.onConfirm()
  confirmDialog.value.show = false
}

const apiErrorMessage = (e: any, fallback: string) => {
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d: any) => d.msg || String(d)).join('; ')
  return fallback
}

const isAdmin = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user_info') || '{}').role === 'admin'
  } catch {
    return false
  }
})

const hasReviewPerm = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user_info') || '{}')
    return (u.permissions?.elements || []).includes('element:catalog:review')
  } catch {
    return false
  }
})

const canHandleRequest = (req: any) => {
  if (req.status !== 0) return false
  if (isAdmin.value || hasReviewPerm.value) return true
  return currentUserId.value != null && req.owner_user_id === currentUserId.value
}

const canRevokeRequest = (req: any) => {
  if (req.status !== 1) return false
  if (req.access_active === false) return false
  if (isAdmin.value || hasReviewPerm.value) return true
  return currentUserId.value != null && req.owner_user_id === currentUserId.value
}

const doRevokeAccess = async (id: number) => {
  handlingId.value = id
  try {
    await axios.post(`/api/portal/catalog/access-requests/${id}/revoke-access`)
    showToast('已收回访问权限', 'success')
    await fetchRequests()
    await refreshCatalogBadge?.()
  } catch (e: any) {
    showToast(apiErrorMessage(e, '收回权限失败'), 'error')
  } finally {
    handlingId.value = null
  }
}

const revokeAccess = (id: number, userName: string) => {
  openConfirm({
    title: '收回权限',
    message: `确认收回用户「${userName}」的 API 访问权限？`,
    type: 'danger',
    confirmText: '收回',
    onConfirm: () => doRevokeAccess(id),
  })
}

const fetchRequests = async () => {
  loading.value = true
  try {
    const params: Record<string, number> = {}
    if (statusFilter.value !== '') {
      params.status = statusFilter.value as number
    }
    const res = await axios.get('/api/portal/catalog/access-requests', { params })
    requests.value = res.data
  } catch (e: any) {
    if (e.response?.status === 403) {
      router.replace('/dashboard/403')
    }
  } finally {
    loading.value = false
  }
}

const approve = async (id: number) => {
  handlingId.value = id
  try {
    await axios.post(`/api/portal/catalog/access-requests/${id}/approve`, { remark: remark.value || undefined })
    remark.value = ''
    showToast('已通过申请', 'success')
    await fetchRequests()
    await refreshCatalogBadge?.()
  } catch (e: any) {
    showToast(apiErrorMessage(e, '审批失败'), 'error')
  } finally {
    handlingId.value = null
  }
}

const doReject = async (id: number) => {
  handlingId.value = id
  try {
    await axios.post(`/api/portal/catalog/access-requests/${id}/reject`, { remark: remark.value || undefined })
    remark.value = ''
    showToast('已拒绝申请', 'success')
    await fetchRequests()
    await refreshCatalogBadge?.()
  } catch (e: any) {
    showToast(apiErrorMessage(e, '操作失败'), 'error')
  } finally {
    handlingId.value = null
  }
}

const reject = (id: number) => {
  openConfirm({
    title: '拒绝申请',
    message: '确认拒绝该权限申请？',
    type: 'warning',
    confirmText: '拒绝',
    onConfirm: () => doReject(id),
  })
}

const statusLabel = (req: any) => {
  if (req.status === 1 && req.access_active === false) return '权限已收回'
  if (req.status === 0) return '待审批'
  if (req.status === 1) return '已通过'
  if (req.status === 3) return '权限已收回'
  return '已拒绝'
}

const statusClass = (req: any) => {
  if (req.status === 1 && req.access_active === false) return 'bg-gray-100 text-gray-600'
  if (req.status === 0) return 'bg-amber-100 text-amber-800'
  if (req.status === 1) return 'bg-green-100 text-green-800'
  if (req.status === 3) return 'bg-gray-100 text-gray-600'
  return 'bg-gray-100 text-gray-600'
}

onMounted(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user_info') || '{}')
    currentUserId.value = u.user_id ?? null
  } catch { /* ignore */ }
  fetchRequests()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">目录权限审批</h1>
        <p class="text-sm text-gray-500 mt-1">审批业务方对数据产品的 API 访问申请（管理员与产品负责人）</p>
      </div>
      <select v-model="statusFilter" class="border border-gray-200 rounded-lg px-3 py-2 text-sm" @change="fetchRequests">
        <option :value="0">待审批</option>
        <option :value="1">已通过</option>
        <option :value="2">已拒绝</option>
        <option :value="3">权限已收回</option>
        <option value="">全部</option>
      </select>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">加载中...</div>
    <div v-else-if="!requests.length" class="text-center py-20 text-gray-400 bg-white rounded-xl border">
      暂无申请记录
    </div>
    <div v-else class="space-y-4">
      <div v-for="req in requests" :key="req.id" class="bg-white rounded-xl border border-gray-100 p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <router-link :to="`/dashboard/catalog/${req.product_key}`" class="font-semibold text-gray-900 hover:text-indigo-600">
                {{ req.product_name || req.product_key }}
              </router-link>
              <span :class="statusClass(req)" class="text-xs px-2 py-0.5 rounded-full">{{ statusLabel(req) }}</span>
            </div>
            <p class="text-sm text-gray-600 mt-2">
              申请人：<strong>{{ req.user_name }}</strong>
              <span class="text-gray-400 mx-2">·</span>
              {{ req.created_at }}
              <router-link
                :to="`/dashboard/users?user_id=${req.user_id}`"
                class="ml-3 text-indigo-600 hover:text-indigo-800 text-xs"
              >
                查看用户权限 →
              </router-link>
            </p>
            <p v-if="req.message" class="text-sm text-gray-500 mt-2 bg-gray-50 rounded-lg p-3">{{ req.message }}</p>
            <p v-if="req.status !== 0 && req.handler_name" class="text-sm text-gray-500 mt-2">
              审批人：<strong>{{ req.handler_name }}</strong>
              <span v-if="req.handled_at" class="text-gray-400 mx-2">·</span>
              <span v-if="req.handled_at">{{ req.handled_at }}</span>
            </p>
            <p v-if="req.handle_remark" class="text-xs text-gray-400 mt-1">
              审批备注：{{ req.handle_remark }}
            </p>
            <p v-if="req.status === 3 || (req.status === 1 && req.access_active === false)" class="text-xs text-gray-500 mt-2">
              该用户当前已无此产品的 API 访问权限，可重新发起申请。
            </p>
          </div>
          <div v-if="canHandleRequest(req)" class="flex flex-col gap-2 min-w-[200px]">
            <input v-model="remark" placeholder="审批备注（可选）" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm" />
            <div class="flex gap-2">
              <button
                :disabled="handlingId === req.id"
                class="flex-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
                @click="approve(req.id)"
              >
                通过
              </button>
              <button
                :disabled="handlingId === req.id"
                class="flex-1 px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-sm hover:bg-red-50 disabled:opacity-50"
                @click="reject(req.id)"
              >
                拒绝
              </button>
            </div>
          </div>
          <div v-else-if="canRevokeRequest(req)" class="flex flex-col gap-2 min-w-[160px]">
            <button
              :disabled="handlingId === req.id"
              class="px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-sm hover:bg-red-50 disabled:opacity-50"
              @click="revokeAccess(req.id, req.user_name)"
            >
              收回权限
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="confirmDialog.show"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :type="confirmDialog.type"
      :confirm-text="confirmDialog.confirmText"
      @confirm="onConfirmDialog"
      @cancel="confirmDialog.show = false"
    />
  </div>
</template>
