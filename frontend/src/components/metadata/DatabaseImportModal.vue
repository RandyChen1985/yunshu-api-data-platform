<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from '../../utils/axios'
import { 
  CircleStackIcon, TableCellsIcon, XMarkIcon, 
  ChevronRightIcon, ArrowPathIcon, CheckIcon,
  MagnifyingGlassIcon, SparklesIcon
} from '@heroicons/vue/24/outline'
import ClearableInput from '../common/ClearableInput.vue'
import LabTableExplorer from '../sqllab/LabTableExplorer.vue'

const props = defineProps<{ 
  show: boolean, 
  initialDataSource?: string,
  existingTableNames?: string[]
}>()
const emit = defineEmits<{
  close: []
  confirm: [
    | { mode: 'profile'; sourceName: string; sourceId: number; tableNames: string[] }
    | { mode: 'ddl'; sourceName: string; ddl: string }
  ]
}>()

const dataSources = ref<any[]>([])
const tables = ref<any[]>([])
const loading = ref(false)
const fetchingTables = ref(false)
const selectedSource = ref<any>(null)
const selectedTables = ref<string[]>([])
const tableSearchQuery = ref('')

const activeTab = ref<'system' | 'profile'>('system')
const tableProfiles = ref<any[]>([])
const loadingProfiles = ref(false)
const showProfileExplorer = ref(false)

const filteredTables = computed(() => {
  if (!tableSearchQuery.value) return tables.value
  const query = tableSearchQuery.value.toLowerCase()
  return tables.value.filter(t => t.name.toLowerCase().includes(query))
})

// 判断表是否已被导入
const isAlreadyImported = (tableName: string) => {
  return props.existingTableNames?.includes(tableName) || false
}

const fetchDataSources = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portal/datasource/datasources?status=active')
    const userInfoStr = localStorage.getItem('user_info')
    let allSources = []
    if (userInfoStr) {
      const user = JSON.parse(userInfoStr)
      if (user.role === 'admin') {
        allSources = res.data
      } else {
        const allowed = user.permissions?.datasources || []
        allSources = res.data.filter((ds: any) => allowed.includes(`ds:${ds.source_name}`))
      }
    }
    dataSources.value = allSources

    if (props.initialDataSource) {
      const match = allSources.find((ds: any) => ds.source_name === props.initialDataSource)
      if (match) {
        handleSourceSelect(match)
      }
    }
  } finally { loading.value = false }
}

const loadTableProfiles = async () => {
  if (!selectedSource.value) return
  loadingProfiles.value = true
  try {
    const res = await axios.get(`/api/portal/datasource/datasources/${selectedSource.value.id}/table-profiles`, {
      params: { summary: true, status: 2 },
    })
    tableProfiles.value = res.data || []
  } catch {
    tableProfiles.value = []
  } finally {
    loadingProfiles.value = false
  }
}

const handleSourceSelect = async (ds: any) => {
  selectedSource.value = ds
  selectedTables.value = []
  tableSearchQuery.value = ''
  fetchingTables.value = true
  showProfileExplorer.value = false
  tableProfiles.value = []
  activeTab.value = 'system'
  try {
    const res = await axios.post('/api/portal/meta/datasource/tables', { data_source: ds.source_name })
    const allTables: any[] = res.data.tables || []
    tables.value = allTables
    
    await loadTableProfiles()
    if (tableProfiles.value.length > 0) {
      activeTab.value = 'profile'
      showProfileExplorer.value = true
    }
  } catch (e) {
    tables.value = []
  } finally { fetchingTables.value = false }
}

const toggleTable = (tableName: string) => {
  if (isAlreadyImported(tableName)) return 
  const idx = selectedTables.value.indexOf(tableName)
  if (idx > -1) {
    selectedTables.value.splice(idx, 1)
  } else {
    selectedTables.value.push(tableName)
  }
}

const profileImportableCount = computed(() =>
  tableProfiles.value.filter(p => p.is_ignored !== 1).length,
)

const openProfileExplorer = () => {
  if (!selectedSource.value) return
  showProfileExplorer.value = true
}

