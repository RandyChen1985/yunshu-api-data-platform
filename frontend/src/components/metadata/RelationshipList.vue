<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { metadataV2Api } from '../../api/metadata_v2'
import request from '../../utils/axios'
import { 
  PlusIcon, TrashIcon, XMarkIcon, ChevronRightIcon,
  ShareIcon, SparklesIcon, ArrowPathIcon, CheckIcon, UserIcon, PencilSquareIcon
} from '@heroicons/vue/24/outline'
import { useToast } from '../../composables/useToast'

const props = defineProps<{
  datasetId: number
  tables: any[]
}>()

const emit = defineEmits(['saved'])

// 权限检查辅助函数
const hasPerm = (code: string) => {
  const userInfoStr = localStorage.getItem('user_info')
  if (!userInfoStr) return false
  const user = JSON.parse(userInfoStr)
  if (user.role === 'admin') return true
  const perms = user.permissions?.elements || []
  return perms.includes(code)
}

const relationships = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const isAiEnabled = ref(true)
const recommending = ref(false)
const showRecommendModal = ref(false)
const recommendedRels = ref<any[]>([])
const dismissAiWarning = ref(false)
const { showToast } = useToast()

const checkAiStatus = async () => {
  try {
    const res = await request.get('/api/portal/system/config/ai')
    isAiEnabled.value = String(res.data.enabled).toLowerCase() === 'true'
  } catch (e) {
    isAiEnabled.value = false
  }
}

// Delete State
const showDeleteConfirm = ref(false)
const deletingRelId = ref<number | null>(null)

const form = ref({
  id: undefined as number | undefined,
  source_table_id: 0,
  target_table_id: 0,
  join_condition: '',
  join_type: 'LEFT JOIN',
  description: ''
})

const sourceField = ref('')
const targetField = ref('')

const openCreate = () => {
  editingId.value = null
  form.value = {
    id: undefined,
    source_table_id: 0,
    target_table_id: 0,
    join_condition: '',
    join_type: 'LEFT JOIN',
    description: ''
  }
  sourceField.value = ''
  targetField.value = ''
  showModal.value = true
}

const openEdit = (r: any) => {
  editingId.value = r.id
  form.value = {
    id: r.id,
    source_table_id: r.source_table_id,
    target_table_id: r.target_table_id,
    join_condition: r.join_condition,
    join_type: r.join_type,
    description: r.description
  }
  
  // 尝试解析 join_condition 以回填下拉框 (格式: table1.field1 = table2.field2)
  try {
    const parts = r.join_condition.split('=').map((s: string) => s.trim())
    if (parts.length === 2) {
      const leftPart = parts[0].split('.')
      const rightPart = parts[1].split('.')
      
      // 只有当格式匹配 table.field 时才回填
      if (leftPart.length === 2) sourceField.value = leftPart[1]
      if (rightPart.length === 2) targetField.value = rightPart[1]
    }
  } catch (e) {
    console.warn('Failed to parse join condition for fields', e)
    sourceField.value = ''
    targetField.value = ''
  }
  
  showModal.value = true
}

const sourceColumns = computed(() => {
  const table = props.tables.find(t => t.id === form.value.source_table_id)
  return table ? (table.columns || []) : []
})

const targetColumns = computed(() => {
  const table = props.tables.find(t => t.id === form.value.target_table_id)
  return table ? (table.columns || []) : []
})

const applyJoinCondition = () => {
  if (sourceField.value && targetField.value) {
    const sourceTable = props.tables.find(t => t.id === form.value.source_table_id)
    const targetTable = props.tables.find(t => t.id === form.value.target_table_id)
    if (sourceTable && targetTable) {
      form.value.join_condition = `${sourceTable.physical_name}.${sourceField.value} = ${targetTable.physical_name}.${targetField.value}`
    }
  }
}

const fetchRelationships = async () => {
  loading.value = true
  try {
    const res = await metadataV2Api.getDataset(props.datasetId)
    // Extract from res.data
    relationships.value = res.data.relationships || []
  } catch (e) {
    console.error('Failed to fetch relationships', e)
  } finally {
    loading.value = false
  }
}

const handleRecommend = async () => {
  if (!isAiEnabled.value) return
  recommending.value = true
  try {
    const res = await metadataV2Api.recommendRelationships(props.datasetId)
    recommendedRels.value = (res.data.data || []).map(r => ({
      ...r,
      selected: true,
      // Map table names back to IDs for saving
      source_table_id: props.tables.find(t => t.physical_name === r.source_table)?.id,
      target_table_id: props.tables.find(t => t.physical_name === r.target_table)?.id
    }))
    showRecommendModal.value = true
  } catch (e) {
    showToast('智能发现失败', 'error')
  } finally {
    recommending.value = false
  }
}

