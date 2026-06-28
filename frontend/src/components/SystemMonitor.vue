<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from '../utils/axios'
import { 
  ServerIcon, CpuChipIcon, CircleStackIcon, 
  ClockIcon, UserGroupIcon 
} from '@heroicons/vue/24/outline'

const loading = ref(false)
const serverStats = ref<any>(null)
const redisStats = ref<any>(null)
let refreshTimer: any = null

const fetchServer = async () => {
  try {
    const res = await axios.get('/api/portal/monitor/server')
    serverStats.value = res.data
  } catch (e) { console.error(e) }
}

const fetchRedis = async () => {
  try {
    const res = await axios.get('/api/portal/monitor/redis')
    redisStats.value = res.data
  } catch (e) { console.error(e) }
}

const fetchData = async () => {
  loading.value = true
  await Promise.all([fetchServer(), fetchRedis()])
  loading.value = false
}

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchData()
  refreshTimer = setInterval(fetchData, 5000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Server Resources -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6" v-if="serverStats">
      <!-- CPU -->
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10"><CpuChipIcon class="w-24 h-24" /></div>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-500 font-bold uppercase text-xs tracking-wider">CPU 使用率</h3>
          <span class="text-2xl font-black text-gray-800">{{ serverStats.cpu }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
          <div class="bg-blue-500 h-2 rounded-full transition-all duration-500" :style="{ width: `${serverStats.cpu}%` }"></div>
        </div>
      </div>

      <!-- Memory -->
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10"><ServerIcon class="w-24 h-24" /></div>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-500 font-bold uppercase text-xs tracking-wider">内存使用</h3>
          <div class="text-right">
            <span class="text-2xl font-black text-gray-800">{{ serverStats.memory.percent }}%</span>
            <p class="text-xs text-gray-400">{{ formatBytes(serverStats.memory.used) }} / {{ formatBytes(serverStats.memory.total) }}</p>
          </div>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
          <div class="bg-purple-500 h-2 rounded-full transition-all duration-500" :style="{ width: `${serverStats.memory.percent}%` }"></div>
        </div>
      </div>

      <!-- Disk -->
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10"><CircleStackIcon class="w-24 h-24" /></div>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-gray-500 font-bold uppercase text-xs tracking-wider">磁盘使用</h3>
          <div class="text-right">
            <span class="text-2xl font-black text-gray-800">{{ serverStats.disk.percent }}%</span>
            <p class="text-xs text-gray-400">{{ formatBytes(serverStats.disk.used) }} / {{ formatBytes(serverStats.disk.total) }}</p>
          </div>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
          <div class="bg-emerald-500 h-2 rounded-full transition-all duration-500" :style="{ width: `${serverStats.disk.percent}%` }"></div>
        </div>
      </div>
    </div>

    <!-- Redis Stats -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden" v-if="redisStats">
      <div class="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
        <div class="flex items-center">
          <div class="w-2 h-2 rounded-full mr-2" :class="redisStats.status === 'connected' ? 'bg-green-500' : 'bg-red-500'"></div>
          <h3 class="font-bold text-gray-800">Redis 状态监控</h3>
        </div>
        <span class="text-xs text-gray-500 font-mono">v{{ redisStats.version }}</span>
      </div>
      
      <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Hit Rate -->
        <div class="text-center">
          <div class="relative w-32 h-32 mx-auto mb-4 flex items-center justify-center">
            <svg class="w-full h-full transform -rotate-90">
              <circle cx="64" cy="64" r="60" stroke="#f3f4f6" stroke-width="8" fill="transparent" />
              <circle cx="64" cy="64" r="60" stroke="#ef4444" stroke-width="8" fill="transparent" :stroke-dasharray="377" :stroke-dashoffset="377 - (377 * redisStats.hit_rate) / 100" class="transition-all duration-1000" />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-3xl font-black text-gray-800">{{ redisStats.hit_rate }}%</span>
              <span class="text-xs text-gray-400 uppercase font-bold">命中率</span>
            </div>
          </div>
        </div>

        <!-- OPS -->
        <div class="flex flex-col justify-center">
          <div class="mb-6">
            <h4 class="text-xs text-gray-400 uppercase font-bold mb-1">实时 OPS</h4>
            <span class="text-3xl font-mono text-gray-800">{{ redisStats.ops_per_sec }}</span>
            <span class="text-xs text-gray-400 ml-1">ops/sec</span>
          </div>
          <div>
            <h4 class="text-xs text-gray-400 uppercase font-bold mb-1">Key 总数</h4>
            <span class="text-3xl font-mono text-gray-800">{{ redisStats.total_keys }}</span>
          </div>
        </div>

        <!-- Memory -->
        <div class="flex flex-col justify-center space-y-4">
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-500 font-bold">内存使用</span>
              <span class="text-gray-800 font-mono">{{ redisStats.used_memory_human }}</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5">
              <div class="bg-orange-400 h-1.5 rounded-full" style="width: 20%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-500 font-bold">RSS 内存</span>
              <span class="text-gray-800 font-mono">{{ redisStats.used_memory_rss_human }}</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5">
              <div class="bg-orange-300 h-1.5 rounded-full" style="width: 25%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-500 font-bold">Max Memory</span>
              <span class="text-gray-800 font-mono">{{ redisStats.max_memory_human }}</span>
            </div>
          </div>
        </div>

        <!-- Info -->
        <div class="flex flex-col justify-center bg-gray-50 rounded-xl p-4 space-y-3">
          <div class="flex items-center">
            <ClockIcon class="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <p class="text-xs text-gray-400">运行时长</p>
              <p class="font-bold text-gray-700">{{ redisStats.uptime_days }} 天</p>
            </div>
          </div>
          <div class="flex items-center">
            <UserGroupIcon class="w-5 h-5 text-gray-400 mr-3" />
            <div>
              <p class="text-xs text-gray-400">连接客户端</p>
              <p class="font-bold text-gray-700">{{ redisStats.connected_clients }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
