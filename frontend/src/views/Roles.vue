<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">业务角色管理</h1>
      <button @click="openCreateDialog" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 shadow-md">
        <PlusIcon class="w-5 h-5" /> 创建角色
      </button>
    </div>

    <div v-if="loading" class="bg-white shadow rounded-lg p-12 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-gray-500">加载角色列表中...</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="role in roles" :key="role.id" class="bg-white shadow-sm border border-gray-200 rounded-2xl p-6 hover:shadow-md transition-all group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-indigo-50 rounded-xl text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-all">
            <UserGroupIcon class="w-6 h-6" />
          </div>
          <div class="flex gap-2">
            <button @click="openMemberDialog(role)" class="p-1.5 text-gray-400 hover:text-indigo-600 transition-colors" title="成员管理"><UserPlusIcon class="w-5 h-5" /></button>
            <button @click="editRole(role)" class="p-1.5 text-gray-400 hover:text-blue-600 transition-colors" title="编辑角色与权限"><PencilSquareIcon class="w-5 h-5" /></button>
            <button @click="confirmDelete(role)" class="p-1.5 text-gray-400 hover:text-red-600 transition-colors"><TrashIcon class="w-5 h-5" /></button>
          </div>
        </div>
        <h3 class="text-lg font-bold text-gray-900">{{ role.role_name }}</h3>
        <p class="text-xs font-mono text-gray-400 mb-3">{{ role.role_code }}</p>
        <p class="text-sm text-gray-500 flex-1 line-clamp-2 mb-4">{{ role.description || '无详细描述' }}</p>
        
        <!-- Permission Stats (New) -->
        <div class="flex flex-wrap gap-2 mb-4">
          <div class="flex items-center bg-indigo-50 text-indigo-700 px-2 py-1 rounded-lg text-[10px] font-bold border border-indigo-100">
            <span class="mr-1">用户:</span> {{ role.stats?.user || 0 }}
          </div>
          <div class="flex items-center bg-blue-50 text-blue-700 px-2 py-1 rounded-lg text-[10px] font-bold border border-blue-100">
            <span class="mr-1">菜单:</span> {{ role.stats?.menu || 0 }}
          </div>
          <div class="flex items-center bg-purple-50 text-purple-700 px-2 py-1 rounded-lg text-[10px] font-bold border border-purple-100">
            <span class="mr-1">功能:</span> {{ role.stats?.element || 0 }}
          </div>
          <div class="flex items-center bg-orange-50 text-orange-700 px-2 py-1 rounded-lg text-[10px] font-bold border border-orange-100">
            <span class="mr-1">资源:</span> {{ role.stats?.resource || 0 }}
          </div>
        </div>

        <!-- Security & Rate Limit Info -->
        <div class="space-y-2 mb-4">
          <div class="flex items-center text-xs text-gray-600">
            <span class="mr-2 text-base">🛡️</span>
            <span class="font-medium mr-2">脱敏策略:</span>
            <span v-if="role.masking_strategy === 'ENABLE'" class="text-red-600 font-bold bg-red-50 px-1.5 py-0.5 rounded">强制开启</span>
            <span v-else-if="role.masking_strategy === 'DISABLE'" class="text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">允许明文</span>
            <span v-else class="text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">跟随全局</span>
          </div>
          <div class="flex items-center text-xs text-gray-600">
            <span class="mr-2 text-base">⚡️</span>
            <span class="font-medium mr-2">流控限制:</span>
            <span v-if="role.rate_limit" class="text-amber-700 font-bold">{{ role.rate_limit }} <span class="font-normal text-[10px]">次/分</span></span>
            <span v-else class="text-gray-400 italic font-normal">默认策略</span>
          </div>
        </div>

        <div class="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center text-[10px] text-gray-400">

          <span class="flex items-center gap-1"><ClockIcon class="w-3 h-3" /> {{ formatDate(role.created_at) }}</span>
          <span class="bg-gray-100 px-2 py-0.5 rounded text-gray-500 font-bold uppercase tracking-tighter">Business Role</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9990]" @click.self="showEditModal = false">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden transform transition-all">
        <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
          <h2 class="text-xl font-bold text-gray-900">{{ isEdit ? '编辑角色权限' : '创建新角色' }}</h2>
          <button @click="showEditModal = false" class="text-gray-400 hover:text-gray-600 transition-colors"><XMarkIcon class="w-6 h-6" /></button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-gray-200 bg-white px-8">
          <button @click="activeTab = 'info'" class="px-6 py-4 text-sm font-bold border-b-2 transition-all" :class="activeTab === 'info' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'">基础信息</button>
          <button @click="activeTab = 'permissions'" class="px-6 py-4 text-sm font-bold border-b-2 transition-all" :class="activeTab === 'permissions' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'">功能权限配置</button>
        </div>

        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar bg-white">
          <!-- Info Tab -->
          <div v-show="activeTab === 'info'" class="space-y-6">
            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">角色名称</label>
                <input v-model="formData.role_name" class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all" placeholder="如：数据分析师" />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">角色编码</label>
                <input v-model="formData.role_code" :disabled="isEdit" class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all disabled:bg-gray-50" placeholder="如：data_analyst" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">角色描述</label>
              <textarea v-model="formData.description" class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all" rows="4" placeholder="简述该角色的职责范围..."></textarea>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                ⚡️ API 限流阈值 (Rate Limit)
                <span class="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded font-normal normal-case">每分钟最大请求数</span>
              </label>
              <div class="relative">
                <input v-model.number="formData.rate_limit" type="number" class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all pr-12" placeholder="0" />
                <span class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xs font-bold">次/分</span>
              </div>
              <p class="mt-1 text-[10px] text-gray-400">设为 0 或留空表示使用系统默认策略。</p>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                🛡️ 角色脱敏策略 (Masking Strategy)
              </label>
              <select v-model="formData.masking_strategy" class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all">
                <option value="GLOBAL">跟随全局 (Follow Global)</option>
                <option value="ENABLE">强制开启 (Force Enable)</option>
                <option value="DISABLE">允许明文 (Allow Plaintext)</option>
              </select>
              <p class="mt-1 text-[10px] text-gray-400">该角色下所有用户的默认脱敏行为。</p>
            </div>
          </div>

          <!-- Permissions Tab -->
          <div v-show="activeTab === 'permissions'" class="flex flex-col h-full min-h-[500px]">
            <!-- Sub Tabs -->
            <div class="flex space-x-1 p-1 bg-gray-100 rounded-xl mb-6 w-fit">
              <button @click="activePermissionSubTab = 'resource'" 
                :class="activePermissionSubTab === 'resource' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                class="px-6 py-2 text-xs font-bold rounded-lg transition-all uppercase tracking-wider flex items-center gap-2">
                接口资源
                <span class="bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded-md text-[10px]">{{ selectedResources.length }}</span>
              </button>
              <button @click="activePermissionSubTab = 'ui'" 
                :class="activePermissionSubTab === 'ui' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                class="px-6 py-2 text-xs font-bold rounded-lg transition-all uppercase tracking-wider flex items-center gap-2">
                功能与菜单
                <span class="bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-md text-[10px]">{{ selectedMenus.length + selectedElements.length }}</span>
              </button>
              <button @click="activePermissionSubTab = 'data'" 
                :class="activePermissionSubTab === 'data' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                class="px-6 py-2 text-xs font-bold rounded-lg transition-all uppercase tracking-wider flex items-center gap-2">
                数据资产 (SQL)
                <span class="bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded-md text-[10px]">{{ selectedDataSources.length + selectedDataTables.length }}</span>
              </button>
            </div>

            <!-- Resource Sub-Tab -->
            <div v-show="activePermissionSubTab === 'resource'" class="space-y-6 flex-1">
              <div v-for="(resources, group) in groupedResources" :key="group" class="bg-gray-50 rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
                <div class="px-5 py-3 bg-white border-b border-gray-100 flex items-center justify-between">
                  <span class="text-xs font-black text-gray-400 uppercase tracking-widest">{{ group }}</span>
                  <button @click="toggleGroupSelection(resources)" type="button" class="text-[10px] font-bold text-blue-600 hover:underline">
                    {{ isGroupAllSelected(resources) ? '取消全选' : '选择全部' }}
                  </button>
                </div>
                <div class="p-4 grid grid-cols-2 gap-3">
                  <label v-for="resource in resources" :key="resource.id" 
                    class="flex items-start p-3 rounded-xl border cursor-pointer transition-all"
                    :class="selectedResources.includes(resource.id) ? 'bg-blue-50 border-blue-200' : 'bg-white border-transparent hover:border-gray-200'">
                    <input type="checkbox" v-model="selectedResources" :value="resource.id" class="mt-1 h-4 w-4 rounded text-blue-600 border-gray-300 focus:ring-blue-500" />
                    <div class="ml-3 min-w-0">
                      <p class="text-sm font-bold text-gray-800 truncate flex items-center gap-2">
                        {{ resource.name }}
                        <span v-if="resource.id === 'system.sql.execute'" class="text-[9px] bg-red-100 text-red-600 px-1 py-0.5 rounded font-black border border-red-200 uppercase shrink-0">ROOT 权限</span>
                      </p>
                      <p class="text-[10px] text-gray-400 font-mono truncate">{{ resource.id }}</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <!-- UI Sub-Tab -->
            <div v-show="activePermissionSubTab === 'ui'" class="grid grid-cols-1 gap-4">
              <div v-for="menu in MENU_TREE" :key="menu.id" class="bg-gray-50 rounded-2xl border border-gray-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <div class="px-5 py-3 bg-white border-b border-gray-100 flex items-center gap-3">
                  <input type="checkbox" :value="menu.id" v-model="selectedMenus" class="h-5 w-5 text-indigo-600 rounded-lg border-gray-300 focus:ring-indigo-500" />
                  <span class="text-sm font-black text-gray-800 flex items-center gap-2">
                    <span class="bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded text-[10px] font-normal border border-gray-200">菜单</span>
                    {{ menu.label }}
                  </span>
                </div>
                <div v-if="menu.children.length > 0" class="p-4 grid grid-cols-2 gap-2">
                  <label v-for="child in menu.children" :key="child.id" 
                    class="flex items-center p-2 rounded-lg border cursor-pointer transition-all"
                    :class="selectedElements.includes(child.id) ? 'bg-indigo-50 border-indigo-100' : 'bg-white/50 border-transparent hover:border-gray-200'">
                    <input type="checkbox" :value="child.id" v-model="selectedElements" class="h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
                    <span class="ml-3 text-xs font-medium text-gray-600 flex items-center gap-2">
                      <span class="bg-purple-50 text-purple-600 px-1 py-0.5 rounded text-[9px] border border-purple-100">功能</span>
                      {{ child.label }}
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Data Asset Sub-Tab -->
            <div v-show="activePermissionSubTab === 'data'" class="space-y-4">
              <div class="bg-orange-50 border border-orange-100 rounded-xl p-4 mb-4">
                <div class="space-y-1">
                  <p class="text-[10px] text-orange-700 font-bold flex items-center gap-2 uppercase tracking-wider">
                    <span class="bg-orange-600 text-white px-1 py-0.5 rounded text-[8px]">重要提示</span>
                    表级权限遵循：空 = 无权限，ALL = 所有权限。请务必显式配置。
                  </p>
                  <p class="text-[10px] text-orange-600 flex items-center gap-2 pl-[54px]">
                    ※ 数据源权限直接影响 SQL 实验室页面功能及 SQL 动态查询接口的访问授权。
                  </p>
                </div>
              </div>

              <div v-for="ds in allDataSources" :key="ds.source_name" class="bg-gray-50 rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
                <div class="px-5 py-3 bg-white border-b border-gray-100 flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <input type="checkbox" :value="`ds:${ds.source_name}`" v-model="selectedDataSources" class="h-5 w-5 text-orange-600 rounded-lg border-gray-300 focus:ring-orange-500" />
                    <span class="text-sm font-black text-gray-800 uppercase">{{ ds.source_name }}</span>
                    <span class="bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded text-[9px] font-bold border border-gray-200">{{ ds.source_type }}</span>
                  </div>
                  <button 
                    v-if="selectedDataSources.includes(`ds:${ds.source_name}`)"
                    @click="toggleDSExpand(ds.source_name)" 
                    class="text-[10px] font-bold text-orange-600 hover:underline flex items-center gap-1">
                    {{ expandedDS === ds.source_name ? '收起配置' : '配置表权限' }}
                  </button>
                </div>

                <div v-if="expandedDS === ds.source_name" class="p-5 bg-white border-t border-gray-50 space-y-4 animate-in slide-in-from-top-2 duration-200">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex gap-2">
                      <button 
                        @click="setDSAllTables(ds.source_name)"
                        :class="isDSAllTables(ds.source_name) ? 'bg-orange-600 text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'"
                        class="px-3 py-1 rounded text-[10px] font-bold transition-all">
                        所有表 (ALL)
                      </button>
                    </div>
                    <div class="relative w-48">
                      <input v-model="tableSearch" placeholder="搜索表名..." class="w-full text-[10px] border border-gray-200 rounded-lg px-2 py-1 outline-none focus:ring-1 focus:ring-orange-500" />
                    </div>
                  </div>

                  <div v-if="loadingTables" class="py-12 text-center">
                    <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-orange-600"></div>
                  </div>
                  
                  <div v-else class="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto custom-scrollbar p-1">
                    <label v-for="table in filteredTables" :key="typeof table === 'string' ? table : table.name" 
                      class="flex items-center p-2 rounded-lg border cursor-pointer transition-all"
                      :class="selectedDataTables.includes(`ds:${ds.source_name}:table:${typeof table === 'string' ? table : table.name}`) ? 'bg-orange-50 border-orange-200' : 'bg-white border-transparent hover:border-gray-100'">
                      <input type="checkbox" :value="`ds:${ds.source_name}:table:${typeof table === 'string' ? table : table.name}`" v-model="selectedDataTables" class="h-3 w-3 text-orange-600 rounded border-gray-300 focus:ring-orange-500" />
                      <div class="ml-2 flex flex-col min-w-0">
                        <span class="text-[10px] font-medium text-gray-600 truncate">{{ typeof table === 'string' ? table : table.name }}</span>
                        <span v-if="typeof table !== 'string'" :class="table.type === 'VIEW' ? 'text-amber-500' : 'text-blue-500'" class="text-[8px] font-black uppercase">{{ table.type }}</span>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <div class="px-8 py-6 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="showEditModal = false" class="px-6 py-2.5 text-gray-500 font-bold hover:text-gray-700 transition-colors">取消</button>
          <button @click="saveRole" :disabled="submitting" class="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-all disabled:opacity-50 flex items-center gap-2">
            <span v-if="submitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            确认保存
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden transform transition-all animate-in zoom-in duration-200">
        <div class="p-6 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <TrashIcon class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg leading-6 font-bold text-gray-900 mb-2">确认删除角色?</h3>
          <p class="text-sm text-gray-500 mb-6">
            您即将删除角色 <span class="font-bold text-gray-800">{{ roleToDelete?.role_name }}</span>。
            <br/><span class="text-red-500 font-bold">此操作不可撤销</span>，所有关联用户的权限将立即失效。
          </p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false" class="flex-1 py-2.5 bg-gray-100 text-gray-700 font-bold rounded-lg hover:bg-gray-200 transition-all">取消</button>
            <button @click="executeDeleteRole" class="flex-1 py-2.5 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 shadow-lg transition-all">确认删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Role Members Assignment Dialog -->
    <div v-if="showMemberModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9990]" @click.self="showMemberModal = false">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden transform transition-all animate-in zoom-in duration-200">
        <div class="px-8 py-6 border-b bg-gray-50 flex justify-between items-center">
          <div>
            <h2 class="text-xl font-bold text-gray-900">成员管理</h2>
            <p class="text-xs text-gray-500 mt-1">当前角色：<span class="font-bold text-indigo-600">{{ currentRole?.role_name }}</span></p>
          </div>
          <button @click="showMemberModal = false" class="text-gray-400 hover:text-gray-600 transition-colors"><XMarkIcon class="w-6 h-6" /></button>
        </div>

        <div class="p-8">
          <div v-if="loadingMembers" class="py-12 text-center">
             <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
             <p class="mt-2 text-gray-500">获取成员数据中...</p>
          </div>
          <div v-else class="flex gap-6 h-[400px]">
            <!-- Available Users -->
            <div class="flex-1 flex flex-col border border-gray-200 rounded-2xl overflow-hidden">
              <div class="px-4 py-2 bg-gray-50 border-b flex justify-between items-center">
                <span class="text-xs font-bold text-gray-600 uppercase">备选用户 ({{ availableUsers.length }})</span>
                <input v-model="userSearch" placeholder="搜索..." class="text-[10px] border border-gray-300 rounded px-2 py-0.5 focus:ring-1 focus:ring-indigo-500 outline-none" />
              </div>
              <div class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
                <div v-for="user in filteredAvailableUsers" :key="user.id" 
                  @click="toggleMemberSelection(user.id)"
                  class="p-2 rounded-lg text-sm cursor-pointer flex items-center justify-between transition-all"
                  :class="selectedMemberIds.includes(user.id) ? 'bg-indigo-600 text-white shadow-sm' : 'hover:bg-gray-100 text-gray-700'">
                  <span class="font-medium">{{ user.user_name }}</span>
                  <span class="text-[10px] opacity-70">{{ user.role }}</span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col justify-center gap-4">
               <button @click="moveToSelected" :disabled="!selectedMemberIds.length" class="p-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-600 hover:text-white transition-all disabled:opacity-30">
                 <ChevronRightIcon class="w-5 h-5" />
               </button>
               <button @click="moveToAvailable" :disabled="!selectedInSelectedIds.length" class="p-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-600 hover:text-white transition-all disabled:opacity-30">
                 <ChevronLeftIcon class="w-5 h-5" />
               </button>
            </div>

            <!-- Selected Users -->
            <div class="flex-1 flex flex-col border border-indigo-200 rounded-2xl overflow-hidden bg-indigo-50/10">
              <div class="px-4 py-2 bg-indigo-50 border-b border-indigo-100 flex justify-between items-center">
                <span class="text-xs font-bold text-indigo-600 uppercase">已分配成员 ({{ roleMembers.length }})</span>
              </div>
              <div class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
                <div v-for="user in roleMembers" :key="user.id" 
                  @click="toggleInSelectedSelection(user.id)"
                  class="p-2 rounded-lg text-sm cursor-pointer flex items-center justify-between transition-all"
                  :class="selectedInSelectedIds.includes(user.id) ? 'bg-indigo-600 text-white shadow-sm' : 'hover:bg-indigo-100/50 text-gray-700'">
                  <span class="font-medium">{{ user.user_name }}</span>
                  <span class="text-[10px] opacity-70">{{ user.role }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="px-8 py-6 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="showMemberModal = false" class="px-6 py-2.5 text-gray-500 font-bold hover:text-gray-700 transition-colors">取消</button>
          <button @click="saveMembers" :disabled="submittingMembers" class="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-all disabled:opacity-50 flex items-center gap-2">
            <span v-if="submittingMembers" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            保存更改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'

import axios from '../utils/axios'
import { useToast } from '../composables/useToast'
import { 
  PlusIcon, UserGroupIcon, PencilSquareIcon, TrashIcon, XMarkIcon, ClockIcon,
  UserPlusIcon, ChevronRightIcon, ChevronLeftIcon
} from '@heroicons/vue/24/outline'

const { showToast } = useToast()

// --- Constants ---
const MENU_TREE = [
    { id: 'menu:overview', label: '系统概览', children: [] },
    { id: 'menu:asset-panorama', label: '数据资产全景', children: [] },
    { id: 'menu:catalog:requests', label: '目录权限申请', children: [
        { id: 'element:catalog:review', label: '审批目录访问申请' },
        { id: 'element:catalog:manage', label: '编辑数据产品信息' }
    ] },
    { id: 'menu:lab', label: 'SQL 实验室', children: [
        { id: 'element:lab:generate', label: 'AI 生成/修改 SQL' }, 
        { id: 'element:lab:publish', label: '发布为 API' },
        { id: 'element:lab:export', label: 'Excel 数据导出' },
        { id: 'element:lab:analysis', label: 'AI 多轮分析/图表' },
        { id: 'element:lab:mode_api', label: '模式：API 调试' },
        { id: 'element:lab:mode_analyst', label: '模式：自助取数' }
    ] },
    { id: 'menu:resources', label: '接口管理', children: [{ id: 'element:resource:create', label: '新建接口' }, { id: 'element:resource:edit', label: '编辑接口' }, { id: 'element:resource:delete', label: '删除接口' }, { id: 'element:resource:import', label: '导入配置' }, { id: 'element:resource:export', label: '导出配置' }, { id: 'element:resource:manage_special', label: '管理特殊资源(TTL/SQL测试)' }, { id: 'element:catalog:publish', label: '发布到产品目录' }] },
    
    { id: 'menu:metadata', label: '元数据管理', children: [
        { id: 'element:metadata:view', label: '查看：元数据详情' },
        { id: 'element:metadata:manage', label: '管理：编辑元数据/指标' }
    ] },

    { id: 'menu:datasource', label: '数据源管理', children: [{ id: 'element:datasource:edit', label: '编辑数据源' }] },
    { id: 'menu:audit', label: '审计日志', children: [] },
    { id: 'menu:playground', label: 'API 调试', children: [] },
    { id: 'menu:users', label: '用户管理', children: [{ id: 'element:user:manage', label: '管理用户/权限' }] },

    { id: 'menu:roles', label: '角色管理', children: [] },
    { id: 'menu:config', label: '系统设置', children: [{ id: 'element:config:save', label: '保存系统配置' }] }
]

// State
const roles = ref<any[]>([])
const loading = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const roleToDelete = ref<any>(null)
const isEdit = ref(false)
const submitting = ref(false)
const activeTab = ref<'info' | 'permissions'>('info')
const activePermissionSubTab = ref<'resource' | 'ui' | 'data'>('resource')
const formData = ref({ 
  id: null, 
  role_name: '', 
  role_code: '', 
  description: '', 
  rate_limit: null as number | null,
  masking_strategy: 'GLOBAL'
})

// Member Assignment State
const showMemberModal = ref(false)
const loadingMembers = ref(false)
const submittingMembers = ref(false)
const currentRole = ref<any>(null)
const allUsers = ref<any[]>([])
const roleMembers = ref<any[]>([])
const userSearch = ref('')
const selectedMemberIds = ref<number[]>([]) // Selection in Available list
const selectedInSelectedIds = ref<number[]>([]) // Selection in Selected list

const availableUsers = computed(() => {
  const memberIds = roleMembers.value.map(m => m.id)
  return allUsers.value.filter(u => !memberIds.includes(u.id))
})

const filteredAvailableUsers = computed(() => {
  if (!userSearch.value) return availableUsers.value
  return availableUsers.value.filter(u => u.user_name.toLowerCase().includes(userSearch.value.toLowerCase()))
})

const openMemberDialog = async (role: any) => {
  currentRole.value = role
  showMemberModal.value = true
  loadingMembers.value = true
  selectedMemberIds.value = []
  selectedInSelectedIds.value = []
  
  try {
    // Parallel fetch: All users and Current role members
    const [usersRes, membersRes] = await Promise.all([
      axios.get('/api/portal/management/users?size=1000'), // Large size to get all
      axios.get(`/api/portal/management/roles/${role.id}/users`)
    ])
    
    allUsers.value = usersRes.data.items || []
    const memberIds = membersRes.data || []
    roleMembers.value = allUsers.value.filter(u => memberIds.includes(u.id))
  } catch (e) {
    showToast('获取成员数据失败', 'error')
  } finally {
    loadingMembers.value = false
  }
}

const toggleMemberSelection = (id: number) => {
  const idx = selectedMemberIds.value.indexOf(id)
  if (idx > -1) selectedMemberIds.value.splice(idx, 1)
  else selectedMemberIds.value.push(id)
}

const toggleInSelectedSelection = (id: number) => {
  const idx = selectedInSelectedIds.value.indexOf(id)
  if (idx > -1) selectedInSelectedIds.value.splice(idx, 1)
  else selectedInSelectedIds.value.push(id)
}

const moveToSelected = () => {
  const usersToMove = allUsers.value.filter(u => selectedMemberIds.value.includes(u.id))
  roleMembers.value = [...roleMembers.value, ...usersToMove]
  selectedMemberIds.value = []
}

const moveToAvailable = () => {
  roleMembers.value = roleMembers.value.filter(m => !selectedInSelectedIds.value.includes(m.id))
  selectedInSelectedIds.value = []
}

const saveMembers = async () => {
  submittingMembers.value = true
  try {
    const userIds = roleMembers.value.map(m => m.id)
    await axios.put(`/api/portal/management/roles/${currentRole.value.id}/users`, { user_ids: userIds })
    showToast('成员分配更新成功', 'success')
    showMemberModal.value = false
  } catch (e: any) {
    showToast(e.response?.data?.detail || '保存失败', 'error')
  } finally {
    submittingMembers.value = false
  }
}

// Selection State
const selectedMenus = ref<string[]>([])
const selectedElements = ref<string[]>([])
const selectedResources = ref<string[]>([])
const selectedDataSources = ref<string[]>([])
const selectedDataTables = ref<string[]>([])

// Data Asset State
const allDataSources = ref<any[]>([])
const expandedDS = ref<string | null>(null)
const currentTables = ref<any[]>([])
const loadingTables = ref(false)
const tableSearch = ref('')

const filteredTables = computed(() => {
  if (!tableSearch.value) return currentTables.value
  return currentTables.value.filter(t => (typeof t === 'string' ? t : t.name).toLowerCase().includes(tableSearch.value.toLowerCase()))
})

// Resource Meta State
const availableResources = ref<any[]>([])
const groupedResources = computed(() => {
  const groups: Record<string, any[]> = {}
  availableResources.value.forEach((res: any) => {
    if (!groups[res.group]) groups[res.group] = []
    groups[res.group]!.push(res)
  })
  return groups
})

const fetchAvailableResources = async () => {
  try {
    const apiKey = localStorage.getItem('api_key')
    const response = await axios.get('/api/portal/meta/resources', {
      headers: { 'X-API-Key': apiKey }
    })
    availableResources.value = response.data.map((r: any) => ({
      id: r.resource_key,
      name: r.resource_name,
      group: r.resource_group || '其他'
    }))
  } catch (e) { console.error(e) }
}

const toggleGroupSelection = (resources: any[]) => {
  const allSelected = resources.every(r => selectedResources.value.includes(r.id))
  if (allSelected) {
    const idsToRemove = resources.map(r => r.id)
    selectedResources.value = selectedResources.value.filter(id => !idsToRemove.includes(id))
  } else {
    resources.forEach(r => { if (!selectedResources.value.includes(r.id)) selectedResources.value.push(r.id) })
  }
}

const isGroupAllSelected = (resources: any[]) => resources.length > 0 && resources.every(r => selectedResources.value.includes(r.id))

const toggleDSExpand = async (dsName: string) => {
  if (expandedDS.value === dsName) {
    expandedDS.value = null
    return
  }
  
  expandedDS.value = dsName
  loadingTables.value = true
  tableSearch.value = ''
  try {
    const res = await axios.post('/api/portal/meta/datasource/tables', { data_source: dsName })
    currentTables.value = res.data.tables || []
  } catch (e) {
    showToast('获取表列表失败', 'error')
    currentTables.value = []
  } finally {
    loadingTables.value = false
  }
}

const isDSAllTables = (dsName: string) => selectedDataTables.value.includes(`ds:${dsName}:table:*`)

const setDSAllTables = (dsName: string) => {
  const allKey = `ds:${dsName}:table:*`
  if (isDSAllTables(dsName)) {
    selectedDataTables.value = selectedDataTables.value.filter(k => k !== allKey)
  } else {
    // 选中 ALL 时，清除该 DS 下的所有具体表勾选，保持数据整洁
    selectedDataTables.value = selectedDataTables.value.filter(k => !k.startsWith(`ds:${dsName}:table:`))
    selectedDataTables.value.push(allKey)
  }
}

const fetchAllDataSources = async () => {
  try {
    const res = await axios.get('/api/portal/datasource/datasources')
    allDataSources.value = res.data
  } catch (e) { console.error(e) }
}

// Watch for data source deselection to auto-remove tables
watch(selectedDataSources, (newVal, oldVal) => {
  if (!oldVal) return
  const removedDS = oldVal.filter(ds => !newVal.includes(ds))
  if (removedDS.length > 0) {
    removedDS.forEach(dsCode => {
      // dsCode is "ds:name"
      // Remove all tables starting with "ds:name:table:"
      selectedDataTables.value = selectedDataTables.value.filter(t => !t.startsWith(`${dsCode}:table:`))
      
      // Close expanded panel if it was the removed one
      const dsName = dsCode.replace('ds:', '')
      if (expandedDS.value === dsName) expandedDS.value = null
    })
  }
})

// Watch for menu deselection to auto-remove children elements
watch(selectedMenus, (newVal, oldVal) => {
  if (!oldVal) return
  const removedMenus = oldVal.filter(m => !newVal.includes(m))
  if (removedMenus.length > 0) {
    removedMenus.forEach(menuId => {
      const menuNode = MENU_TREE.find(m => m.id === menuId)
      if (menuNode && menuNode.children) {
        const childIds = menuNode.children.map(c => c.id)
        selectedElements.value = selectedElements.value.filter(eid => !childIds.includes(eid))
      }
    })
  }
})

const fetchRoles = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portal/management/roles')
    roles.value = res.data
  } finally { loading.value = false }
}

