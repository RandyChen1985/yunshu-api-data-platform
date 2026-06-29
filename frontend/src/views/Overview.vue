<template>
  <div class="space-y-6">
    <!-- Toast Notifications -->
    <Toast
      v-for="(toast, index) in toasts"
      :key="index"
      :message="toast.message"
      :type="toast.type"
      :duration="toast.duration"
      @close="removeToast(index)"
      :style="{ top: `${4 + index * 5}rem` }"
    />

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-lg sm:text-2xl font-semibold text-gray-900">
        {{ userInfo?.role === "admin" ? "系统概览" : "我的工作台" }}
      </h1>
      <div class="flex items-center space-x-3">
        <!-- Auto Refresh Toggle -->
        <div class="flex items-center bg-white border border-gray-300 rounded-md shadow-sm px-3 py-1.5 space-x-2">
          <span class="text-xs font-medium text-gray-500">自动刷新</span>
          <button 
            @click="isAutoRefresh = !isAutoRefresh"
            class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="isAutoRefresh ? 'bg-primary' : 'bg-gray-200'"
          >
            <span 
              class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="isAutoRefresh ? 'translate-x-4' : 'translate-x-0'"
            />
          </button>
          <transition name="fade">
            <span v-if="isAutoRefresh" class="text-[10px] font-mono text-primary w-6 text-center">{{ countdown }}s</span>
          </transition>
        </div>

        <button
          @click="refreshData"
          :disabled="loading"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 transition-all duration-200"
        >
          <svg
            class="-ml-1 mr-2 h-5 w-5 text-gray-500"
            :class="{ 'animate-spin': loading }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {{ loading ? '同步中...' : '刷新' }}
        </button>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading && !stats" class="space-y-6 animate-pulse">
      <!-- Skeleton Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div v-for="i in 5" :key="i" class="bg-white rounded-lg shadow p-6 h-24">
          <div class="flex items-center">
            <div class="h-10 w-10 bg-gray-200 rounded-md"></div>
            <div class="ml-4 flex-1 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-1/2"></div>
              <div class="h-5 bg-gray-200 rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </div>
      <!-- Skeleton Chart -->
      <div class="bg-white rounded-lg shadow p-6 h-96">
        <div class="flex justify-between items-center mb-4">
          <div class="h-6 bg-gray-200 rounded w-1/4"></div>
          <div class="h-4 bg-gray-200 rounded w-1/6"></div>
        </div>
        <div class="h-full bg-gray-100 rounded"></div>
      </div>
      <!-- Skeleton Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i" class="h-20 bg-white rounded-lg shadow border-2 border-gray-50"></div>
      </div>
    </div>

    <!-- Admin View -->
    <template v-else-if="userInfo?.role === 'admin' || hasMenu('menu:overview')">

      <!-- Statistics Cards -->
      <transition-group 
        tag="div" 
        enter-active-class="transition-all duration-500 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
      >
        <!-- Total Users -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  总用户数
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.total_users || 0 }}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- Active Users -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  活跃用户
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.active_users || 0 }}
                </dd>
                <dd class="text-xs text-gray-400">最近7天</dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- API Calls -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-purple-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  API 调用
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.api_calls?.total || 0 }}
                </dd>
                <dd class="text-xs text-gray-400">
                  <select
                    v-model="period"
                    @change="fetchAdminStats"
                    class="text-xs border-none p-0 focus:ring-0 cursor-pointer"
                  >
                    <option value="today">今日</option>
                    <option value="week">本周</option>
                    <option value="month">本月</option>
                  </select>
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- Avg Latency -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  平均耗时
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.avg_response_time || 0 }} <span class="text-xs font-normal text-gray-500">ms</span>
                </dd>
                <dd class="text-xs text-gray-400">系统平均响应</dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- Success Rate -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div
              class="flex-shrink-0 rounded-md p-3"
              :class="
                (stats?.success_rate || 0) >= 90 ? 'bg-green-100' : 'bg-red-100'
              "
            >
              <svg
                class="h-6 w-6"
                :class="
                  (stats?.success_rate || 0) >= 90
                    ? 'text-green-600'
                    : 'text-red-600'
                "
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  成功率
                </dt>
                <dd
                  class="text-lg font-semibold"
                  :class="
                    (stats?.success_rate || 0) >= 90
                      ? 'text-green-600'
                      : 'text-red-600'
                  "
                >
                  {{ stats?.success_rate || 0 }}%
                </dd>
                <dd class="text-xs text-gray-400">
                  {{ stats?.api_calls?.success || 0 }} /
                  {{ stats?.api_calls?.total || 0 }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </transition-group>

      <!-- Trend Chart (New Section) -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 sm:mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:space-x-4">
            <h2 class="text-sm sm:text-lg font-medium text-gray-900 shrink-0">请求趋势</h2>
            <!-- Tab Switcher -->
            <div class="flex p-0.5 sm:p-1 bg-gray-100 rounded-lg w-fit">
              <button 
                @click="trendTimeframe = '24h'"
                class="px-2 sm:px-4 py-0.5 sm:py-1 text-xs sm:text-sm font-medium rounded-md transition-all duration-200"
                :class="trendTimeframe === '24h' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              >
                近 24 小时
              </button>
              <button 
                @click="trendTimeframe = '7d'"
                class="px-2 sm:px-4 py-0.5 sm:py-1 text-xs sm:text-sm font-medium rounded-md transition-all duration-200"
                :class="trendTimeframe === '7d' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              >
                近 7 天
              </button>
            </div>
          </div>
          <span class="text-[10px] sm:text-xs text-gray-400 shrink-0">更新时间: {{ new Date().toLocaleTimeString() }}</span>
        </div>
        <div class="h-80 w-full relative">
           <!-- Chart Loading Overlay -->
           <div v-if="loadingTrend" class="absolute inset-0 z-10 bg-white bg-opacity-60 flex items-center justify-center">
              <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
           </div>
           <v-chart class="h-full w-full" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- Interface Resource Analysis (New) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Hot Ranking Bar Chart -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 min-w-0">
              <h2 class="text-sm sm:text-lg font-medium text-gray-900 shrink-0">活跃排行 (TOP 10)</h2>
              <!-- Ranking Tab -->
              <div class="flex p-0.5 bg-gray-100 rounded-lg text-xs w-fit">
                <button 
                  @click="rankingType = 'resource'"
                  class="px-3 py-1 font-medium rounded-md transition-all duration-200"
                  :class="rankingType === 'resource' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                  按接口
                </button>
                <button 
                  @click="rankingType = 'user'"
                  class="px-3 py-1 font-medium rounded-md transition-all duration-200"
                  :class="rankingType === 'user' ? 'bg-white text-green-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                  按用户
                </button>
              </div>
            </div>
            <div class="flex space-x-2 shrink-0">
               <div class="flex items-center text-xs text-gray-500">
                  <span class="w-3 h-3 rounded-sm mr-1" :class="rankingType === 'resource' ? 'bg-indigo-500' : 'bg-green-500'"></span>
                  调用量
               </div>
            </div>
          </div>
          <div class="h-80 w-full relative">
            <div v-if="loadingResources || loadingUserRanking" class="absolute inset-0 z-10 bg-white bg-opacity-60 flex items-center justify-center">
                <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
            <v-chart v-if="(rankingType === 'resource' ? resourceStats : userRanking).length > 0" class="h-full w-full" :option="resourceChartOption" autoresize />
            <div v-else class="h-full flex items-center justify-center text-gray-400 text-sm">暂无数据</div>
          </div>
        </div>

        <!-- Resource Performance Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-sm sm:text-lg font-medium text-gray-900">接口性能分布</h3>
          </div>
          <div class="flex-1 overflow-auto custom-scrollbar">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">接口</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">耗时(ms)</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">错误率</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="res in resourceStats" :key="res.endpoint" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 whitespace-nowrap">
                    <div class="text-xs font-mono text-gray-600 truncate max-w-[140px]" :title="res.endpoint">
                      {{ res.endpoint }}
                    </div>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-right">
                    <span class="text-xs font-semibold" :class="res.avg_latency > 500 ? 'text-red-600' : 'text-gray-900'">
                      {{ res.avg_latency }}
                    </span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-right">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" 
                      :class="res.error_rate > 5 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'">
                      {{ res.error_rate }}%
                    </span>
                  </td>
                </tr>
                <tr v-if="resourceStats.length === 0">
                  <td colspan="3" class="px-4 py-8 text-center text-sm text-gray-400">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="px-4 py-3 bg-gray-50 border-t border-gray-200 text-[10px] text-gray-400">
            * 仅展示调用量前 10 的接口
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-sm sm:text-lg font-medium text-gray-900 mb-4">快捷操作</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <router-link
            to="/dashboard/users"
            class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <svg
              class="h-8 w-8 text-blue-600 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
            <div>
              <div class="font-medium text-gray-900">创建用户</div>
              <div class="text-sm text-gray-500">管理系统用户</div>
            </div>
          </router-link>

          <router-link
            to="/dashboard/audit"
            class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <svg
              class="h-8 w-8 text-blue-600 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <div>
              <div class="font-medium text-gray-900">查看日志</div>
              <div class="text-sm text-gray-500">审计日志管理</div>
            </div>
          </router-link>

          <router-link
            to="/dashboard/playground"
            class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <svg
              class="h-8 w-8 text-blue-600 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <div>
              <div class="font-medium text-gray-900">API 调试</div>
              <div class="text-sm text-gray-500">在线调试工具</div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Recent Activities -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Users -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-sm sm:text-lg font-medium text-gray-900">最新用户</h3>
          </div>
          <div class="p-6">
            <div v-if="activities?.recent_users?.length > 0" class="space-y-4">
              <div
                v-for="user in activities.recent_users"
                :key="user.user_name"
                class="flex items-center"
              >
                <div
                  class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold"
                >
                  {{ user.user_name.charAt(0).toUpperCase() }}
                </div>
                <div class="ml-4 flex-1">
                  <p class="text-sm font-medium text-gray-900">
                    {{ user.user_name }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ user.role === "admin" ? "管理员" : "普通用户" }}
                  </p>
                </div>
                <div class="text-xs text-gray-400">
                  {{ formatDate(user.created_at) }}
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>暂无数据</p>
            </div>
          </div>
        </div>

        <!-- Recent API Calls -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-sm sm:text-lg font-medium text-gray-900">最近调用</h3>
          </div>
          <div class="p-6">
            <div v-if="activities?.recent_calls?.length > 0" class="space-y-3">
              <div
                v-for="call in activities.recent_calls.slice(0, 5)"
                :key="call.id"
                class="flex items-center text-sm"
              >
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mr-2"
                  :class="{
                    'bg-green-100 text-green-800':
                      call.status_code >= 200 && call.status_code < 300,
                    'bg-red-100 text-red-800': call.status_code >= 400,
                  }"
                >
                  {{ call.status_code }}
                </span>
                <span
                  class="text-gray-600 font-mono text-xs flex-1 truncate"
                  :title="call.endpoint"
                >
                  {{ call.endpoint }}
                </span>
                <span class="text-xs text-gray-400 ml-2">
                  {{ formatDate(call.created_at) }}
                </span>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>暂无数据</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- User View -->
    <template v-else>
      <!-- User Statistics Cards -->
      <transition-group 
        tag="div" 
        enter-active-class="transition-all duration-500 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <!-- API Key Status -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div
              class="flex-shrink-0 rounded-md p-3"
              :class="
                stats?.api_key_status === 'active'
                  ? 'bg-green-100'
                  : 'bg-red-100'
              "
            >
              <svg
                class="h-6 w-6"
                :class="
                  stats?.api_key_status === 'active'
                    ? 'text-green-600'
                    : 'text-red-600'
                "
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  API Key
                </dt>
                <dd
                  class="text-lg font-semibold"
                  :class="
                    stats?.api_key_status === 'active'
                      ? 'text-green-600'
                      : 'text-red-600'
                  "
                >
                  {{ stats?.api_key_status === "active" ? "正常" : "已禁用" }}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- My API Calls -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  我的调用
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.api_calls?.total || 0 }}
                </dd>
                <dd class="text-xs text-gray-400">
                  <select
                    v-model="period"
                    @change="fetchUserStats"
                    class="text-xs border-none p-0 focus:ring-0 cursor-pointer"
                  >
                    <option value="today">今日</option>
                    <option value="week">本周</option>
                    <option value="month">本月</option>
                  </select>
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- Avg Response Time -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-100 rounded-md p-3">
              <svg
                class="h-6 w-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  平均响应
                </dt>
                <dd class="text-lg font-semibold text-gray-900">
                  {{ stats?.avg_response_time || 0 }} ms
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <!-- Success Rate -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div
              class="flex-shrink-0 rounded-md p-3"
              :class="
                (stats?.success_rate || 0) >= 90 ? 'bg-green-100' : 'bg-red-100'
              "
            >
              <svg
                class="h-6 w-6"
                :class="
                  (stats?.success_rate || 0) >= 90
                    ? 'text-green-600'
                    : 'text-red-600'
                "
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  成功率
                </dt>
                <dd
                  class="text-lg font-semibold"
                  :class="
                    (stats?.success_rate || 0) >= 90
                      ? 'text-green-600'
                      : 'text-red-600'
                  "
                >
                  {{ stats?.success_rate || 0 }}%
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </transition-group>

      <!-- User Trend Chart (New Section) -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 sm:mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:space-x-4">
            <h2 class="text-sm sm:text-lg font-medium text-gray-900 shrink-0">请求趋势</h2>
            <div class="flex p-0.5 sm:p-1 bg-gray-100 rounded-lg w-fit">
              <button 
                @click="trendTimeframe = '24h'"
                class="px-2 sm:px-4 py-0.5 sm:py-1 text-xs sm:text-sm font-medium rounded-md transition-all duration-200"
                :class="trendTimeframe === '24h' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              >
                近 24 小时
              </button>
              <button 
                @click="trendTimeframe = '7d'"
                class="px-2 sm:px-4 py-0.5 sm:py-1 text-xs sm:text-sm font-medium rounded-md transition-all duration-200"
                :class="trendTimeframe === '7d' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              >
                近 7 天
              </button>
            </div>
          </div>
          <span class="text-[10px] sm:text-xs text-gray-400 shrink-0">更新时间: {{ new Date().toLocaleTimeString() }}</span>
        </div>
        <div class="h-80 w-full relative">
           <div v-if="loadingTrend" class="absolute inset-0 z-10 bg-white bg-opacity-60 flex items-center justify-center">
              <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
           </div>
           <v-chart class="h-full w-full" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- Interface Resource Analysis (User View) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-lg shadow p-4 sm:p-6">
          <h2 class="text-sm sm:text-lg font-medium text-gray-900 mb-4">我的活跃接口 (TOP 10)</h2>
          <div class="h-80 w-full relative">
            <div v-if="loadingResources" class="absolute inset-0 z-10 bg-white bg-opacity-60 flex items-center justify-center">
                <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
            <v-chart v-if="resourceStats.length > 0" class="h-full w-full" :option="resourceChartOption" autoresize />
            <div v-else class="h-full flex items-center justify-center text-gray-400 text-sm">暂无数据</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-sm sm:text-lg font-medium text-gray-900">我的接口性能</h3>
          </div>
          <div class="flex-1 overflow-auto custom-scrollbar">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">接口</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">耗时(ms)</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">错误率</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="res in resourceStats" :key="res.endpoint" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 whitespace-nowrap">
                    <div class="text-xs font-mono text-gray-600 truncate max-w-[140px]" :title="res.endpoint">
                      {{ res.endpoint }}
                    </div>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-right">
                    <span class="text-xs font-semibold" :class="res.avg_latency > 500 ? 'text-red-600' : 'text-gray-900'">
                      {{ res.avg_latency }}
                    </span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-right">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" 
                      :class="res.error_rate > 5 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'">
                      {{ res.error_rate }}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Quick Start -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-sm sm:text-lg font-medium text-gray-900 mb-4">快速开始</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="border-2 border-gray-200 rounded-lg p-4">
            <div class="flex items-center mb-3">
              <svg
                class="h-6 w-6 text-blue-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
              <h3 class="font-medium text-gray-900">API 文档</h3>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              查看完整的 API 接口文档和使用说明
            </p>
            <a
              :href="`${API_BASE}/docs`"
              target="_blank"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              查看文档 →
            </a>
          </div>

          <div class="border-2 border-gray-200 rounded-lg p-4">
            <div class="flex items-center mb-3">
              <svg
                class="h-6 w-6 text-blue-600 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <h3 class="font-medium text-gray-900">API 调试</h3>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              在线测试 API 接口，快速验证功能
            </p>
            <router-link
              to="/dashboard/playground"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              开始调试 →
            </router-link>
          </div>
        </div>
      </div>

      <!-- My Recent Calls -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-sm sm:text-lg font-medium text-gray-900">我的最近调用</h3>
        </div>
        <div class="p-6">
          <div v-if="activities?.recent_calls?.length > 0" class="space-y-3">
            <div
              v-for="call in activities.recent_calls"
              :key="call.id"
              class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
            >
              <div class="flex items-center flex-1">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-3"
                  :class="{
                    'bg-green-100 text-green-800':
                      call.status_code >= 200 && call.status_code < 300,
                    'bg-yellow-100 text-yellow-800':
                      call.status_code >= 300 && call.status_code < 400,
                    'bg-red-100 text-red-800': call.status_code >= 400,
                  }"
                >
                  {{ call.status_code }}
                </span>
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 font-mono mr-3"
                >
                  {{ call.method }}
                </span>
                <span
                  class="text-sm text-gray-600 font-mono flex-1 truncate"
                  :title="call.endpoint"
                >
                  {{ call.endpoint }}
                </span>
              </div>
              <div class="flex items-center space-x-4 ml-4">
                <span class="text-sm text-gray-500"
                  >{{ call.process_time_ms?.toFixed(2) }} ms</span
                >
                <span class="text-xs text-gray-400">{{
                  formatDate(call.created_at)
                }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-12 text-gray-500">
            <svg
              class="mx-auto h-12 w-12 text-gray-300 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p class="text-sm">暂无调用记录</p>
            <p class="text-xs text-gray-400 mt-1">
              开始使用 API 后，这里会显示最近的调用记录
            </p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import axios from "axios";
import Toast from "../components/Toast.vue";

// ECharts
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, BarChart, PieChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from "echarts/components";
import VChart from "vue-echarts";

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

const apiKey = ref(localStorage.getItem("api_key") || "");
const userInfo = ref<any>(null);
const loading = ref(false);
const period = ref("today");

const stats = ref<any>(null);
const activities = ref<any>(null);

// Auto Refresh State
const isAutoRefresh = ref(false);
const refreshInterval = 30; // 30 seconds
const countdown = ref(refreshInterval);
let autoRefreshTimer: any = null;
let countdownTimer: any = null;

const startAutoRefresh = () => {
  stopAutoRefresh();
  countdown.value = refreshInterval;
  
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      refreshData();
      countdown.value = refreshInterval;
    }
  }, 1000);
};

