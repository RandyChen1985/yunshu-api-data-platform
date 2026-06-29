<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, PieChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const router = useRouter()
const loading = ref(true)
const periodDays = ref(30)
const data = ref<any>(null)

const fetchPanorama = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portal/catalog/panorama', { params: { days: periodDays.value } })
    data.value = res.data
  } catch (e: any) {
    if (e.response?.status === 403) {
      router.replace('/dashboard/403')
    }
  } finally {
    loading.value = false
  }
}

const trendOption = computed(() => {
  const trend = data.value?.calls_trend || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: trend.map((t: any) => t.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: trend.map((t: any) => t.calls), smooth: true, itemStyle: { color: '#6366f1' }, areaStyle: { color: 'rgba(99,102,241,0.1)' } }],
  }
})

const domainPieOption = computed(() => {
  const dist = data.value?.domain_distribution || []
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: dist.map((d: any) => ({ name: d.domain, value: d.count })),
      label: { formatter: '{b}: {c}' },
    }],
  }
})

const topBarOption = computed(() => {
  const top = data.value?.top_products?.slice(0, 8) || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 120, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: top.map((p: any) => p.display_name).reverse(), axisLabel: { width: 100, overflow: 'truncate' } },
    series: [{ type: 'bar', data: top.map((p: any) => p.calls_7d).reverse(), itemStyle: { color: '#818cf8' } }],
  }
})

const formatNum = (n: number) => {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  return n.toLocaleString()
}

onMounted(fetchPanorama)
</script>

<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">数据资产全景</h1>
        <p class="text-sm text-gray-500 mt-1">数据产品盘点、使用热度与治理健康度一览</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model.number="periodDays" class="border border-gray-200 rounded-lg px-3 py-2 text-sm" @change="fetchPanorama">
          <option :value="7">近 7 天</option>
          <option :value="30">近 30 天</option>
          <option :value="90">近 90 天</option>
        </select>
        <router-link to="/dashboard/catalog" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
          进入产品目录 →
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">加载中...</div>
    <template v-else-if="data">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <p class="text-xs text-gray-500 uppercase tracking-wide">已发布产品</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ data.published_count }}</p>
        </div>
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <p class="text-xs text-gray-500 uppercase tracking-wide">业务域</p>
          <p class="text-3xl font-bold text-indigo-600 mt-1">{{ data.domain_count }}</p>
        </div>
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <p class="text-xs text-gray-500 uppercase tracking-wide">数据源类型</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ Object.keys(data.datasource_types || {}).length }}</p>
        </div>
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <p class="text-xs text-gray-500 uppercase tracking-wide">总调用量</p>
          <p class="text-3xl font-bold text-purple-600 mt-1">{{ formatNum(data.total_calls) }}</p>
        </div>
        <div class="bg-white rounded-xl border p-5 shadow-sm col-span-2 lg:col-span-1">
          <p class="text-xs text-gray-500 uppercase tracking-wide">活跃消费方</p>
          <p class="text-3xl font-bold text-green-600 mt-1">{{ data.active_consumers }}</p>
        </div>
      </div>

      <!-- Alerts -->
      <div class="bg-amber-50 border border-amber-100 rounded-xl p-4 flex flex-wrap gap-6 text-sm">
        <span>⚠️ 零调用产品 <strong>{{ data.alerts?.zero_call_products?.length || 0 }}</strong> 个</span>
        <span>⚠️ 健康分偏低 <strong>{{ data.alerts?.low_health_products?.length || 0 }}</strong> 个</span>
        <span>⚠️ 信息不完整 <strong>{{ data.alerts?.incomplete_products?.length || 0 }}</strong> 个</span>
        <span>🆕 本月新增 <strong>{{ data.alerts?.new_this_month || 0 }}</strong> 个</span>
        <span class="text-gray-500">
          健康度：优 {{ data.health_summary?.good || 0 }} · 中 {{ data.health_summary?.medium || 0 }} · 待治理 {{ data.health_summary?.low || 0 }}
        </span>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <h3 class="text-sm font-bold text-gray-700 mb-4">调用趋势</h3>
          <VChart :option="trendOption" style="height: 260px" autoresize />
        </div>
        <div class="bg-white rounded-xl border p-5 shadow-sm">
          <h3 class="text-sm font-bold text-gray-700 mb-4">按业务域分布</h3>
          <VChart :option="domainPieOption" style="height: 260px" autoresize />
        </div>
      </div>

      <div class="bg-white rounded-xl border p-5 shadow-sm">
        <h3 class="text-sm font-bold text-gray-700 mb-4">热门产品 TOP</h3>
        <VChart :option="topBarOption" style="height: 280px" autoresize />
      </div>

      <!-- Incomplete products -->
      <div v-if="data.alerts?.incomplete_products?.length" class="bg-white rounded-xl border p-5 shadow-sm">
        <h3 class="text-sm font-bold text-gray-700 mb-3">需完善：缺少简介或负责人</h3>
        <div class="flex flex-wrap gap-2">
          <router-link
            v-for="p in data.alerts.incomplete_products"
            :key="p.product_key"
            :to="`/dashboard/catalog/${p.product_key}/edit`"
            class="text-xs bg-amber-50 border border-amber-100 px-3 py-1.5 rounded-lg hover:border-amber-300 text-gray-700"
          >
            {{ p.display_name }}
          </router-link>
        </div>
      </div>

      <!-- Zero call list -->
      <div v-if="data.alerts?.zero_call_products?.length" class="bg-white rounded-xl border p-5 shadow-sm">
        <h3 class="text-sm font-bold text-gray-700 mb-3">需关注：零调用产品</h3>
        <div class="flex flex-wrap gap-2">
          <router-link
            v-for="p in data.alerts.zero_call_products"
            :key="p.product_key"
            :to="`/dashboard/catalog/${p.product_key}`"
            class="text-xs bg-gray-50 border px-3 py-1.5 rounded-lg hover:border-indigo-300 text-gray-700"
          >
            {{ p.display_name }} <span class="text-gray-400">({{ p.domain }})</span>
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>