const switchToProfileTab = () => {
  activeTab.value = 'profile'
  if (profileImportableCount.value > 0) {
    openProfileExplorer()
  }
}

const operableFilteredTableNames = computed(() =>
  filteredTables.value.filter(t => !isAlreadyImported(t.name)).map(t => t.name),
)

const allFilteredTablesSelected = computed(() => {
  const names = operableFilteredTableNames.value
  return names.length > 0 && names.every(n => selectedTables.value.includes(n))
})

const toggleAll = () => {
  if (activeTab.value !== 'system') return
  const operableTables = filteredTables.value.filter(t => !isAlreadyImported(t.name))
  const operableTableNames = operableTables.map(t => t.name)
  const currentlySelectedOperable = selectedTables.value.filter(name => operableTableNames.includes(name))

  if (currentlySelectedOperable.length === operableTableNames.length && operableTableNames.length > 0) {
    const idsToRemove = new Set(operableTableNames)
    selectedTables.value = selectedTables.value.filter(name => !idsToRemove.has(name))
  } else {
    const currentSet = new Set(selectedTables.value)
    operableTableNames.forEach(name => currentSet.add(name))
    selectedTables.value = Array.from(currentSet)
  }
}

const handleConfirm = async () => {
  const finalTables = selectedTables.value.filter(t => !isAlreadyImported(t))
  if (!selectedSource.value || finalTables.length === 0) return

  if (activeTab.value === 'profile') {
    emit('confirm', {
      mode: 'profile',
      sourceName: selectedSource.value.source_name,
      sourceId: selectedSource.value.id,
      tableNames: finalTables,
    })
    emit('close')
    return
  }

  loading.value = true
  try {
    let combinedDdl = ""
    for (const tableName of finalTables) {
      const res = await axios.post('/api/portal/meta/datasource/columns', {
        data_source: selectedSource.value.source_name,
        table_name: tableName,
      })
      const cols = res.data.columns
      const generatedDdl = `CREATE TABLE ${tableName} (\n` +
        cols.map((c: any) => `  ${c.name} ${c.type} COMMENT '${c.comment || ''}'`).join(',\n') +
        `\n);\n\n`
      combinedDdl += generatedDdl
    }
    emit('confirm', {
      mode: 'ddl',
      sourceName: selectedSource.value.source_name,
      ddl: combinedDdl.trim(),
    })
    emit('close')
  } finally { loading.value = false }
}

onMounted(fetchDataSources)
</script>