const stopAutoRefresh = () => {
  if (countdownTimer) clearInterval(countdownTimer);
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
};

watch(isAutoRefresh, (val) => {
  if (val) {
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
});

// Resource Stats State
const resourceStats = ref<any[]>([]);
const loadingResources = ref(false);

// --- Ranking State (Added) ---
const rankingType = ref<'resource' | 'user'>('resource');
const userRanking = ref<any[]>([]);
const loadingUserRanking = ref(false);

const fetchUserRanking = async () => {
  if (userInfo.value?.role !== 'admin') return;
  loadingUserRanking.value = true;
  try {
    const response = await axios.get(`${API_BASE}/api/portal/dashboard/user-ranking`, {
      headers: { "X-API-Key": apiKey.value },
      params: { period: period.value, limit: 10 },
    });
    userRanking.value = response.data;
  } catch (error) {
    console.error("Failed to fetch user ranking:", error);
  } finally {
    loadingUserRanking.value = false;
  }
};
// -----------------------------

const fetchResourceStats = async () => {
  loadingResources.value = true;
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/resource-stats`,
      {
        headers: { "X-API-Key": apiKey.value },
        params: { period: period.value, limit: 10 },
      }
    );
    resourceStats.value = response.data;
  } catch (error) {
    console.error("Failed to fetch resource stats:", error);
  } finally {
    loadingResources.value = false;
  }
};

// Trends State
const trendTimeframe = ref<"24h" | "7d">("24h");
const trends24h = ref<any[]>([]);
const trends7d = ref<any[]>([]);
const loadingTrend = ref(false);

const toasts = ref<
  Array<{
    message: string;
    type: "success" | "error" | "warning" | "info";
    duration?: number;
  }>
>([]);

const addToast = (
  message: string,
  type: "success" | "error" | "warning" | "info" = "info",
  duration = 3000
) => {
  toasts.value.push({ message, type, duration });
};

const removeToast = (index: number) => {
  toasts.value.splice(index, 1);
};

const fetchTrends24h = async () => {
  loadingTrend.value = true;
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/api-trends-24h`,
      {
        headers: { "X-API-Key": apiKey.value },
      }
    );
    trends24h.value = response.data;
  } catch (error: any) {
    console.error("Failed to fetch 24h trends:", error);
  } finally {
    loadingTrend.value = false;
  }
};

