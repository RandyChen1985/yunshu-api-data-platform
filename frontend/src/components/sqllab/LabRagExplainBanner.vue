<script setup lang="ts">
import { computed } from 'vue'
import { SparklesIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  recalledContext?: any[]
}>()

const items = computed(() => props.recalledContext || [])

const metrics = computed(() => items.value.filter(i => i.type === 'metric'))
</script>

<template>
  <div v-if="items.length" class="mx-3 mb-2 p-3 rounded-xl border border-indigo-100 bg-indigo-50/40">
    <div class="flex items-center gap-2 mb-2">
      <SparklesIcon class="w-4 h-4 text-indigo-600" />
      <span class="text-[10px] font-black text-indigo-900 uppercase tracking-widest">AI 建模参考（为何选这些资产）</span>
    </div>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(item, idx) in items.slice(0, 8)"
        :key="idx"
        class="px-2.5 py-1.5 bg-white border border-indigo-100 rounded-lg text-[10px] max-w-[200px]"
      >
        <div class="font-bold text-gray-800 truncate">{{ item.name }}</div>
        <div class="text-indigo-500 uppercase text-[8px] font-black">{{ item.type }}</div>
        <div class="text-gray-500 line-clamp-2 mt-0.5">{{ item.reason || item.debug_info }}</div>
      </div>
    </div>
    <div v-if="metrics.length" class="mt-2 text-[10px] text-amber-800 bg-amber-50 border border-amber-100 rounded-lg px-2 py-1.5">
      <span class="font-bold">指标口径提示：</span>
      本次 SQL 可能涉及指标 {{ metrics.map(m => m.name).join('、') }}，请与元数据定义保持一致。
    </div>
  </div>
</template>