<template>
  <div v-if="props.show" class="fixed inset-0 z-[120] flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-3xl overflow-hidden animate-in zoom-in duration-200 flex flex-col max-h-[85vh]">
      <!-- Header -->
      <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
        <div class="flex items-center gap-4">
          <div class="p-3 bg-indigo-600 rounded-xl text-white shadow-md">
            <CircleStackIcon class="w-6 h-6" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900">从现有数据源导入</h2>
            <p class="text-xs text-gray-400 mt-0.5 uppercase tracking-widest font-bold">Pick one or more tables to analyze</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors"><XMarkIcon class="w-6 h-6" /></button>
      </div>

      <div class="flex-1 overflow-hidden grid grid-cols-12">
        <!-- Left: Sources (Hidden if initialDataSource is provided) -->
        <div v-if="!props.initialDataSource" class="col-span-5 p-6 border-r flex flex-col gap-4 bg-white overflow-y-auto custom-scrollbar">
          <label class="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">1. 选择数据源</label>
          <div 
            v-for="ds in dataSources" :key="ds.id"
            @click="handleSourceSelect(ds)"
            :class="selectedSource?.id === ds.id ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg' : 'bg-gray-50 border-gray-100 text-gray-600 hover:bg-gray-100'"
            class="p-4 rounded-xl border transition-all cursor-pointer flex justify-between items-center group"
          >
            <div class="flex items-center gap-3">
              <CircleStackIcon class="w-5 h-5 opacity-50" />
              <span class="text-sm font-bold">{{ ds.source_name }}</span>
            </div>
            <ChevronRightIcon class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        <!-- Right: Tables (Full width if no source list) -->
        <div :class="props.initialDataSource ? 'col-span-12' : 'col-span-7'" class="p-6 flex flex-col gap-4 bg-gray-50/50 overflow-y-auto custom-scrollbar">
          
          <!-- 双 Tab 切换 -->
          <div v-if="selectedSource" class="flex border-b border-gray-200 shrink-0">
            <button 
              type="button"
              :class="['px-4 py-2 text-xs font-bold transition-all border-b-2 flex items-center gap-1.5', activeTab === 'system' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-600']"
              @click="activeTab = 'system'"
            >
              物理直连导入
            </button>
            <button 
              v-if="tableProfiles.length > 0"
              type="button"
              :class="['px-4 py-2 text-xs font-bold transition-all border-b-2 flex items-center gap-1.5', activeTab === 'profile' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-600']"
              @click="switchToProfileTab"
            >
              AI 摸排资产导入
              <span class="px-1.5 py-0.5 text-[9px] bg-indigo-50 text-indigo-600 rounded-full font-bold">
                {{ profileImportableCount }}
              </span>
            </button>
          </div>

          <div v-if="activeTab === 'system'" class="flex justify-between items-center">
             <label class="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">
                {{ props.initialDataSource ? `从 ${props.initialDataSource} 选择数据表` : '选择目标表' }} ({{ selectedTables.length }})
             </label>
             <button 
               v-if="tables.length > 0"
               @click="toggleAll" 
               class="text-[10px] font-bold text-indigo-600 hover:underline px-2 py-1"
             >
               {{ allFilteredTablesSelected ? '取消全选' : '选择当前全部' }}
             </button>
          </div>

          <ClearableInput
            v-if="tables.length > 0 && activeTab === 'system'"
            v-model="tableSearchQuery"
            show-search-icon
            input-class="py-2 text-xs shadow-sm"
            placeholder="快速过滤表名..."
          />

          <div v-if="fetchingTables" class="flex-1 flex flex-col items-center justify-center text-gray-400">
            <ArrowPathIcon class="w-8 h-8 animate-spin mb-2" />
            <span class="text-xs font-bold tracking-widest uppercase">Fetching Tables...</span>
          </div>

          <template v-else-if="tables.length > 0">
            <!-- 物理直连表列表 -->
            <div v-if="activeTab === 'system'">
              <div v-if="filteredTables.length > 0" class="grid grid-cols-1 gap-2">
                <div 
                  v-for="t in filteredTables" :key="t.name"
                  @click="toggleTable(t.name)"
                  :class="[
                    selectedTables.includes(t.name) ? 'bg-white border-indigo-600 ring-1 ring-indigo-600' : 'bg-white border-gray-200 text-gray-500 hover:border-indigo-300',
                    isAlreadyImported(t.name) ? 'opacity-40 grayscale cursor-not-allowed border-gray-100 bg-gray-50 ring-0' : 'cursor-pointer'
                  ]"
                  class="p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between group shadow-sm"
                >
                  <div class="flex items-center gap-3">
                     <TableCellsIcon class="w-4 h-4 opacity-40" />
                     <span :class="selectedTables.includes(t.name) && !isAlreadyImported(t.name) ? 'text-indigo-600 font-bold' : ''">{{ t.name }}</span>
                     <span :class="t.type === 'VIEW' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'" class="text-[9px] px-1.5 py-0.5 rounded uppercase font-black ml-1 scale-90 origin-left">{{ t.type }}</span>
                     <span v-if="isAlreadyImported(t.name)" class="text-[9px] bg-gray-200 text-gray-500 px-1.5 py-0.5 rounded uppercase font-black">Already In</span>
                  </div>
                  <div v-if="selectedTables.includes(t.name)" :class="isAlreadyImported(t.name) ? 'bg-gray-300' : 'bg-indigo-600'" class="w-5 h-5 rounded-full flex items-center justify-center text-white animate-in zoom-in duration-200">
                     <CheckIcon class="w-3 h-3 stroke-[4]" />
                  </div>
                </div>
              </div>
              <div v-else class="flex-1 flex flex-col items-center justify-center py-12 text-gray-400">
                 <MagnifyingGlassIcon class="w-8 h-8 mb-2 opacity-20" />
                 <p class="text-xs font-bold uppercase tracking-widest">没有匹配的表</p>
              </div>
            </div>

            <!-- AI 摸排：复用 SQL Lab 表探索器 -->
            <div v-else-if="activeTab === 'profile'" class="flex-1 flex flex-col gap-4 min-h-0">
              <div class="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50/90 to-white p-5 shadow-sm shrink-0">
                <div class="flex items-start gap-3">
                  <div class="p-2 rounded-xl bg-indigo-600 text-white shrink-0">
                    <SparklesIcon class="w-5 h-5" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <h3 class="text-sm font-bold text-gray-900">高级表探索器</h3>
                    <p class="text-xs text-gray-500 mt-1 leading-relaxed">
                      与 SQL Lab 相同的选表体验：关键词搜索、排序、标签筛选、字段画像、数据预览，以及基于摸排画像的关联表推荐。
                    </p>
                    <button
                      type="button"
                      class="mt-3 inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md transition-all active:scale-[0.98]"
                      @click="openProfileExplorer"
                    >
                      <TableCellsIcon class="w-4 h-4" />
                      打开表探索器选表
                      <span class="opacity-80 font-medium">（{{ profileImportableCount }} 张可导入）</span>
                    </button>
                  </div>
                </div>
              </div>

              <div class="flex-1 min-h-0 flex flex-col gap-2">
                <label class="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1 shrink-0">
                  已选表 ({{ selectedTables.length }})
                </label>
                <div v-if="selectedTables.length" class="flex flex-wrap gap-2 content-start overflow-y-auto custom-scrollbar flex-1 min-h-0 p-1">
                  <button
                    v-for="name in selectedTables"
                    :key="name"
                    type="button"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono border transition-colors"
                    :class="isAlreadyImported(name)
                      ? 'bg-gray-50 border-gray-200 text-gray-400 line-through'
                      : 'bg-white border-indigo-200 text-indigo-700 hover:bg-indigo-50'"
                    :title="isAlreadyImported(name) ? '已导入，将自动跳过' : '点击移除'"
                    @click="toggleTable(name)"
                  >
                    {{ name }}
                    <XMarkIcon v-if="!isAlreadyImported(name)" class="w-3.5 h-3.5 opacity-60" />
                  </button>
                </div>
                <div v-else class="flex-1 flex flex-col items-center justify-center py-10 text-gray-400 border border-dashed border-gray-200 rounded-2xl bg-white/60">
                  <TableCellsIcon class="w-10 h-10 mb-2 opacity-20" />
                  <p class="text-xs font-bold">尚未选择表</p>
                  <p class="text-[11px] mt-1">点击上方按钮，在探索器中搜索、预览并勾选要导入的表</p>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-300 opacity-50">
             <TableCellsIcon class="w-12 h-12 mb-2" />
             <span class="text-xs font-bold uppercase tracking-widest">Select Source First</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-8 py-6 bg-gray-50 border-t flex gap-3 justify-end">
        <button @click="emit('close')" class="px-6 py-2.5 bg-white border border-gray-200 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition-all text-sm">取消</button>
        <button 
          @click="handleConfirm" :disabled="selectedTables.length === 0 || loading"
          class="px-10 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-lg transition-all active:scale-95 disabled:opacity-50 text-sm flex items-center gap-2"
        >
          <ArrowPathIcon v-if="loading" class="w-4 h-4 animate-spin" />
          <span>{{ loading ? '抓取结构中...' : (activeTab === 'profile' ? `导入摸排画像 (${selectedTables.length})` : `确认加载 (${selectedTables.length})`) }}</span>
        </button>
      </div>
    </div>

    <LabTableExplorer
      v-if="showProfileExplorer && selectedSource"
      :source-id="selectedSource.id"
      v-model="selectedTables"
      :source-name="selectedSource.source_name"
      :excluded-tables="props.existingTableNames || []"
      initial-scope="profiled"
      overlay-z-class="z-[130]"
      confirm-label="确认选表"
      selection-hint="将用于元数据导入"
      @close="showProfileExplorer = false"
    />
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }
</style>