const fetchTrends7d = async () => {
  loadingTrend.value = true;
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/api-trends`,
      {
        headers: { "X-API-Key": apiKey.value },
        params: { days: 7 }
      }
    );
    trends7d.value = response.data;
  } catch (error: any) {
    console.error("Failed to fetch 7d trends:", error);
  } finally {
    loadingTrend.value = false;
  }
};

const fetchActiveTrend = () => {
  if (trendTimeframe.value === "24h") {
    fetchTrends24h();
  } else {
    fetchTrends7d();
  }
};

watch(trendTimeframe, () => {
  fetchActiveTrend();
});

const chartOption = computed(() => {
  const is24h = trendTimeframe.value === "24h";
  const data = is24h ? trends24h.value : trends7d.value;
  
  return {
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(255, 255, 255, 0.9)",
      borderWidth: 1,
      borderColor: "#e5e7eb",
      textStyle: { color: "#374151" },
      formatter: (params: any[]) => {
        if (!params || params.length === 0) return "";
        const title = params[0].axisValue;
        let html = `<div class="font-medium mb-1">${title}</div>`;
        params.forEach(p => {
          html += `<div class="flex items-center justify-between space-x-4">
            <span class="flex items-center text-xs text-gray-500">
              <span class="w-2 h-2 rounded-full mr-1.5" style="background-color: ${p.color}"></span>
              ${p.seriesName}
            </span>
            <span class="text-sm font-semibold">${p.value}</span>
          </div>`;
        });
        return html;
      }
    },
    legend: {
      data: ["总请求量", "成功请求量"],
      bottom: 0,
      icon: "circle",
      itemWidth: 8,
      itemHeight: 8,
      textStyle: { color: "#6b7280", fontSize: 12 }
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: data.map((item: any) => is24h ? item.hour : item.date),
      axisLine: { lineStyle: { color: "#e5e7eb" } },
      axisLabel: { 
        color: "#9ca3af", 
        fontSize: 11,
        interval: is24h ? 1 : 0 // Show more labels for 7d
      },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#9ca3af", fontSize: 11 },
      splitLine: { lineStyle: { type: "dashed", color: "#f3f4f6" } },
    },
    series: [
      {
        name: "总请求量",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: data.map((item: any) => item.total_calls),
        itemStyle: { color: "#3b82f6" },
        lineStyle: { width: 3 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(59, 130, 246, 0.15)" },
              { offset: 1, color: "rgba(59, 130, 246, 0)" },
            ],
          },
        },
      },
      {
        name: "成功请求量",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: data.map((item: any) => item.success_calls),
        itemStyle: { color: "#10b981" },
        lineStyle: { width: 3 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(16, 185, 129, 0.15)" },
              { offset: 1, color: "rgba(16, 185, 129, 0)" },
            ],
          },
        },
      },
    ],
  };
});

const fetchAdminStats = async () => {
  loading.value = true;
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/admin-stats`,
      {
        headers: { "X-API-Key": apiKey.value },
        params: { period: period.value },
      }
    );
    stats.value = response.data;
  } catch (error: any) {
    addToast(error.response?.data?.detail || "加载统计数据失败", "error");
    console.error("Failed to fetch admin stats:", error);
  } finally {
    loading.value = false;
  }
};

