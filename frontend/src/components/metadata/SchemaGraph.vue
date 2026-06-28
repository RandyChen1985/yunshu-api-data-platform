<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { 
  TableCellsIcon, MagnifyingGlassPlusIcon, MagnifyingGlassMinusIcon, 
  ArrowsPointingOutIcon, HandRaisedIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  datasetId: number
  tables: any[]
  relationships: any[]
}>()

// --- 画布状态管理 ---
const viewport = ref({ x: 0, y: 0, scale: 0.8 })
const nodePositions = ref<Record<number, { x: number, y: number }>>({})
const isPanning = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// --- 初始化节点位置 ---
const initPositions = () => {
  const cols = Math.ceil(Math.sqrt(props.tables.length || 1))
  const newPositions: Record<number, { x: number, y: number }> = {}
  
  props.tables.forEach((t, i) => {
    newPositions[t.id] = {
      x: (i % cols) * 400 + 100,
      y: Math.floor(i / cols) * 280 + 100
    }
  })
  nodePositions.value = newPositions
  
  // 居中画布 (简单逻辑)
  viewport.value = { x: 50, y: 50, scale: 0.75 }
}

// 监听 tables 变化重新初始化
watch(() => props.tables, initPositions, { deep: true })

// --- 节点拖拽逻辑 ---
const activeNodeId = ref<number | null>(null)
const nodeDragStart = ref({ x: 0, y: 0 })

const onNodeMouseDown = (e: MouseEvent, nodeId: number) => {
  e.stopPropagation()
  if (!nodePositions.value[nodeId]) return
  activeNodeId.value = nodeId
  nodeDragStart.value = { 
    x: e.clientX - nodePositions.value[nodeId].x * viewport.value.scale, 
    y: e.clientY - nodePositions.value[nodeId].y * viewport.value.scale 
  }
}

// --- 画布平移逻辑 ---
const onBgMouseDown = (e: MouseEvent) => {
  isPanning.value = true
  dragStart.value = { x: e.clientX - viewport.value.x, y: e.clientY - viewport.value.y }
}

const onMouseMove = (e: MouseEvent) => {
  if (activeNodeId.value !== null) {
    // 拖动节点
    nodePositions.value[activeNodeId.value] = {
      x: (e.clientX - nodeDragStart.value.x) / viewport.value.scale,
      y: (e.clientY - nodeDragStart.value.y) / viewport.value.scale
    }
  } else if (isPanning.value) {
    // 平移画布
    viewport.value.x = e.clientX - dragStart.value.x
    viewport.value.y = e.clientY - dragStart.value.y
  }
}

const onMouseUp = () => {
  isPanning.value = false
  activeNodeId.value = null
}

// --- 缩放逻辑 ---
const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.min(Math.max(viewport.value.scale * delta, 0.2), 2)
  
  // 以鼠标中心缩放 (简化版)
  viewport.value.scale = newScale
}

const zoomIn = () => viewport.value.scale = Math.min(viewport.value.scale + 0.1, 2)
const zoomOut = () => viewport.value.scale = Math.max(viewport.value.scale - 0.1, 0.2)
const resetView = () => viewport.value = { x: 50, y: 50, scale: 0.75 }

// --- 连线计算 ---
interface Edge {
  id: string | number
  path: string
  labelX: number
  labelY: number
  type: string
  isSelf: boolean
}

const edges = computed<Edge[]>(() => {
  if (!props.relationships || !props.tables.length) return []
  
  const results: Edge[] = []
  props.relationships.forEach(rel => {
    const sId = Number(rel.source_table_id || rel.source_id)
    const tId = Number(rel.target_table_id || rel.target_id)
    
    const posS = nodePositions.value[sId]
    const posT = nodePositions.value[tId]
    
    if (posS && posT) {
      const cardWidth = 208
      const cardHeight = 90
      const isSelf = sId === tId
      
      let path = ''
      let lx = 0, ly = 0

      if (isSelf) {
        const x = posS.x + cardWidth / 2
        const y = posS.y
        path = `M ${x-20} ${y} C ${x-50} ${y-60}, ${x+50} ${y-60}, ${x+20} ${y}`
        lx = x
        ly = y - 45
      } else {
        const sourceOnLeft = posS.x + cardWidth < posT.x
        const x1 = sourceOnLeft ? posS.x + cardWidth : posS.x
        const y1 = posS.y + cardHeight / 2
        const x2 = sourceOnLeft ? posT.x : posT.x + cardWidth
        const y2 = posT.y + cardHeight / 2
        
        const cp1x = x1 + (sourceOnLeft ? 50 : -50)
        const cp2x = x2 + (sourceOnLeft ? -50 : 50)
        path = `M ${x1} ${y1} C ${cp1x} ${y1}, ${cp2x} ${y2}, ${x2} ${y2}`
        
        lx = (x1 + x2) / 2
        ly = (y1 + y2) / 2
      }

      results.push({
        id: rel.id || `${sId}-${tId}`,
        path,
        labelX: lx,
        labelY: ly,
        isSelf,
        type: rel.join_type || 'JOIN'
      })
    }
  })
  return results
})

