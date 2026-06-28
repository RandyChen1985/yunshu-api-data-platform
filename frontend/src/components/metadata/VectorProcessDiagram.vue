<script setup lang="ts">
import { ref } from 'vue'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, PhotoIcon, CodeBracketIcon } from '@heroicons/vue/24/outline'

defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const activeTab = ref<'diagram' | 'specs'>('diagram')
</script>

<template>
  <TransitionRoot as="template" :show="show">
    <Dialog as="div" class="relative z-[9999]" @close="emit('close')">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-900/75 backdrop-blur-sm transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
              <!-- Header -->
              <div class="px-6 py-4 bg-indigo-50/50 border-b border-indigo-100 flex justify-between items-center">
                <div>
                  <h3 class="text-lg font-bold text-gray-900">向量化与检索原理 (Vectorization & RAG)</h3>
                  <p class="text-xs text-gray-500 mt-0.5">Understanding how Data transforms into Vectors and powers Semantic Search</p>
                </div>
                <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-white/50">
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>

              <!-- Tabs -->
              <div class="px-6 border-b border-gray-100 flex gap-6">
                <button 
                  @click="activeTab = 'diagram'"
                  class="py-3 text-xs font-bold border-b-2 transition-colors flex items-center gap-2"
                  :class="activeTab === 'diagram' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                >
                  <PhotoIcon class="w-4 h-4" /> 流程原理图 (Diagram)
                </button>
                <button 
                  @click="activeTab = 'specs'"
                  class="py-3 text-xs font-bold border-b-2 transition-colors flex items-center gap-2"
                  :class="activeTab === 'specs' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                >
                  <CodeBracketIcon class="w-4 h-4" /> 详细设计文档 (Specs)
                </button>
              </div>

              <!-- Content -->
              <div class="p-8 bg-white min-h-[500px]">
                
                <!-- Tab 1: Diagram -->
                <div v-if="activeTab === 'diagram'">
                  <svg viewBox="0 0 800 500" class="w-full h-auto" xmlns="http://www.w3.org/2000/svg">
                    <!-- Defs for arrows and gradients -->
                    <defs>
                      <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
                      </marker>
                      <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
                      </linearGradient>
                      <filter id="shadow">
                        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.1" />
                      </filter>
                    </defs>

                    <!-- Background Grid (Subtle) -->
                    <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#smallGrid)" />

                    <!-- ================= PART 1: SYNC PROCESS (Top) ================= -->
                    <g transform="translate(50, 40)">
                       <text x="0" y="0" class="text-sm font-bold fill-indigo-900" style="font-size: 14px; font-weight: 800;">🔄 流程一：数据同步与向量化 (Sync & Embedding)</text>
                       <line x1="0" y1="15" x2="700" y2="15" stroke="#e2e8f0" stroke-dasharray="4"/>
                    </g>

                    <!-- Node 1: Dataset -->
                    <g transform="translate(50, 100)" filter="url(#shadow)">
                      <rect width="120" height="80" rx="10" fill="white" stroke="#cbd5e1" stroke-width="2" />
                      <text x="60" y="35" text-anchor="middle" font-size="24">🗄️</text>
                      <text x="60" y="55" text-anchor="middle" font-size="12" font-weight="bold" fill="#334155">MySQL</text>
                      <text x="60" y="70" text-anchor="middle" font-size="10" fill="#64748b">Datasets</text>
                    </g>

                    <!-- Arrow 1 -->
                    <line x1="170" y1="140" x2="210" y2="140" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrowhead)" />
                    <text x="190" y="130" text-anchor="middle" font-size="10" fill="#64748b">YAML Gen</text>

                    <!-- Node 2: AI Model -->
                    <g transform="translate(220, 100)" filter="url(#shadow)">
                      <rect width="120" height="80" rx="10" fill="#f8fafc" stroke="#4f46e5" stroke-width="2" stroke-dasharray="5,5" />
                      <text x="60" y="35" text-anchor="middle" font-size="24">🧠</text>
                      <text x="60" y="55" text-anchor="middle" font-size="12" font-weight="bold" fill="#4f46e5">Embedding</text>
                      <text x="60" y="70" text-anchor="middle" font-size="10" fill="#6366f1">text-embedding-3</text>
                    </g>

                    <!-- Arrow 2 -->
                    <line x1="340" y1="140" x2="380" y2="140" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrowhead)" />
                    
                    <!-- Node 3: Vector Data -->
                    <g transform="translate(390, 115)">
                       <text x="0" y="0" font-family="monospace" font-size="10" fill="#059669">[0.12, -0.9, ...]</text>
                       <rect x="-5" y="-15" width="100" height="20" fill="none" stroke="#10b981" rx="4" />
                    </g>

                    <!-- Arrow 3 -->
                    <line x1="495" y1="140" x2="535" y2="140" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrowhead)" />

                    <!-- Node 4: Redis Stack -->
                    <g transform="translate(545, 90)" filter="url(#shadow)">
                      <rect width="140" height="100" rx="10" fill="#fff1f2" stroke="#e11d48" stroke-width="2" />
                      <text x="70" y="40" text-anchor="middle" font-size="24">🔴</text>
                      <text x="70" y="65" text-anchor="middle" font-size="14" font-weight="bold" fill="#be123c">Redis Stack</text>
                      <text x="70" y="85" text-anchor="middle" font-size="10" fill="#9f1239">Vector Index</text>
                    </g>


                    <!-- ================= PART 2: SEARCH PROCESS (Bottom) ================= -->
                    <g transform="translate(50, 260)">
                       <text x="0" y="0" class="text-sm font-bold fill-indigo-900" style="font-size: 14px; font-weight: 800;">🔎 流程二：语义检索 (Semantic Search)</text>
                       <line x1="0" y1="15" x2="700" y2="15" stroke="#e2e8f0" stroke-dasharray="4"/>
                    </g>

                    <!-- Node 1: User Query -->
                    <g transform="translate(50, 320)" filter="url(#shadow)">
                      <rect width="120" height="80" rx="10" fill="white" stroke="#cbd5e1" stroke-width="2" />
                      <text x="60" y="35" text-anchor="middle" font-size="24">👤</text>
                      <text x="60" y="55" text-anchor="middle" font-size="12" font-weight="bold" fill="#334155">用户提问</text>
                      <text x="60" y="70" text-anchor="middle" font-size="10" fill="#64748b">"查下销售额"</text>
                    </g>

                    <!-- Arrow 1 -->
                    <line x1="170" y1="360" x2="210" y2="360" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrowhead)" />

                    <!-- Node 2: AI Model (Reuse) -->
                    <g transform="translate(220, 320)" filter="url(#shadow)">
                      <rect width="120" height="80" rx="10" fill="#f8fafc" stroke="#4f46e5" stroke-width="2" stroke-dasharray="5,5" />
                      <text x="60" y="35" text-anchor="middle" font-size="24">🧠</text>
                      <text x="60" y="55" text-anchor="middle" font-size="12" font-weight="bold" fill="#4f46e5">Embedding</text>
                    </g>

                    <!-- Arrow 2 -->
                    <line x1="340" y1="360" x2="540" y2="360" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrowhead)" />
                    <text x="440" y="350" text-anchor="middle" font-size="10" fill="#64748b">Query Vector</text>

                    <!-- Connection to Redis -->
                    <path d="M 615 190 L 615 320" stroke="#e11d48" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrowhead)" />
                    <text x="625" y="270" font-size="11" fill="#be123c" font-weight="bold">KNN Search (Cosine)</text>

                    <!-- Node 3: Result -->
                    <g transform="translate(545, 320)" filter="url(#shadow)">
                       <rect width="140" height="80" rx="10" fill="#f0fdf4" stroke="#16a34a" stroke-width="2" />
                       <text x="70" y="35" text-anchor="middle" font-size="24">📄</text>
                       <text x="70" y="55" text-anchor="middle" font-size="12" font-weight="bold" fill="#15803d">Matched YAML</text>
                       <text x="70" y="70" text-anchor="middle" font-size="10" fill="#166534">Top K Results</text>
                    </g>

                  </svg>
                  
                  <div class="mt-6 bg-gray-50 p-4 rounded-xl border border-gray-100 text-xs text-gray-600 space-y-2">
                     <p><span class="font-bold text-gray-900">Embedding:</span> 将文本转化为 1536 维度的浮点数向量，让计算机能够理解"语义"。</p>
                     <p><span class="font-bold text-gray-900">Redis Stack:</span> 内置向量搜索引擎，支持 HNSW 算法，能够在毫秒级内从海量向量中找出最相似的 Top-K。</p>
                     <p><span class="font-bold text-gray-900">RAG (检索增强生成):</span> 将检索到的 YAML 上下文注入到 Prompt 中，让大模型基于准确的业务元数据生成 SQL。</p>
                  </div>
                </div>

                <!-- Tab 2: Specs -->
                <div v-else class="space-y-6 animate-fade-in text-sm">
                  <div class="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg">
                    <p class="text-indigo-800 font-medium">
                      要构建一套高性能且精准的元数据语义搜索系统，我们需要在 Redis Stack 中建立一套“向量+标量”的混合存储结构。
                    </p>
                  </div>

                  <div class="space-y-4">
                    <h4 class="font-bold text-gray-900 flex items-center gap-2">
                      <span class="w-6 h-6 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs">1</span>
                      存储单元设计 (Granularity)
                    </h4>
                    <div class="ml-8 bg-white p-4 rounded-xl border border-gray-200">
                      <p class="text-gray-600 mb-2">不建议直接把整个数据集存为一个 Key，因为这样会导致检索粒度太粗。我们应该以 <span class="font-bold text-gray-800">“业务原子”</span> 为单位进行存储：</p>
                      <ul class="list-disc list-inside text-gray-600 space-y-1 ml-2">
                        <li><span class="font-bold text-indigo-600">Table 单元：</span>每张表对应一个 Redis Key。</li>
                        <li><span class="font-bold text-amber-600">Metric 单元：</span>每个指标对应一个 Redis Key。</li>
                      </ul>
                    </div>
                  </div>

                  <div class="space-y-4">
                    <h4 class="font-bold text-gray-900 flex items-center gap-2">
                      <span class="w-6 h-6 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs">2</span>
                      Key 命名规范 (Key Design)
                    </h4>
                    <div class="ml-8 bg-slate-900 text-slate-300 p-4 rounded-xl font-mono text-xs">
                      <p class="mb-2 text-slate-500">// 采用分层命名空间，确保唯一性且方便前缀扫描</p>
                      <p>表 (Table): <span class="text-emerald-400">meta:v2:table:{table_id}</span></p>
                      <p>指标 (Metric): <span class="text-emerald-400">meta:v2:metric:{metric_id}</span></p>
                    </div>
                  </div>

                  <div class="space-y-4">
                     <h4 class="font-bold text-gray-900 flex items-center gap-2">
                      <span class="w-6 h-6 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs">3</span>
                      内容结构设计 (Redis Hash Structure)
                    </h4>
                    <div class="ml-8 overflow-hidden rounded-xl border border-gray-200">
                      <table class="min-w-full text-left text-xs">
                        <thead class="bg-gray-50 text-gray-500 font-bold uppercase">
                          <tr>
                            <th class="px-4 py-2">字段名</th>
                            <th class="px-4 py-2">类型</th>
                            <th class="px-4 py-2">设计目的</th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                          <tr class="bg-white">
                            <td class="px-4 py-3 font-mono font-bold text-indigo-600">payload</td>
                            <td class="px-4 py-3 font-mono text-gray-500">TEXT</td>
                            <td class="px-4 py-3 text-gray-600">被向量化的文本。包含表名、描述、字段列表。越详尽，匹配越准。</td>
                          </tr>
                          <tr class="bg-gray-50/50">
                            <td class="px-4 py-3 font-mono font-bold text-indigo-600">vector</td>
                            <td class="px-4 py-3 font-mono text-gray-500">VECTOR</td>
                            <td class="px-4 py-3 text-gray-600">二进制向量数据 (Binary Blob)，由 Embedding 模型生成。</td>
                          </tr>
                          <tr class="bg-white">
                            <td class="px-4 py-3 font-mono font-bold text-indigo-600">metadata</td>
                            <td class="px-4 py-3 font-mono text-gray-500">JSON</td>
                            <td class="px-4 py-3 text-gray-600">完整的表结构对象，命中后直接取出解析，无需回查 MySQL。</td>
                          </tr>
                          <tr class="bg-gray-50/50">
                            <td class="px-4 py-3 font-mono font-bold text-indigo-600">ds_name</td>
                            <td class="px-4 py-3 font-mono text-gray-500">TAG</td>
                            <td class="px-4 py-3 text-gray-600">归属数据源，用于 <span class="bg-gray-200 px-1 rounded">FILTER</span> 过滤查询。</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div class="space-y-4">
                    <h4 class="font-bold text-gray-900 flex items-center gap-2">
                      <span class="w-6 h-6 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs">4</span>
                      索引与查询 (Index & Search)
                    </h4>
                    <div class="ml-8 grid grid-cols-2 gap-4">
                       <div class="bg-slate-900 p-4 rounded-xl">
                          <p class="text-[10px] text-slate-500 font-bold uppercase mb-2">FT.CREATE (Index Setup)</p>
                          <pre class="text-[10px] text-emerald-400 font-mono leading-relaxed">FT.CREATE idx:meta_v2 
  ON HASH PREFIX 1 "meta:v2:"
  SCHEMA
    ds_name TAG
    payload TEXT WEIGHT 1.0
    vector VECTOR HNSW 6 
      TYPE FLOAT32 
      DIM 1536 
      DISTANCE_METRIC COSINE</pre>
                       </div>
                       <div class="bg-slate-900 p-4 rounded-xl">
                          <p class="text-[10px] text-slate-500 font-bold uppercase mb-2">FT.SEARCH (Retrieval)</p>
                          <pre class="text-[10px] text-cyan-400 font-mono leading-relaxed">FT.SEARCH idx:meta_v2
  "(@ds_name:{default})=>[KNN 20 @vector $vec]"
  PARAMS 2 vec [binary_blob]
  SORTBY score
  DIALECT 2</pre>
                       </div>
                    </div>
                  </div>

                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