const fetchUserStats = async () => {
  loading.value = true;
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/user-stats`,
      {
        headers: { "X-API-Key": apiKey.value },
        params: { period: period.value },
      }
    );
    stats.value = response.data;
  } catch (error: any) {
    addToast(error.response?.data?.detail || "加载统计数据失败", "error");
    console.error("Failed to fetch user stats:", error);
  } finally {
    loading.value = false;
  }
};

const fetchRecentActivities = async () => {
  try {
    const response = await axios.get(
      `${API_BASE}/api/portal/dashboard/recent-activities`,
      {
        headers: { "X-API-Key": apiKey.value },
        params: { limit: 10 },
      }
    );
    activities.value = response.data;
  } catch (error: any) {
    console.error("Failed to fetch recent activities:", error);
  }
};

const refreshData = async () => {
  if (userInfo.value?.role === "admin") {
    await fetchAdminStats();
    fetchUserRanking(); // Added
  } else {
    await fetchUserStats();
  }
  await fetchRecentActivities();
  fetchActiveTrend();
  fetchResourceStats();
};

// Top 10 Resources Chart Option
const resourceChartOption = computed(() => {
  const isResource = rankingType.value === 'resource';
  const rawData = isResource ? resourceStats.value : userRanking.value;
  const data = [...rawData].sort((a, b) => a.total_calls - b.total_calls);
  
  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      backgroundColor: "rgba(255, 255, 255, 0.9)",
      borderWidth: 1,
      borderColor: "#e5e7eb",
      formatter: (params: any[]) => {
        if (!params.length) return '';
        const p = params[0];
        const item = data[p.dataIndex];
        return `
          <div class="font-bold mb-1">${p.name}</div>
          <div class="text-xs text-gray-500">总调用: <span class="font-bold text-indigo-600">${item.total_calls}</span></div>
          <div class="text-xs text-gray-500">错误率: <span class="font-bold ${item.error_rate > 5 ? 'text-red-500' : 'text-green-600'}">${item.error_rate || 0}%</span></div>
        `;
      }
    },
    grid: {
      left: "3%",
      right: "8%",
      bottom: "3%",
      top: "3%",
      containLabel: true
    },
    xAxis: {
      type: "value",
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { type: "dashed", color: "#f3f4f6" } }
    },
    yAxis: {
      type: "category",
      data: data.map(item => {
        const name = isResource ? item.endpoint : item.user_name;
        return name.length > 20 ? name.substring(0, 17) + "..." : name;
      }),
      axisLine: { lineStyle: { color: "#e5e7eb" } },
      axisTick: { show: false },
      axisLabel: { color: "#4b5563", fontSize: 11 }
    },
    series: [
      {
        name: "总调用量",
        type: "bar",
        data: data.map(item => item.total_calls),
        itemStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: isResource ? "#6366f1" : "#10b981" },
              { offset: 1, color: isResource ? "#818cf8" : "#34d399" }
            ]
          },
          borderRadius: [0, 4, 4, 0]
        },
        barWidth: "60%"
      }
    ]
  };
});

import { onUnmounted } from "vue";
onUnmounted(() => {
  stopAutoRefresh();
});

const formatDate = (dateStr: string) => {
  if (!dateStr) return "-";
  
  // Fix Safari compatibility & Timezone
  let dateInput = typeof dateStr === 'string' ? dateStr.replace(' ', 'T') : dateStr;

  const date = new Date(dateInput);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // Less than 1 minute
  if (diff < 60000) {
    return "刚刚";
  }
  // Less than 1 hour
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`;
  }
  // Less than 1 day
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`;
  }
  // Less than 7 days
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)} 天前`;
  }

  // Otherwise show date
  return date.toLocaleDateString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const loadUserInfo = () => {
  const stored = localStorage.getItem("user_info");
  if (stored) {
    userInfo.value = JSON.parse(stored);
  }
};

const hasMenu = (menuCode: string) => {
  if (userInfo.value?.role === 'admin') return true;
  return userInfo.value?.permissions?.menus?.includes(menuCode);
};

onMounted(async () => {
  loadUserInfo();
  await refreshData();
});
</script>
