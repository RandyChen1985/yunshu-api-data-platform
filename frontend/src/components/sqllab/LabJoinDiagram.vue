<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  joinPaths: any[]
}>()

const emit = defineEmits<{ (e: 'insert', snippet: string): void }>()

const nodes = computed(() => {
  const set = new Set<string>()
  props.joinPaths.forEach(p => {
    set.add(p.source_table)
    set.add(p.target_table)
  })
  return [...set]
})

const nodePos = computed(() => {
  const positions: Record<string, { x: number; y: number }> = {}
  const list = nodes.value
  const cols = Math.min(3, list.length)
  list.forEach((name, i) => {
    const col = i % cols
    const row = Math.floor(i / cols)
    positions[name] = { x: 40 + col * 180, y: 40 + row * 100 }
  })
  return positions
})

const edges = computed(() =>
  props.joinPaths.map(p => ({
    ...p,
    from: nodePos.value[p.source_table],
    to: nodePos.value[p.target_table],
  })).filter(e => e.from && e.to)
)
</script>

<template>
  <div v-if="joinPaths.length" class="px-3 py-2 border-b bg-slate-50">
    <div class="text-[9px] font-black text-slate-600 uppercase tracking-widest mb-2">表关联图</div>
    <div class="overflow-x-auto">
      <svg :width="Math.max(360, nodes.length * 120)" height="160" class="bg-white rounded-lg border">
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#6366f1" />
          </marker>
        </defs>
        <line
          v-for="(e, i) in edges"
          :key="'e-' + i"
          :x1="(e.from?.x ?? 0) + 70"
          :y1="(e.from?.y ?? 0) + 20"
          :x2="(e.to?.x ?? 0) + 10"
          :y2="(e.to?.y ?? 0) + 20"
          stroke="#a5b4fc"
          stroke-width="2"
          marker-end="url(#arrow)"
        />
        <g v-for="name in nodes" :key="name">
          <rect
            :x="nodePos[name]?.x ?? 0"
            :y="nodePos[name]?.y ?? 0"
            width="140"
            height="40"
            rx="8"
            fill="#eef2ff"
            stroke="#6366f1"
            stroke-width="1.5"
          />
          <text :x="(nodePos[name]?.x ?? 0) + 70" :y="(nodePos[name]?.y ?? 0) + 24" text-anchor="middle" class="text-[10px] fill-indigo-900 font-bold">
            {{ name.length > 16 ? name.slice(0, 14) + '…' : name }}
          </text>
        </g>
      </svg>
    </div>
    <div class="mt-2 space-y-1">
      <button
        v-for="(p, i) in joinPaths.slice(0, 4)"
        :key="i"
        type="button"
        class="w-full text-left text-[10px] px-2 py-1 rounded bg-white border hover:border-indigo-300 font-mono text-gray-600 truncate"
        @click="emit('insert', p.snippet)"
      >
        {{ p.source_table }} → {{ p.target_table }}: {{ p.condition }}
      </button>
    </div>
  </div>
</template>
