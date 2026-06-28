<script setup lang="ts">
import { ref } from 'vue'
import { metadataV2Api } from '../../api/metadata_v2'
import { useToast } from '../../composables/useToast'
import { 
  SparklesIcon, ArrowPathIcon, XMarkIcon, 
  BoltIcon, CheckIcon, BeakerIcon
} from '@heroicons/vue/24/outline'

const props = defineProps<{ show: boolean, datasetId: number }>()
const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const saving = ref(false)
const recommendations = ref<any[]>([])
const selectedIndices = ref<number[]>([])
const { showToast } = useToast()

const handleDiscover = async () => {
  loading.value = true
  recommendations.value = []
  selectedIndices.value = []
  try {
    const res = await metadataV2Api.recommendMetrics(props.datasetId)
    recommendations.value = res.data.data
    // 默认全选
    selectedIndices.value = recommendations.value.map((_, i) => i)
  } catch (e) {
    showToast('智能推荐失败', 'error')
  } finally {
    loading.value = false
  }
}

const toggleSelection = (idx: number) => {
  const i = selectedIndices.value.indexOf(idx)
  if (i > -1) selectedIndices.value.splice(i, 1)
  else selectedIndices.value.push(idx)
}

const handleSave = async () => {
  const targets = recommendations.value.filter((_, i) => selectedIndices.value.includes(i))
  if (targets.length === 0) return
  
  saving.value = true
  try {
    for (const m of targets) {
      await metadataV2Api.createMetric(props.datasetId, m)
    }
    showToast(`成功导入 ${targets.length} 个指标`, 'success')
    emit('saved')
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[250] flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col overflow-hidden animate-in zoom-in duration-300">
      <!-- Header -->
      <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
        <div class="flex items-center gap-4">
          <div class="p-3 bg-amber-500 rounded-2xl text-white shadow-lg"><SparklesIcon class="w-6 h-6" /></div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 tracking-tight">AI 智能发现指标</h2>
            <p class="text-xs text-gray-400 mt-0.5 font-bold uppercase tracking-widest">Automatic Business Metric Extraction</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600"><XMarkIcon class="w-7 h-7" /></button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-8 bg-gray-50/30 custom-scrollbar">
        <div v-if="recommendations.length === 0 && !loading" class="h-full flex flex-col items-center justify-center space-y-6">
           <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-xl border border-gray-100">
              <BeakerIcon class="w-12 h-12 text-amber-500 animate-pulse" />
           </div>
           <div class="text-center">
              <h3 class="text-lg font-bold text-gray-900">挖掘业务价值</h3>
              <p class="text-sm text-gray-400 mt-1">AI 将深入分析该数据集的表结构，为您推荐最有业务价值的分析指标</p>
           </div>
           <button @click="handleDiscover" class="px-8 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-bold shadow-lg transition-all active:scale-95 flex items-center gap-2 text-sm">
              <SparklesIcon class="w-5 h-5" /> 开始智能扫描
           </button>
        </div>

        <div v-else-if="loading" class="h-full flex flex-col items-center justify-center space-y-4">
           <ArrowPathIcon class="w-12 h-12 text-amber-500 animate-spin" />
           <p class="text-sm font-black text-amber-600 uppercase tracking-widest">Analyzing Schema...</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div 
             v-for="(m, idx) in recommendations" :key="idx"
             @click="toggleSelection(idx)"
             :class="selectedIndices.includes(idx) ? 'border-amber-500 bg-white ring-2 ring-amber-500/20' : 'border-gray-200 bg-white opacity-60 hover:opacity-100'"
             class="p-6 rounded-2xl border transition-all cursor-pointer group relative"
           >
              <div class="flex justify-between items-start mb-4">
                 <div class="flex items-center gap-3">
                    <div :class="selectedIndices.includes(idx) ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-400'" class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors">
                       <BoltIcon class="w-5 h-5" />
                    </div>
                    <div>
                       <h4 class="font-bold text-gray-900">{{ m.display_name }}</h4>
                       <p class="text-[10px] font-mono text-gray-400 uppercase tracking-widest">{{ m.name }}</p>
                    </div>
                 </div>
                 <div v-if="selectedIndices.includes(idx)" class="w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center text-white shadow-lg">
                    <CheckIcon class="w-4 h-4 stroke-[4]" />
                 </div>
              </div>
              <div class="bg-gray-900 rounded-xl p-3 mb-3">
                 <code class="text-[10px] text-amber-400 font-mono break-all">{{ m.calculation_logic }}</code>
              </div>
              <p class="text-xs text-gray-500 line-clamp-2 leading-relaxed italic">"{{ m.description }}"</p>
           </div>
        </div>
      </div>

      <!-- Footer -->
      <div v-if="recommendations.length > 0" class="px-8 py-6 bg-gray-50 border-t flex justify-end gap-4">
         <button @click="emit('close')" class="px-6 py-2.5 bg-white border border-gray-200 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition-all text-sm">取消</button>
         <button @click="handleSave" :disabled="selectedIndices.length === 0 || saving" class="px-10 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-bold shadow-lg shadow-amber-100 transition-all active:scale-95 disabled:opacity-50 text-sm flex items-center gap-2">
            <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
            <span>确认导入 {{ selectedIndices.length }} 个指标</span>
         </button>
      </div>
    </div>
  </div>
</template>
