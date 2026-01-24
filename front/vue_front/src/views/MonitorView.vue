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
              <div class="text-xl font-semibold text-success mt-1">正常</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">数据运行状态</div>
              <div class="text-xl font-semibold text-success mt-1">正常</div>
            </div>
          </div>
          
          <!-- 告警统计卡片 - 右上角 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 md:mt-0">
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">总告警数</div>
              <div class="text-xl font-semibold mt-1">147</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">待处理</div>
              <div class="text-xl font-semibold text-warning mt-1">36</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">已解决</div>
              <div class="text-xl font-semibold text-success mt-1">98</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">高风险</div>
              <div class="text-xl font-semibold text-danger mt-1">13</div>
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
                @click="selectedPeriod = period.value"
                class="px-3 py-1 text-sm rounded-md transition-smooth"
                :class="selectedPeriod === period.value 
                  ? 'bg-primary text-white hover:bg-primary/90' 
                  : 'bg-gray-100 text-light-dark hover:bg-gray-200'"
              >
                {{ period.label }}
              </button>
            </div>
          </div>
          <div class="h-64">
            <canvas ref="riskTrendChartRef"></canvas>
          </div>
        </div>
      </section>
      
      <!-- 风险告警可视化 -->
      <section class="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl p-6 card-shadow lg:col-span-1">
          <h3 class="text-lg font-semibold mb-4">告警级别分布</h3>
          <div class="h-64">
            <canvas ref="alertLevelChartRef"></canvas>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-6 card-shadow lg:col-span-2">
          <h3 class="text-lg font-semibold mb-4">告警类型趋势</h3>
          <div class="h-64">
            <canvas ref="alertTypeChartRef"></canvas>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
    <Toast ref="toastRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'

Chart.register(...registerables)

const riskTrendChartRef = ref<HTMLCanvasElement | null>(null)
const alertLevelChartRef = ref<HTMLCanvasElement | null>(null)
const alertTypeChartRef = ref<HTMLCanvasElement | null>(null)

const selectedPeriod = ref('today')
const timePeriods = [
  { value: 'today', label: '今日' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' }
]

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
let refreshTimer: number | null = null
let riskTrendChart: Chart | null = null
let alertLevelChart: Chart | null = null
let alertTypeChart: Chart | null = null

const initRiskTrendChart = () => {
  if (!riskTrendChartRef.value) return
  
  const ctx = riskTrendChartRef.value.getContext('2d')
  if (!ctx) return
  
  riskTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
      datasets: [
        {
          label: '高风险',
          data: [2, 1, 0, 3, 5, 4, 3, 4],
          borderColor: '#FF4D4F',
          backgroundColor: 'rgba(255, 77, 79, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: '中风险',
          data: [3, 2, 4, 5, 6, 5, 7, 6],
          borderColor: '#FAAD14',
          backgroundColor: 'rgba(250, 173, 20, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: '低风险',
          data: [5, 7, 6, 8, 10, 9, 8, 10],
          borderColor: '#1890FF',
          backgroundColor: 'rgba(24, 144, 255, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
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

const initAlertLevelChart = () => {
  if (!alertLevelChartRef.value) return
  
  const ctx = alertLevelChartRef.value.getContext('2d')
  if (!ctx) return
  
  alertLevelChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['高风险', '中风险', '低风险'],
      datasets: [{
        data: [13, 56, 78],
        backgroundColor: [
          '#FF4D4F',
          '#FAAD14',
          '#1890FF'
        ],
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

const initAlertTypeChart = () => {
  if (!alertTypeChartRef.value) return
  
  const ctx = alertTypeChartRef.value.getContext('2d')
  if (!ctx) return
  
  alertTypeChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['6/10', '6/11', '6/12', '6/13', '6/14', '6/15'],
      datasets: [
        {
          label: '账户风险',
          data: [8, 12, 9, 15, 11, 7],
          backgroundColor: '#165DFF'
        },
        {
          label: '交易风险',
          data: [15, 18, 12, 20, 17, 9],
          backgroundColor: '#36CFC9'
        },
        {
          label: '身份验证',
          data: [5, 7, 9, 6, 8, 4],
          backgroundColor: '#FAAD14'
        },
        {
          label: '设备异常',
          data: [3, 5, 4, 6, 5, 3],
          backgroundColor: '#722ED1'
        },
        {
          label: '行为异常',
          data: [7, 6, 9, 8, 10, 5],
          backgroundColor: '#EB0AA4'
        }
      ]
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

const simulateDataRefresh = () => {
  console.log('数据已刷新')
  toastRef.value?.show()
}

const setupAutoRefresh = (intervalSeconds: number) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  refreshTimer = window.setInterval(() => {
    simulateDataRefresh()
  }, intervalSeconds * 1000)
}

onMounted(async () => {
  await nextTick()
  initRiskTrendChart()
  initAlertLevelChart()
  initAlertTypeChart()
  setupAutoRefresh(10)
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

