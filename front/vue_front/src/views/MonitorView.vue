<template>
  <div class="font-inter bg-gray-50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- 系统状态卡片 -->
      <div class="mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
          <!-- 系统状态卡片 - 左上角 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">模型运行状态</div>
              <div 
                class="text-xl font-semibold mt-1"
                :class="systemStatus.modelStatus === 'normal' ? 'text-success' : 'text-danger'"
              >
                {{ systemStatus.modelStatusName }}
              </div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">数据运行状态</div>
              <div 
                class="text-xl font-semibold mt-1"
                :class="systemStatus.dataStatus === 'normal' ? 'text-success' : 'text-danger'"
              >
                {{ systemStatus.dataStatusName }}
              </div>
            </div>
          </div>
          
          <!-- 告警统计卡片 - 右上角 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 md:mt-0">
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">总告警数</div>
              <div class="text-xl font-semibold mt-1">{{ alertStats.total }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">待处理</div>
              <div class="text-xl font-semibold text-warning mt-1">{{ alertStats.pending }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">已解决</div>
              <div class="text-xl font-semibold text-success mt-1">{{ alertStats.resolved }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">高风险</div>
              <div class="text-xl font-semibold text-danger mt-1">{{ alertStats.highRisk }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 风险趋势图表 -->
      <section class="mb-8">
        <div class="bg-white rounded-xl p-6 card-shadow">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
            <h3 class="text-lg font-semibold">风险事件趋势</h3>
            <div class="flex space-x-2 mt-3 md:mt-0">
              <button 
                v-for="period in timePeriods"
                :key="period.value"
                @click="handlePeriodChange(period.value)"
                class="px-3 py-1 text-sm rounded-md transition-smooth"
                :class="selectedPeriod === period.value 
                  ? 'bg-primary text-white hover:bg-primary/90' 
                  : 'bg-gray-100 text-light-dark hover:bg-gray-200'"
              >
                {{ period.label }}
              </button>
            </div>
          </div>
          <div class="h-64 relative">
            <div v-if="loading.riskTrend" class="absolute inset-0 flex items-center justify-center bg-white/80">
              <i class="fas fa-spinner fa-spin text-primary text-2xl"></i>
            </div>
            <canvas ref="riskTrendChartRef"></canvas>
          </div>
        </div>
      </section>
      
      <!-- 风险告警可视化 -->
      <section class="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl p-6 card-shadow lg:col-span-1">
          <h3 class="text-lg font-semibold mb-4">告警级别分布</h3>
          <div class="h-64 relative">
            <div v-if="loading.levelDistribution" class="absolute inset-0 flex items-center justify-center bg-white/80">
              <i class="fas fa-spinner fa-spin text-primary text-2xl"></i>
            </div>
            <canvas ref="alertLevelChartRef"></canvas>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-6 card-shadow lg:col-span-2">
          <h3 class="text-lg font-semibold mb-4">告警类型趋势</h3>
          <div class="h-64 relative">
            <div v-if="loading.typeTrend" class="absolute inset-0 flex items-center justify-center bg-white/80">
              <i class="fas fa-spinner fa-spin text-primary text-2xl"></i>
            </div>
            <canvas ref="alertTypeChartRef"></canvas>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'

// API 导入
import { getSystemStatus, getRiskTrend } from '@/api/monitor'
import { getAlertStatistics, getAlertLevelDistribution, getAlertTypeTrend } from '@/api/alerts'
import type { SystemStatus, AlertStatistics, RiskTrendData, AlertLevelDistribution, AlertTypeTrendData } from '@/api/types'

Chart.register(...registerables)

// DOM 引用
const riskTrendChartRef = ref<HTMLCanvasElement | null>(null)
const alertLevelChartRef = ref<HTMLCanvasElement | null>(null)
const alertTypeChartRef = ref<HTMLCanvasElement | null>(null)
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

// 状态
const selectedPeriod = ref('today')
const timePeriods = [
  { value: 'today', label: '今日' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' }
]

const toastMessage = ref('数据已刷新')
const toastType = ref<'success' | 'warning'>('success')

// 加载状态
const loading = reactive({
  systemStatus: false,
  alertStats: false,
  riskTrend: false,
  levelDistribution: false,
  typeTrend: false
})

// 数据状态
const systemStatus = reactive<SystemStatus>({
  modelStatus: 'normal',
  modelStatusName: '正常',
  dataStatus: 'normal',
  dataStatusName: '正常'
})

const alertStats = reactive<AlertStatistics>({
  total: 0,
  pending: 0,
  resolved: 0,
  highRisk: 0,
  mediumRisk: 0,
  lowRisk: 0
})

// 图表实例
let refreshTimer: number | null = null
let riskTrendChart: Chart | null = null
let alertLevelChart: Chart | null = null
let alertTypeChart: Chart | null = null

// 图表颜色配置
const chartColors = {
  high: '#FF4D4F',
  medium: '#FAAD14',
  low: '#1890FF',
  types: ['#165DFF', '#36CFC9', '#FAAD14', '#722ED1', '#EB0AA4']
}

// ============ API 调用函数 ============

// 获取系统状态
const fetchSystemStatus = async () => {
  loading.systemStatus = true
  try {
    const { data: res } = await getSystemStatus()
    if (res.code === 200 && res.data) {
      Object.assign(systemStatus, res.data)
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
  } finally {
    loading.systemStatus = false
  }
}

// 获取告警统计
const fetchAlertStatistics = async () => {
  loading.alertStats = true
  try {
    const { data: res } = await getAlertStatistics()
    if (res.code === 200 && res.data) {
      Object.assign(alertStats, res.data)
    }
  } catch (error) {
    console.error('获取告警统计失败:', error)
  } finally {
    loading.alertStats = false
  }
}

// 获取风险趋势数据并更新图表
const fetchRiskTrend = async () => {
  loading.riskTrend = true
  try {
    const { data: res } = await getRiskTrend(selectedPeriod.value)
    if (res.code === 200 && res.data) {
      updateRiskTrendChart(res.data)
    }
  } catch (error) {
    console.error('获取风险趋势失败:', error)
  } finally {
    loading.riskTrend = false
  }
}

// 获取告警级别分布并更新图表
const fetchAlertLevelDistribution = async () => {
  loading.levelDistribution = true
  try {
    const { data: res } = await getAlertLevelDistribution()
    if (res.code === 200 && res.data) {
      updateAlertLevelChart(res.data)
    }
  } catch (error) {
    console.error('获取告警级别分布失败:', error)
  } finally {
    loading.levelDistribution = false
  }
}

// 获取告警类型趋势并更新图表
const fetchAlertTypeTrend = async () => {
  loading.typeTrend = true
  try {
    const { data: res } = await getAlertTypeTrend(6)
    if (res.code === 200 && res.data) {
      updateAlertTypeChart(res.data)
    }
  } catch (error) {
    console.error('获取告警类型趋势失败:', error)
  } finally {
    loading.typeTrend = false
  }
}

// ============ 图表初始化和更新函数 ============

const initRiskTrendChart = () => {
  if (!riskTrendChartRef.value) return
  
  const ctx = riskTrendChartRef.value.getContext('2d')
  if (!ctx) return
  
  riskTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: []
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      },
      interaction: {
        mode: 'index',
        intersect: false
      }
    }
  })
}

const updateRiskTrendChart = (data: RiskTrendData) => {
  if (!riskTrendChart) return
  
  const colorMap: Record<string, { border: string; bg: string }> = {
    '高风险': { border: chartColors.high, bg: 'rgba(255, 77, 79, 0.1)' },
    '中风险': { border: chartColors.medium, bg: 'rgba(250, 173, 20, 0.1)' },
    '低风险': { border: chartColors.low, bg: 'rgba(24, 144, 255, 0.1)' }
  }
  
  riskTrendChart.data.labels = data.labels
  riskTrendChart.data.datasets = data.datasets.map(ds => ({
    label: ds.label,
    data: ds.data,
    borderColor: colorMap[ds.label]?.border || chartColors.low,
    backgroundColor: colorMap[ds.label]?.bg || 'rgba(24, 144, 255, 0.1)',
    tension: 0.4,
    fill: true
  }))
  riskTrendChart.update()
}

const initAlertLevelChart = () => {
  if (!alertLevelChartRef.value) return
  
  const ctx = alertLevelChartRef.value.getContext('2d')
  if (!ctx) return
  
  alertLevelChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['高风险', '中风险', '低风险'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: [chartColors.high, chartColors.medium, chartColors.low],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 15,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        }
      },
      cutout: '70%'
    }
  })
}

