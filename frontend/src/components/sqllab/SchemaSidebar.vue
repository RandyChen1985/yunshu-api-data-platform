<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { TableCellsIcon, ChevronRightIcon, ChevronDownIcon, CubeIcon, SparklesIcon, EyeIcon, CommandLineIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  tables: any[]
  loading: boolean
  modelValue: string[] // selectedTables
  collapsed: boolean
  flashTitle: boolean
  autoContext?: boolean 
  columnsCache?: Record<string, {name: string, type: string}[]>
  showAi?: boolean
  isAdmin?: boolean
  aiLogs?: {timestamp: number, type: 'info' | 'error' | 'success', msg: string}[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
  (e: 'update:autoContext', value: boolean): void 
  (e: 'refresh'): void
  (e: 'table-click', table: string): void
  (e: 'table-dblclick', table: string): void
  (e: 'fetch-columns', table: string): void
  (e: 'column-dblclick', column: string): void
  (e: 'table-ai', table: string): void
  (e: 'clear-logs'): void
}>()

const activeTab = ref<'tables' | 'debug'>('tables')
const logContainerRef = ref<HTMLElement | null>(null)

// Auto scroll to bottom when new logs arrive
watch(() => props.aiLogs?.length, () => {
  if (activeTab.value === 'debug') {
    nextTick(() => {
      if (logContainerRef.value) {
        logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
      }
    })
  }
})

const formatTime = (ts: number) => {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

const search = ref('')
const expandedTables = ref<string[]>([]) 

const filteredTables = computed(() => {
  if (!search.value) return props.tables
  const query = search.value.toLowerCase()
  return props.tables.filter(t => (typeof t === 'string' ? t : t.name).toLowerCase().includes(query))
})

const handleTableDblClick = (table: string) => {
  emit('table-dblclick', table)
}

const toggleExpand = (table: string, event: Event) => {
  event.stopPropagation()
  const idx = expandedTables.value.indexOf(table)
  if (idx > -1) {
    expandedTables.value.splice(idx, 1)
  } else {
    expandedTables.value.push(table)
    if (!props.columnsCache?.[table]) {
      emit('fetch-columns', table)
    }
  }
}

const isExpanded = (table: string) => expandedTables.value.includes(table)

const handleColumnDblClick = (colName: string) => {
  emit('column-dblclick', colName)
}

const handleDragStart = (event: DragEvent, name: string) => {
  if (event.dataTransfer) {
    // 使用自定义类型防止浏览器默认的 text 插入逻辑触发，从而避免重复
    event.dataTransfer.setData('application/x-sqllab-item', name)
    event.dataTransfer.dropEffect = 'copy'
  }
}
</script>

<template>
  <div :class="collapsed ? 'lg:w-0 opacity-0 invisible' : 'lg:w-64 opacity-100 visible'" 
    class="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden transition-all duration-300 relative">
    <div class="h-full flex flex-col min-w-[256px]">
      <!-- Tab Switcher -->
      <div class="flex border-b bg-gray-100/50">
        <button 
          @click="activeTab = 'tables'"
          class="flex-1 py-2 text-[10px] font-black uppercase tracking-widest transition-all border-b-2"
          :class="activeTab === 'tables' ? 'bg-white border-blue-600 text-blue-600' : 'text-gray-400 border-transparent hover:text-gray-600'"
        >
          <div class="flex items-center justify-center gap-1.5">
            <TableCellsIcon class="w-3 h-3" /> 数据表
          </div>
        </button>
        <button 
          v-if="isAdmin"
          @click="activeTab = 'debug'"
          class="flex-1 py-2 text-[10px] font-black uppercase tracking-widest transition-all border-b-2 relative"
          :class="activeTab === 'debug' ? 'bg-white border-indigo-600 text-indigo-600' : 'text-gray-400 border-transparent hover:text-gray-600'"
        >
          <div class="flex items-center justify-center gap-1.5">
            <CommandLineIcon class="w-3 h-3" /> 调试日志
            <span v-if="aiLogs?.length" class="absolute top-1.5 right-2 w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></span>
          </div>
        </button>
      </div>

      <template v-if="activeTab === 'tables'">
        <div class="p-3 border-b bg-gray-50 flex items-center justify-between transition-colors duration-500" :class="flashTitle ? 'bg-indigo-100' : ''">
          <div class="flex items-center gap-2">
            <!-- Checkbox only visible when autoContext is OFF -->
            <input 
              v-if="!autoContext"
              type="checkbox" 
              :checked="modelValue.length === tables.length && tables.length > 0"
              :indeterminate="modelValue.length > 0 && modelValue.length < tables.length"
              @change="(e) => {
                const checked = (e.target as HTMLInputElement).checked;
                emit('update:modelValue', checked ? tables.map(t => typeof t === 'string' ? t : t.name) : []);
              }"
              class="h-3.5 w-3.5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer animate-in zoom-in duration-200"
              title="全选/取消全选"
            />
            <span class="text-xs font-bold uppercase tracking-wider transition-colors duration-500" :class="flashTitle ? 'text-indigo-600' : 'text-gray-500'">库表资产</span>
            <span class="ml-0.5 px-1.5 py-0.5 bg-gray-200 text-gray-500 rounded text-[10px] font-bold">{{ filteredTables.length }}</span>
          </div>
          <button @click="$emit('refresh')" class="text-gray-400 hover:text-blue-600">
            <svg class="w-3.5 h-3.5" :class="loading ? 'animate-spin' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          </button>
        </div>
        
        <div class="p-2 border-b">
          <input v-model="search" placeholder="搜索资产..." class="w-full px-2 py-1 text-xs border-none bg-gray-100 rounded focus:ring-1 focus:ring-blue-500" />
        </div>
        <div class="flex-1 overflow-y-auto p-1 custom-scrollbar">
          <div v-if="loading" class="p-4 text-center text-gray-400 text-xs italic">资源扫描中...</div>
          <div v-else-if="filteredTables.length === 0" class="p-4 text-center text-gray-400 text-xs">无匹配资产</div>
          
          <div v-for="t in filteredTables" :key="typeof t === 'string' ? t : t.name">
            <div 
              @click="toggleExpand(typeof t === 'string' ? t : t.name, $event)" 
              @dblclick="handleTableDblClick(typeof t === 'string' ? t : t.name)"
              draggable="true"
              @dragstart="handleDragStart($event, typeof t === 'string' ? t : t.name)"
              class="px-3 py-2 text-xs text-gray-700 hover:bg-blue-50 hover:text-blue-700 rounded cursor-pointer transition-colors flex items-center group justify-between"
              :class="isExpanded(typeof t === 'string' ? t : t.name) ? 'bg-blue-50/50' : ''">
              <div class="flex items-center overflow-hidden flex-1">
                <!-- Checkbox only visible when autoContext is OFF -->
                <input 
                  v-if="!autoContext"
                  type="checkbox" 
                  :checked="modelValue.includes(typeof t === 'string' ? t : t.name)"
                  @change="(e) => {
                    const checked = (e.target as HTMLInputElement).checked;
                    const name = typeof t === 'string' ? t : t.name;
                    const newVal = checked ? [...modelValue, name] : modelValue.filter(x => x !== name);
                    emit('update:modelValue', newVal);
                  }"
                  @click.stop
                  class="mr-2 h-3.5 w-3.5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 animate-in zoom-in duration-200"
                />
                <TableCellsIcon class="w-3 h-3 mr-1.5" :class="modelValue.includes(typeof t === 'string' ? t : t.name) ? 'text-blue-500' : 'text-gray-400'" />
                <span class="truncate font-medium flex items-center gap-1.5" :class="modelValue.includes(typeof t === 'string' ? t : t.name) ? 'text-blue-700 font-bold' : ''" :title="typeof t === 'string' ? t : t.name">
                  {{ typeof t === 'string' ? t : t.name }}
                  <span v-if="typeof t !== 'string'" :class="t.type === 'VIEW' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'" class="text-[8px] px-1 py-0.5 rounded leading-none scale-90 font-black">
                    {{ t.type }}
                  </span>
                </span>
              </div>
              <div class="flex items-center ml-1">
                 <button 
                   @click.stop="emit('table-click', typeof t === 'string' ? t : t.name)" 
                   class="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-all opacity-0 group-hover:opacity-100 mr-0.5"
                   title="查看资产画像"
                 >
                   <EyeIcon class="w-3.5 h-3.5" />
                 </button>
                 <button 
                   v-if="showAi"
                   @click.stop="emit('table-ai', typeof t === 'string' ? t : t.name)" 
                   class="p-1 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded transition-all opacity-0 group-hover:opacity-100 mr-1"
                   title="针对该表进行 AI 建模"
                 >
                   <SparklesIcon class="w-3.5 h-3.5" />
                 </button>
                 <component :is="isExpanded(typeof t === 'string' ? t : t.name) ? ChevronDownIcon : ChevronRightIcon" class="w-3 h-3 text-gray-400" />
              </div>
            </div>
            
            <!-- Columns Tree -->
            <div v-if="isExpanded(typeof t === 'string' ? t : t.name)" class="pl-4 border-l border-gray-100 ml-3 mb-1 max-h-96 overflow-y-auto custom-scrollbar">
               <div v-if="!columnsCache?.[typeof t === 'string' ? t : t.name]" class="py-1 text-[10px] text-gray-400 italic pl-4">读取 Schema...</div>
               <div v-else v-for="col in columnsCache[typeof t === 'string' ? t : t.name]" :key="col.name" 
                  @dblclick.stop="handleColumnDblClick(col.name)"
                  draggable="true"
                  @dragstart.stop="handleDragStart($event, col.name)"
                  class="flex items-center py-1 pl-2 pr-2 hover:bg-gray-50 cursor-pointer group/col rounded">
                  <CubeIcon class="w-2.5 h-2.5 mr-1.5 text-gray-300 group-hover/col:text-indigo-400" />
                  <span class="text-[10px] text-gray-500 group-hover/col:text-indigo-600 font-mono truncate mr-1">{{ col.name }}</span>
                  <span class="text-[9px] text-gray-300 group-hover/col:text-indigo-300 ml-auto uppercase">{{ col.type }}</span>
               </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Debug Logs Tab -->
      <template v-else>
        <div class="p-3 border-b bg-gray-900 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <CommandLineIcon class="w-3.5 h-3.5 text-green-400" />
            <span class="text-xs font-bold text-gray-100 uppercase tracking-wider">AI 核心日志</span>
          </div>
          <button @click="emit('clear-logs')" class="p-1 text-gray-500 hover:text-red-400 transition-colors">
            <TrashIcon class="w-3.5 h-3.5" />
          </button>
        </div>
        <div ref="logContainerRef" class="flex-1 overflow-y-auto bg-black p-3 font-mono custom-scrollbar">
          <div v-if="!aiLogs?.length" class="text-gray-600 text-[10px] italic">等待 AI 任务触发...</div>
          <div v-for="(log, idx) in aiLogs" :key="idx" class="mb-3 animate-in slide-in-from-left duration-200">
            <div class="flex items-start gap-2">
              <span class="text-[9px] text-gray-500 flex-shrink-0 whitespace-nowrap mt-0.5">{{ formatTime(log.timestamp) }}</span>
              <div class="flex-1">
                <span 
                  class="px-1.5 py-0.5 rounded-[4px] text-[8px] font-black uppercase tracking-tighter mr-1.5"
                  :class="{
                    'bg-blue-900/50 text-blue-400 border border-blue-800/50': log.type === 'info',
                    'bg-red-900/50 text-red-400 border border-red-800/50': log.type === 'error',
                    'bg-green-900/50 text-green-400 border border-green-800/50': log.type === 'success'
                  }"
                >{{ log.type }}</span>
                <span 
                  class="text-[10px] break-words leading-relaxed"
                  :class="{
                    'text-gray-300': log.type === 'info',
                    'text-red-300': log.type === 'error',
                    'text-green-300': log.type === 'success'
                  }"
                >{{ log.msg }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="p-2 border-t bg-gray-900/90 text-[9px] text-gray-500 text-center font-mono">
          INTERNAL ENGINE DEBUG MODE V2
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>