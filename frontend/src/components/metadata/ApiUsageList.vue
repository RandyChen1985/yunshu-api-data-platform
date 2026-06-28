<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { metadataV2Api } from '../../api/metadata_v2'
import {
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
const props = defineProps<{ datasetId: number }>()
const usageList = ref<any[]>([])
const loading = ref(false)

const fetchUsage = async () => {
  loading.value = true
  try {
    const res = await metadataV2Api.getDatasetUsage(props.datasetId)
    usageList.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchUsage)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center px-1">
      <div>
        <h3 class="text-xl font-bold text-gray-900 tracking-tight">关联 API 接口 (Impact Analysis)</h3>
        <p class="text-xs text-gray-500 mt-1">识别正在使用此数据集内表的业务接口，辅助评估变更影响</p>
      </div>
    </div>

    <div v-if="loading" class="py-20 text-center text-gray-400">
       <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
       <p class="text-xs font-bold uppercase tracking-widest">Scanning Resources...</p>
    </div>

    <div v-else-if="usageList.length === 0" class="py-32 text-center bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">
       <div class="text-5xl mb-4 grayscale opacity-20">📡</div>
       <p class="text-gray-400 font-bold">暂无关联接口</p>
       <p class="text-xs text-gray-400/60 mt-2">该数据集中的表尚未被任何已定义的 API 资源引用</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
       <div v-for="item in usageList" :key="item.id" class="bg-white border border-gray-200 p-5 rounded-xl hover:shadow-md transition-all group flex items-center justify-between">
          <div class="flex items-center gap-5">
             <div class="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <RocketLaunchIcon class="w-6 h-6" />
             </div>
             <div>
                <div class="flex items-center gap-3">
                   <h4 class="font-bold text-gray-900">{{ item.term }}</h4>
                   <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] font-mono rounded uppercase">/api/v1/{{ item.name }}</span>
                </div>
                <div class="flex items-center gap-4 mt-2 text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                   <span class="flex items-center gap-1"><UserIcon class="w-3 h-3" /> {{ item.creator }}</span>
                   <span class="flex items-center gap-1"><ClockIcon class="w-3 h-3" /> {{ new Date(item.updated_at).toLocaleDateString() }}</span>
                   <span :class="item.status === 'active' ? 'text-emerald-500' : 'text-amber-500'">● {{ item.status }}</span>
                </div>
             </div>
          </div>
          
          <div class="flex items-center gap-4">
             <div class="text-right hidden sm:block">
                <p class="text-[10px] text-gray-400 font-bold uppercase">Data Source</p>
                <p class="text-xs font-mono text-gray-600">{{ item.data_source }}</p>
             </div>
             <button class="p-2 text-gray-300 hover:text-indigo-600 transition-colors">
                <ChevronRightIcon class="w-5 h-5" />
             </button>
          </div>
       </div>
    </div>
  </div>
</template>