const openCreateDialog = () => {
  isEdit.value = false
  activeTab.value = 'info'
  formData.value = { 
    id: null, 
    role_name: '', 
    role_code: '', 
    description: '', 
    rate_limit: null,
    masking_strategy: 'GLOBAL'
  }

  selectedMenus.value = []



    selectedElements.value = []



    selectedResources.value = []



    selectedDataSources.value = []



    selectedDataTables.value = []



    expandedDS.value = null



    showEditModal.value = true



  }



  



const editRole = async (role: any) => {
  isEdit.value = true
  activeTab.value = 'info'
  formData.value = { 
    id: role.id, 
    role_name: role.role_name, 
    role_code: role.role_code, 
    description: role.description,
    rate_limit: role.rate_limit,
    masking_strategy: role.masking_strategy || 'GLOBAL'
  }





  

  // Fetch specific permissions for this role
  try {
    const res = await axios.get(`/api/portal/management/roles/${role.id}/permissions`)
    selectedMenus.value = res.data.menus || []
    selectedElements.value = res.data.elements || []
    selectedResources.value = res.data.resources || []
    selectedDataSources.value = res.data.datasources || []
    selectedDataTables.value = res.data.data_tables || []
  } catch (e) {
    selectedMenus.value = []
    selectedElements.value = []
    selectedResources.value = []
    selectedDataSources.value = []
    selectedDataTables.value = []
  }

  showEditModal.value = true
}



