<script setup lang="ts">
import { inject } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import CatalogChangeNotificationsPanel from '@/components/catalog/CatalogChangeNotificationsPanel.vue'

const router = useRouter()
const { showToast } = useToast()
const refreshCatalogBadge = inject<(() => void) | undefined>('refreshCatalogBadge', undefined)

const onNavigateProduct = (productKey: string) => {
  router.push({ name: 'CatalogDetail', params: { key: productKey }, query: { tab: 'changes' } })
}

const onNavigateResource = (resourceKey: string) => {
  router.push({ name: 'ResourceEdit', params: { key: resourceKey }, query: { tab: 'history' } })
}
</script>

<template>
  <CatalogChangeNotificationsPanel
    :active="true"
    @read-changed="refreshCatalogBadge?.()"
    @navigate-product="onNavigateProduct"
    @navigate-resource="onNavigateResource"
    @toast="(msg, type) => showToast(msg, type || 'info')"
  />
</template>