onMounted(() => {
  initPositions()
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<template>
  <div 
    class="relative bg-slate-50 rounded-3xl border border-gray-200 overflow-hidden min-h-[750px] select-none shadow-inner cursor-grab active:cursor-grabbing"
    @mousedown="onBgMouseDown"
    @wheel="onWheel"
  >
    <!-- Grid Background (Follows Pan/Zoom) -->
    <div 
      class="absolute inset-0 opacity-[0.05]" 
      :style="{ 
        backgroundImage: 'radial-gradient(#4f46e5 1.5px, transparent 1px)', 
        backgroundSize: `${40 * viewport.scale}px ${40 * viewport.scale}px`,
        backgroundPosition: `${viewport.x}px ${viewport.y}px`
      }"
    ></div>

    <!-- Transform Layer -->
    <div 
      class="absolute inset-0 origin-top-left transition-transform duration-75 ease-out"
      :style="{ transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.scale})` }"
    >
      <!-- SVG Layer (Edges) -->
      <svg class="absolute inset-0 w-[5000px] h-[5000px] pointer-events-none z-0">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orientation="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#4f46e5" />
          </marker>
        </defs>
        
        <g v-for="edge in edges" :key="edge.id">
          <path :d="edge.path" fill="none" stroke="#4f46e5" stroke-width="4" class="opacity-5" />
          <path :d="edge.path" fill="none" stroke="#4f46e5" stroke-width="2" :marker-end="edge.isSelf ? '' : 'url(#arrowhead)'" class="opacity-40" />
          <path :d="edge.path" fill="none" stroke="white" stroke-width="1.5" stroke-dasharray="10, 100" class="flowing-light" />
          
          <foreignObject :x="edge.labelX - 30" :y="edge.labelY - 10" width="60" height="20">
             <div class="flex justify-center items-center h-full">
                <span class="bg-indigo-600 text-white text-[7px] font-black px-1.5 py-0.5 rounded shadow uppercase tracking-tighter">
                  {{ edge.type }}
                </span>
             </div>
          </foreignObject>
        </g>
      </svg>

      <!-- Nodes Layer -->
      <div 
        v-for="table in props.tables" 
        :key="table.id"
        :style="{ left: `${nodePositions[table.id]?.x}px`, top: `${nodePositions[table.id]?.y}px` }"
        @mousedown="onNodeMouseDown($event, table.id)"
        class="absolute w-52 bg-white rounded-2xl border-2 shadow-sm p-4 hover:shadow-xl transition-shadow z-10 cursor-move group"
        :class="activeNodeId === table.id ? 'border-indigo-600 ring-4 ring-indigo-500/10' : 'border-gray-100 hover:border-indigo-400'"
      >
         <div class="flex items-start gap-3">
            <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-all">
               <TableCellsIcon class="w-4 h-4" />
            </div>
            <div class="flex-1 min-w-0">
               <h4 class="text-[10px] font-black text-gray-900 truncate uppercase tracking-tighter">{{ table.physical_name }}</h4>
               <p class="text-[9px] text-gray-400 font-bold truncate">{{ table.term }}</p>
            </div>
         </div>
         <div class="mt-3 pt-2 border-t border-gray-50 flex justify-between items-center text-[8px] font-black text-gray-300 uppercase">
            <span>{{ table.columns?.length || 0 }} Fields</span>
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
         </div>
      </div>
    </div>

    <!-- Controls Panel (Moved to top-right) -->
    <div class="absolute top-6 right-6 z-30 flex items-center gap-2">
       <div class="bg-white/90 backdrop-blur-md p-1 rounded-xl border border-gray-200 shadow-xl flex items-center gap-1">
          <button @click="zoomIn" title="放大" class="p-2 hover:bg-indigo-50 text-gray-600 hover:text-indigo-600 rounded-lg transition-all"><MagnifyingGlassPlusIcon class="w-5 h-5" /></button>
          <div class="w-px h-4 bg-gray-100 mx-1"></div>
          <button @click="zoomOut" title="缩小" class="p-2 hover:bg-indigo-50 text-gray-600 hover:text-indigo-600 rounded-lg transition-all"><MagnifyingGlassMinusIcon class="w-5 h-5" /></button>
          <div class="w-px h-4 bg-gray-100 mx-1"></div>
          <button @click="resetView" title="重置视角" class="p-2 hover:bg-indigo-50 text-gray-600 hover:text-indigo-600 rounded-lg transition-all"><ArrowsPointingOutIcon class="w-5 h-5" /></button>
       </div>
    </div>

    <!-- Hint -->
    <div class="absolute bottom-6 left-6 z-30 bg-gray-900/10 backdrop-blur-sm px-3 py-1.5 rounded-full border border-gray-200/20">
       <div class="flex items-center gap-2 text-[9px] font-black text-gray-600 uppercase tracking-widest">
          <HandRaisedIcon class="w-3 h-3" />
          <span>滚轮缩放 • 右键/左键背景平移 • 拖动卡片调整位置</span>
       </div>
    </div>
  </div>
</template>

<style scoped>
.flowing-light {
  animation: flow 3s linear infinite;
  filter: blur(1px);
}
@keyframes flow {
  from { stroke-dashoffset: 110; }
  to { stroke-dashoffset: 0; }
}
</style>

<style scoped>
.absolute {
  animation: nodeFadeIn 0.5s ease-out backwards;
}
.flowing-light {
  animation: flow 3s linear infinite;
  filter: blur(1px);
}
@keyframes flow {
  from { stroke-dashoffset: 110; }
  to { stroke-dashoffset: 0; }
}
@keyframes nodeFadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
</style>