const saveRole = async () => {

  if (!formData.value.role_name || !formData.value.role_code) return showToast('请填写必填项', 'warning')

  submitting.value = true

  try {

    // 1. Save Basic Info

    let roleId = formData.value.id

    if (isEdit.value) {

      await axios.put(`/api/portal/management/roles/${roleId}`, formData.value)

    } else {

      await axios.post('/api/portal/management/roles', formData.value)

    }



    // 2. Save Permissions (Only if we have a roleId)

    if (!isEdit.value) {

        await fetchRoles()

        const newRole = roles.value.find(r => r.role_code === formData.value.role_code)

        if (newRole) roleId = newRole.id

    }



            if (roleId) {
              // 统一处理所有 UI 权限：根据 ID 前缀自动归类到菜单或功能
              const allUiIds = [...selectedMenus.value, ...selectedElements.value]
              const finalMenus = allUiIds.filter(id => id.startsWith('menu:'))
              const finalElements = allUiIds.filter(id => id.startsWith('element:'))

              await axios.put(`/api/portal/management/roles/${roleId}/permissions`, {
                menus: Array.from(new Set(finalMenus)),
                elements: Array.from(new Set(finalElements)),
                resources: selectedResources.value,
                datasources: selectedDataSources.value,
                data_tables: selectedDataTables.value
              })
            }



    



    showToast('角色权限更新成功', 'success')
    showEditModal.value = false
    fetchRoles()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '操作失败', 'error')
  } finally { submitting.value = false }
}

const confirmDelete = (role: any) => {
  roleToDelete.value = role
  showDeleteModal.value = true
}

const executeDeleteRole = async () => {
  if (!roleToDelete.value) return
  try {
    await axios.delete(`/api/portal/management/roles/${roleToDelete.value.id}`)
    showToast('删除成功', 'success')
    showDeleteModal.value = false
    fetchRoles()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '删除失败', 'error')
  }
}

const formatDate = (d: string) => d ? new Date(d).toLocaleString('zh-CN', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'}) : '-'

onMounted(() => {
  fetchRoles()
  fetchAvailableResources()
  fetchAllDataSources()
})

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>