const updateAlertLevelChart = (data: AlertLevelDistribution) => {
  if (!alertLevelChart) return
  
  alertLevelChart.data.datasets[0].data = [data.high, data.medium, data.low]
  alertLevelChart.update()
}

const initAlertTypeChart = () => {
  if (!alertTypeChartRef.value) return
  
  const ctx = alertTypeChartRef.value.getContext('2d')
  if (!ctx) return
  
  alertTypeChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: []
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      },
      barPercentage: 0.6
    }
  })
}

const updateAlertTypeChart = (data: AlertTypeTrendData) => {
  if (!alertTypeChart) return
  
  alertTypeChart.data.labels = data.labels
  alertTypeChart.data.datasets = data.datasets.map((ds, index) => ({
    label: ds.label,
    data: ds.data,
    backgroundColor: chartColors.types[index % chartColors.types.length]
  }))
  alertTypeChart.update()
}

// ============ 事件处理 ============

const handlePeriodChange = (period: string) => {
  selectedPeriod.value = period
  fetchRiskTrend()
}

const refreshAllData = async () => {
  await Promise.all([
    fetchSystemStatus(),
    fetchAlertStatistics(),
    fetchRiskTrend(),
    fetchAlertLevelDistribution(),
    fetchAlertTypeTrend()
  ])
  toastMessage.value = '数据已刷新'
  toastType.value = 'success'
  toastRef.value?.show()
}

const setupAutoRefresh = (intervalSeconds: number) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  refreshTimer = window.setInterval(() => {
    refreshAllData()
  }, intervalSeconds * 1000)
}

// ============ 生命周期 ============

onMounted(async () => {
  await nextTick()
  
  // 初始化图表
  initRiskTrendChart()
  initAlertLevelChart()
  initAlertTypeChart()
  
  // 加载数据
  await refreshAllData()
  
  // 设置自动刷新（30秒）
  setupAutoRefresh(30)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  riskTrendChart?.destroy()
  alertLevelChart?.destroy()
  alertTypeChart?.destroy()
})
</script>

<style scoped>
/* 组件样式 */
</style>
