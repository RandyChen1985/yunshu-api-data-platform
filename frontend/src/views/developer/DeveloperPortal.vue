<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">开发者中心 (Developer Portal)</h1>
      <p class="text-sm text-gray-500 mt-1">欢迎使用南孜数据 API 平台。本中心提供完善的 API 接入引导、SDK 示例及错误码参考。</p>
    </div>

    <div class="flex gap-2 border-b border-gray-200 overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="activeTab === tab.id ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        class="px-4 py-2 border-b-2 text-sm font-medium whitespace-nowrap"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <component :is="activeTabComponent" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'

const tabs = [
  { id: 'getting-started', name: '快速入门' },
  { id: 'python-sdk', name: 'Python SDK' },
  { id: 'java-sdk', name: 'Java SDK' },
  { id: 'error-codes', name: '错误码字典' },
  { id: 'auth-guide', name: '认证授权' }
]

const activeTab = ref('getting-started')

const activeTabComponent = computed(() => {
  switch (activeTab.value) {
    case 'getting-started':
      return defineAsyncComponent(() => import('./sections/GettingStarted.vue'))
    case 'python-sdk':
      return defineAsyncComponent(() => import('./sections/PythonSDK.vue'))
    case 'java-sdk':
      return defineAsyncComponent(() => import('./sections/JavaSDK.vue'))
    case 'error-codes':
      return defineAsyncComponent(() => import('./sections/ErrorCodes.vue'))
    case 'auth-guide':
      return defineAsyncComponent(() => import('./sections/AuthGuide.vue'))
    default:
      return null
  }
})
</script>