const handleSaveRecommended = async () => {
  const selected = recommendedRels.value.filter(r => r.selected && r.source_table_id && r.target_table_id)
  if (selected.length === 0) return
  
  saving.value = true
  try {
    for (const r of selected) {
      await metadataV2Api.createRelationship(props.datasetId, {
        source_table_id: r.source_table_id,
        target_table_id: r.target_table_id,
        join_condition: r.condition,
        join_type: r.type,
        description: r.description
      })
    }
    showRecommendModal.value = false
    fetchRelationships()
    emit('saved')
    showToast(`成功导入 ${selected.length} 条关联关系`, 'success')
  } catch (e) {
    showToast('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const handleSave = async () => {
  if (!form.value.source_table_id || !form.value.target_table_id) return
  saving.value = true
  try {
    await metadataV2Api.createRelationship(props.datasetId, form.value)
    showModal.value = false
    fetchRelationships()
    emit('saved')
    showToast(editingId.value ? '关联关系已更新' : '关联关系已保存', 'success')
  } finally {
    saving.value = false
  }
}

const handleDelete = (relId: number) => {
  deletingRelId.value = relId
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  if (!deletingRelId.value) return
  try {
    await metadataV2Api.deleteRelationship(props.datasetId, deletingRelId.value)
    showToast('关联关系已删除', 'success')
    showDeleteConfirm.value = false
    deletingRelId.value = null
    fetchRelationships()
    emit('saved')
  } catch (e) {
    showToast('删除失败', 'error')
  }
}

const getTableName = (id: number) => {
  const t = props.tables.find(t => t.id === id)
  return t ? t.physical_name : 'Unknown'
}

watch(() => props.datasetId, fetchRelationships)
onMounted(() => {
  fetchRelationships()
  checkAiStatus()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center px-1">
      <div>
        <h3 class="text-xl font-bold text-gray-900 tracking-tight">实体关联图谱</h3>
        <p class="text-xs text-gray-500 mt-1">定义跨表 JOIN 路径，帮助 AI 理解数据模型</p>
      </div>
      <div class="flex gap-2">
        <button 
          v-if="hasPerm('element:metadata:manage')"
          @click="handleRecommend" :disabled="!isAiEnabled || recommending || tables.length < 2"
          class="bg-white border border-indigo-100 text-indigo-600 px-4 py-2 rounded-lg transition shadow-sm flex items-center gap-2 text-sm font-bold active:scale-95 disabled:opacity-50"
        >
          <ArrowPathIcon v-if="recommending" class="w-4 h-4 animate-spin" />
          <SparklesIcon v-else class="w-4 h-4 text-amber-500" />
          智能发现关系
        </button>
        <button 
          v-if="hasPerm('element:metadata:manage')"
          @click="openCreate" :disabled="tables.length < 2" 
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition shadow-md flex items-center gap-2 text-sm font-bold active:scale-95 disabled:opacity-50"
        >
          <PlusIcon class="w-4 h-4" /> 新建关联
        </button>
      </div>
    </div>

    <!-- AI Warning if disabled -->
    <div v-if="!isAiEnabled && !dismissAiWarning" class="bg-amber-50 border border-amber-100 p-3 rounded-2xl flex items-center justify-between gap-2 text-amber-700 text-xs animate-in fade-in slide-in-from-top-1">
       <div class="flex items-center gap-2">
          <SparklesIcon class="w-4 h-4" />
          <span>AI 功能未开启，无法使用“智能发现关系”功能。请先在系统设置中启用 AI。</span>
       </div>
       <button @click="dismissAiWarning = true" class="text-amber-400 hover:text-amber-600 transition-colors p-0.5">
          <XMarkIcon class="w-4 h-4" />
       </button>
    </div>

    <div v-if="relationships.length === 0" class="text-center py-32 bg-purple-50/30 rounded-[2.5rem] border-4 border-dashed border-purple-100">
      <div class="text-5xl mb-4 grayscale opacity-30">🔗</div>
      <p class="text-purple-700 font-black">暂无定义的实体关联</p>
      <p class="text-xs text-purple-600/60 mt-2">定义表之间的 Join 路径，让 AI 知道如何进行多表关联查询</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div v-for="r in relationships" :key="r.id" class="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm flex items-center gap-8 group hover:shadow-md transition-all">
        <div class="flex-1 flex items-center justify-between">
           <div class="flex items-center gap-4">
              <span class="px-4 py-2 bg-indigo-50 text-indigo-600 rounded-xl font-black text-xs border border-indigo-100">{{ getTableName(r.source_table_id) }}</span>
              <div class="flex flex-col items-center gap-1">
                 <span class="text-[8px] font-black text-purple-500 uppercase tracking-widest">{{ r.join_type }}</span>
                 <ChevronRightIcon class="w-6 h-6 text-gray-300 group-hover:text-purple-500 transition-colors" />
              </div>
              <span class="px-4 py-2 bg-emerald-50 text-emerald-600 rounded-xl font-black text-xs border border-emerald-100">{{ getTableName(r.target_table_id) }}</span>
           </div>
           
           <div class="flex-1 max-w-md mx-10">
              <code class="block w-full bg-gray-900 text-cyan-400 font-mono text-[11px] px-4 py-2 rounded-xl truncate shadow-inner">{{ r.join_condition }}</code>
           </div>
           <div class="flex items-center gap-1 text-[10px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
              <UserIcon class="w-3 h-3" />
              <span>{{ r.creator_name || '系统' }}</span>
           </div>
        </div>
        <div v-if="hasPerm('element:metadata:manage')" class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button @click="openEdit(r)" class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all" title="编辑关联"><PencilSquareIcon class="w-5 h-5" /></button>
          <button @click="handleDelete(r.id)" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all" title="删除关联"><TrashIcon class="w-5 h-5" /></button>
        </div>
      </div>
    </div>

    <!-- Recommend Modal -->
    <div v-if="showRecommendModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
       <div class="bg-white rounded-[2.5rem] shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col overflow-hidden animate-in zoom-in duration-200">
          <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
             <div class="flex items-center gap-3">
                <SparklesIcon class="w-6 h-6 text-amber-500" />
                <h3 class="text-xl font-bold text-gray-900">AI 智能发现关联</h3>
             </div>
             <button @click="showRecommendModal = false" class="text-gray-400 hover:text-gray-600 p-2"><XMarkIcon class="w-6 h-6" /></button>
          </div>
          
          <div class="flex-1 overflow-y-auto p-8 bg-gray-50/50 space-y-4">
             <p class="text-xs text-gray-500 mb-4 uppercase tracking-widest font-black">AI 根据表名和字段语义，为您识别出以下潜在关联：</p>
             
             <div v-if="recommendedRels.length === 0" class="text-center py-12">
                <p class="text-sm text-gray-400">AI 未能发现新的有效关联关系。</p>
             </div>

             <div v-for="(r, idx) in recommendedRels" :key="idx" 
               @click="r.selected = !r.selected"
               :class="r.selected ? 'border-indigo-500 bg-white shadow-md' : 'border-transparent bg-gray-100 opacity-60'"
               class="p-5 rounded-2xl border-2 transition-all cursor-pointer flex items-center gap-6"
             >
                <div class="flex-shrink-0">
                   <div :class="r.selected ? 'bg-indigo-600' : 'bg-gray-300'" class="w-6 h-6 rounded-full flex items-center justify-center text-white">
                      <CheckIcon class="w-4 h-4 stroke-[3]" />
                   </div>
                </div>
                <div class="flex-1">
                   <div class="flex items-center gap-3 mb-2">
                      <span class="text-xs font-black text-gray-900">{{ r.source_table }}</span>
                      <ChevronRightIcon class="w-4 h-4 text-gray-400" />
                      <span class="text-xs font-black text-gray-900">{{ r.target_table }}</span>
                      <span class="text-[9px] bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded font-bold uppercase">{{ r.type }}</span>
                   </div>
                   <code class="text-[10px] font-mono text-indigo-600 block mb-1">{{ r.condition }}</code>
                   <p class="text-[10px] text-gray-400 font-medium">{{ r.description }}</p>
                </div>
             </div>
          </div>

          <div class="px-8 py-6 bg-gray-50 border-t flex justify-end gap-3">
             <button @click="showRecommendModal = false" class="px-6 py-2.5 text-gray-500 font-bold hover:bg-gray-100 rounded-xl transition-all text-sm">取消</button>
             <button 
               @click="handleSaveRecommended" :disabled="saving || recommendedRels.filter(r=>r.selected).length === 0"
               class="px-10 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-all active:scale-95 disabled:opacity-50 text-sm flex items-center gap-2"
             >
               <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
               确认导入已选关联
             </button>
          </div>
       </div>
    </div>

    <!-- Create Modal (Aligned Style) -->
    <div v-if="showModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
       <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in zoom-in duration-200 flex flex-col">
          <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
             <div class="flex items-center gap-3">
                <div class="p-2.5 bg-indigo-600 rounded-xl text-white shadow-md"><ShareIcon class="w-5 h-5" /></div>
                <h3 class="text-xl font-bold text-gray-900">{{ editingId ? '编辑关联关系' : '定义表关联关系' }}</h3>
             </div>
             <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors"><XMarkIcon class="w-6 h-6" /></button>
          </div>
          
          <div class="p-8 space-y-8 bg-white">
             <div class="grid grid-cols-2 gap-8">
                <div class="space-y-3">
                   <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">源表 (Left Table)</label>
                   <select 
                     v-model.number="form.source_table_id" 
                     class="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl font-bold text-sm outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                   >
                      <option :value="0">请选择源表...</option>
                      <option v-for="t in tables" :key="t.id" :value="t.id">{{ t.physical_name }} ({{ t.term }})</option>
                   </select>
                   
                   <div v-if="form.source_table_id > 0" class="space-y-1.5 animate-in slide-in-from-top-2">
                      <label class="block text-[9px] font-bold text-indigo-400 uppercase tracking-widest ml-1">关联字段</label>
                      <select v-model="sourceField" @change="applyJoinCondition" class="w-full px-4 py-2 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs font-mono text-indigo-600 outline-none">
                         <option value="">-- 选择字段 --</option>
                         <option v-for="c in sourceColumns" :key="c.physical_name" :value="c.physical_name">{{ c.physical_name }}</option>
                      </select>
                   </div>
                </div>

                <div class="space-y-3">
                   <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">目标表 (Right Table)</label>
                   <select 
                     v-model.number="form.target_table_id" 
                     class="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl font-bold text-sm outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                   >
                      <option :value="0">请选择目标表...</option>
                      <option v-for="t in tables" :key="t.id" :value="t.id">{{ t.physical_name }} ({{ t.term }})</option>
                   </select>

                   <div v-if="form.target_table_id > 0" class="space-y-1.5 animate-in slide-in-from-top-2">
                      <label class="block text-[9px] font-bold text-emerald-400 uppercase tracking-widest ml-1">关联字段</label>
                      <select v-model="targetField" @change="applyJoinCondition" class="w-full px-4 py-2 bg-emerald-50/50 border border-emerald-100 rounded-lg text-xs font-mono text-emerald-600 outline-none">
                         <option value="">-- 选择字段 --</option>
                         <option v-for="c in targetColumns" :key="c.physical_name" :value="c.physical_name">{{ c.physical_name }}</option>
                      </select>
                   </div>
                </div>
             </div>

             <div class="space-y-2">
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">SQL Join 条件 (Condition)</label>
                <input v-model="form.join_condition" class="w-full px-5 py-4 bg-slate-900 border-none rounded-2xl text-cyan-400 font-mono text-sm focus:ring-4 focus:ring-indigo-500/10 transition-all shadow-inner" placeholder="e.g. t1.id = t2.ref_id" />
             </div>
          </div>

          <div class="px-8 py-6 bg-gray-50 border-t flex justify-end gap-3">
             <button @click="showModal = false" class="px-6 py-2 text-gray-500 font-bold hover:text-gray-700 transition-colors text-sm">取消</button>
             <button 
               @click="handleSave" :disabled="saving || !form.source_table_id || !form.target_table_id" 
               class="px-10 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-all active:scale-95 disabled:opacity-50 text-sm"
             >
               建立关联路径
             </button>
          </div>
       </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden transform transition-all animate-in zoom-in duration-200">
        <div class="p-6 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <TrashIcon class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg leading-6 font-bold text-gray-900 mb-2">确认删除实体关联?</h3>
          <p class="text-sm text-gray-500 mb-6 leading-relaxed">
            此操作将永久移除该 Join 路径，<br/><span class="text-red-500 font-bold">不可撤销</span>。
          </p>
          <div class="flex gap-3">
            <button @click="showDeleteConfirm = false" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-bold rounded-lg hover:bg-gray-200 transition-all text-sm">取消</button>
            <button @click="confirmDelete" class="flex-1 py-2.5 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 shadow-lg transition-all text-sm">确认删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>