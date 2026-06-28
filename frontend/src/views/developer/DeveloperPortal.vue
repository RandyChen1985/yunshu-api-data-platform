<template>
  <div class="p-6 max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">开发者中心 (Developer Portal)</h1>
      <p class="mt-2 text-gray-600">欢迎使用云枢数据 API 平台。本中心提供完善的 API 接入引导、SDK 示例及错误码参考。</p>
    </div>

    <!-- 导航标签 -->
    <div class="border-b border-gray-200 mb-8">
      <nav class="-mb-px flex space-x-8">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id 
              ? 'border-blue-500 text-blue-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- 动态内容区域 -->
    <div class="bg-white rounded-lg shadow-sm p-6 min-h-[600px]">
      <component :is="activeTabComponent" />
    </div>
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
