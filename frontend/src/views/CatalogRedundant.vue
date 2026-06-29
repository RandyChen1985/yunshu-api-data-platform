<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { useToast } from '@/composables/useToast'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const { showToast } = useToast()
const loading = ref(true)
const items = ref<any[]>([])
const archivingKey = ref<string | null>(null)

const confirmDialog = ref({
  show: false,
  title: '',
  message: '',
  type: 'warning' as 'danger' | 'warning' | 'info',
  confirmText: '确认',
  onConfirm: () => {},
})

const statusLabel = (s: number) => {
  if (s === 1) return '已上架'
  if (s === 0) return '草稿'
  if (s === 2) return '已下线'
  return '未知'
}

const fetchItems = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portal/catalog/products/redundant')
    items.value = res.data
  } catch (e: any) {
    if (e.response?.status === 403) {
      router.replace('/dashboard/403')
      return
    }
    items.value = []
  } finally {
    loading.value = false
  }
}

const archive = (item: any, revokePermissions: boolean) => {
  confirmDialog.value = {
    show: true,
    title: '归档冗余产品',
    message: `确认归档「${item.display_name}」？该 API 已合并至「${item.host_display_name}」。归档后将从目录移除此重复产品记录。${
      item.status === 1 && revokePermissions ? ' 将同时收回该产品上的访问权限。' : ''
    }`,
    type: 'warning',
    confirmText: '确认归档',
    onConfirm: () => doArchive(item.product_key, revokePermissions),
  }
}

const doArchive = async (productKey: string, revokePermissions: boolean) => {
  archivingKey.value = productKey
  try {
    await axios.post(`/api/portal/catalog/products/${productKey}/archive-redundant`, {
      revoke_permissions: revokePermissions,
    })
    showToast('冗余产品已归档', 'success')
    await fetchItems()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '归档失败', 'error')
  } finally {
    archivingKey.value = null
  }
}

onMounted(fetchItems)
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">冗余产品清理</h1>
        <p class="text-sm text-gray-500 mt-1">
          多个 API 合并到同一产品后，原先「一资源一产品」产生的重复记录可在此归档
        </p>
      </div>
      <router-link to="/dashboard/catalog" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
        ← 返回产品目录
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">加载中...</div>
    <div v-else-if="!items.length" class="text-center py-16 text-gray-400 bg-white rounded-xl border">
      暂无冗余产品，目录数据整洁 ✓
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="item in items"
        :key="item.product_key"
        class="bg-white rounded-xl border border-amber-100 p-5"
      >
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-bold text-gray-900">{{ item.display_name }}</h3>
              <span class="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{{ statusLabel(item.status) }}</span>
            </div>
            <p class="text-sm text-gray-600 mt-2">
              API <code class="text-xs bg-gray-50 px-1 rounded">{{ item.duplicate_resource_key }}</code>
              已关联至主产品
              <router-link
                :to="`/dashboard/catalog/${item.host_product_key}`"
                class="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {{ item.host_display_name }}
              </router-link>
            </p>
            <p v-if="item.owner_name" class="text-xs text-gray-400 mt-1">负责人 {{ item.owner_name }}</p>
          </div>
          <div class="flex flex-wrap gap-2 shrink-0">
            <button
              type="button"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              :disabled="archivingKey === item.product_key"
              @click="archive(item, false)"
            >
              {{ archivingKey === item.product_key ? '处理中...' : '归档' }}
            </button>
            <button
              v-if="item.status === 1"
              type="button"
              class="px-3 py-1.5 text-sm border border-amber-200 text-amber-800 rounded-lg hover:bg-amber-50 disabled:opacity-50"
              :disabled="archivingKey === item.product_key"
              @click="archive(item, true)"
            >
              归档并收回权限
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
      @confirm="confirmDialog.onConfirm(); confirmDialog.show = false"
      @cancel="confirmDialog.show = false"
    />
  </div>
</template>
