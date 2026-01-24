<template>
  <div class="font-inter bg-gray-50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- 页面标题和状态概览 -->
      <div class="mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-dark">数据采集监控</h2>
            <p class="text-light-dark mt-1">监控数据源接入状态、采集进度和数据质量</p>
          </div>
          
          <!-- 数据采集状态卡片 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 md:mt-0">
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">数据源总数</div>
              <div class="text-xl font-semibold mt-1">12</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">正常运行</div>
              <div class="text-xl font-semibold text-success mt-1">9</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">异常数据源</div>
              <div class="text-xl font-semibold text-danger mt-1">2</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">数据质量问题</div>
              <div class="text-xl font-semibold text-warning mt-1">56</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 数据源监控 -->
      <section class="mb-8">
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between">
              <h3 class="text-lg font-semibold mb-3 md:mb-0">数据源监控</h3>
              <div class="flex flex-wrap gap-3">
                <div class="relative">
                  <input 
                    v-model="searchKeyword"
                    type="text" 
                    placeholder="搜索数据源..." 
                    class="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-64"
                  >
                  <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-light-dark"></i>
                </div>
                <select 
                  v-model="statusFilter"
                  class="border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth"
                >
                  <option value="all">全部状态</option>
                  <option value="normal">正常</option>
                  <option value="warning">警告</option>
                  <option value="error">异常</option>
                  <option value="stopped">已停止</option>
                </select>
                <button 
                  @click="refreshData"
                  class="flex items-center justify-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-smooth"
                >
                  <i class="fas fa-refresh mr-2"></i>刷新
                </button>
              </div>
            </div>
          </div>
          
          <!-- 数据源列表 -->
          <div class="divide-y divide-gray-200">
            <div 
              v-for="source in dataSources" 
              :key="source.id"
              class="p-6 hover:bg-gray-50 transition-smooth"
            >
              <div class="flex flex-col md:flex-row md:items-start justify-between">
                <div class="flex items-start space-x-4">
                  <div 
                    class="p-3 rounded-lg mt-0.5"
                    :class="getStatusIconClass(source.status)"
                  >
                    <i :class="source.icon"></i>
                  </div>
                  <div>
                    <div class="flex flex-wrap items-center gap-2">
                      <h4 class="font-medium text-lg">{{ source.name }}</h4>
                      <span 
                        class="px-2 py-0.5 text-xs rounded-full"
                        :class="getStatusBadgeClass(source.status)"
                      >
                        {{ source.statusText }}
                      </span>
                      <span 
                        v-if="source.isCollecting"
                        class="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full pulse-animation"
                      >
                        采集进行中
                      </span>
                      <span 
                        v-if="source.status === 'error'"
                        class="px-2 py-0.5 bg-gray-200 text-light-dark text-xs rounded-full"
                      >
                        采集已停止
                      </span>
                    </div>
                    <p class="text-sm text-light-dark mt-1">
                      <i class="fas fa-database mr-1"></i>
                      连接: {{ source.connection }} <span class="mx-2">|</span>
                      <i class="far fa-clock mr-1"></i>
                      最后同步: {{ source.lastSync }}
                    </p>
                    
                    <!-- 数据质量问题提示 -->
                    <div 
                      v-if="source.qualityIssues > 0"
                      @click="openQualityModal(source)"
                      class="mt-3 flex items-center text-sm cursor-pointer"
                      :class="source.qualityIssues > 10 ? 'text-danger' : 'text-warning'"
                    >
                      <i :class="source.qualityIssues > 10 ? 'fas fa-exclamation-circle' : 'fas fa-exclamation-triangle'" class="mr-1"></i>
                      检测到 {{ source.qualityIssues }} 个数据质量问题 <i class="fas fa-angle-right ml-1"></i>
                    </div>
                    <div 
                      v-else-if="source.status !== 'error'"
                      class="mt-3 flex items-center text-light-dark text-sm"
                    >
                      <i class="fas fa-check-circle mr-1 text-success"></i>
                      未检测到数据质量问题
                    </div>
                    
                    <!-- 错误信息 -->
                    <div 
                      v-if="source.error"
                      class="mt-3 flex items-center text-danger text-sm"
                    >
                      <i class="fas fa-times-circle mr-1"></i>
                      {{ source.error }}
                    </div>
                    
                    <!-- 警告信息 -->
                    <div 
                      v-if="source.warning"
                      class="mt-2 flex items-center text-warning text-sm"
                    >
                      <i class="fas fa-exclamation-triangle mr-1"></i>
                      {{ source.warning }}
                    </div>
                    
                    <!-- 重新连接按钮 -->
                    <div v-if="source.status === 'error'" class="mt-3">
                      <button class="px-3 py-1 bg-primary text-white text-sm rounded hover:bg-primary/90 transition-smooth">
                        <i class="fas fa-refresh mr-1"></i>重新连接
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="w-full md:w-1/3 mt-4 md:mt-0">
                  <div class="mb-1 flex justify-between items-center">
                    <span class="text-sm text-light-dark">采集进度</span>
                    <span 
                      class="text-sm font-medium"
                      :class="source.status === 'error' ? 'text-danger' : ''"
                    >
                      {{ source.status === 'error' ? '中断' : source.progress + '%' }}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      class="h-2.5 rounded-full transition-all duration-300"
                      :class="getProgressBarClass(source.status)"
                      :style="{ width: source.progress + '%' }"
                    ></div>
                  </div>
                  <div class="mt-2 text-sm text-light-dark flex justify-between">
                    <span>今日已采集: {{ source.collected }} 条</span>
                    <span>{{ source.status === 'error' ? '上次失败: ' + source.lastFailure : '预计完成: ' + source.estimatedComplete }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <div class="p-6 border-t border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="text-sm text-light-dark">
              显示 1-5 条，共 12 条
            </div>
            <div class="flex space-x-1">
              <button class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                <i class="fas fa-angle-left"></i>
              </button>
              <button class="w-9 h-9 flex items-center justify-center rounded-md bg-primary text-white">1</button>
              <button class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 hover:border-primary hover:text-primary transition-smooth">2</button>
              <button class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 hover:border-primary hover:text-primary transition-smooth">3</button>
              <button class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth">
                <i class="fas fa-angle-right"></i>
              </button>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 数据预览和质量检查 -->
      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 数据预览 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">数据样本预览</h3>
          </div>
          
          <div class="p-6">
            <div class="mb-4 flex flex-wrap gap-2">
              <button 
                v-for="tab in previewTabs"
                :key="tab.value"
                @click="activePreviewTab = tab.value"
                class="px-3 py-1 text-sm rounded-md transition-smooth"
                :class="activePreviewTab === tab.value 
                  ? 'bg-primary text-white hover:bg-primary/90' 
                  : 'bg-gray-100 text-light-dark hover:bg-gray-200'"
              >
                {{ tab.label }}
              </button>
            </div>
            
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-light-dark uppercase tracking-wider">交易ID</th>
                    <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-light-dark uppercase tracking-wider">用户ID</th>
                    <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-light-dark uppercase tracking-wider">金额</th>
                    <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-light-dark uppercase tracking-wider">时间</th>
                    <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-light-dark uppercase tracking-wider">状态</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="item in previewData" :key="item.id">
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.id }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.userId }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.amount }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.time }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">
                      <span 
                        class="px-2 py-0.5 text-xs rounded-full"
                        :class="getTransactionStatusClass(item.status)"
                      >
                        {{ item.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="mt-4 text-sm text-light-dark text-center">
              显示最新 4 条数据 | <a href="#" class="text-primary hover:underline">查看更多</a>
            </div>
          </div>
        </div>
        
        <!-- 数据质量检查 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">数据质量问题汇总</h3>
          </div>
          
          <div class="p-6">
            <div class="space-y-4">
              <div 
                v-for="issue in qualityIssues"
                :key="issue.id"
                class="flex items-center justify-between p-3 rounded-lg border"
                :class="issue.severity === 'high' ? 'bg-danger/5 border-danger/20' : 'bg-warning/5 border-warning/20'"
              >
                <div class="flex items-center">
                  <div 
                    class="p-2 rounded-full mr-3"
                    :class="issue.severity === 'high' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'"
                  >
                    <i :class="issue.icon"></i>
                  </div>
                  <div>
                    <div class="font-medium">{{ issue.title }}</div>
                    <div class="text-sm text-light-dark">{{ issue.description }}</div>
                  </div>
                </div>
                <div 
                  class="font-medium"
                  :class="issue.severity === 'high' ? 'text-danger' : 'text-warning'"
                >
                  {{ issue.count }} 条记录
                </div>
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t border-gray-200">
              <div class="flex justify-between items-center mb-3">
                <h4 class="font-medium">数据质量评分</h4>
                <span class="text-xl font-bold text-warning">82/100</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="bg-warning h-2.5 rounded-full" style="width: 82%"></div>
              </div>
              <div class="mt-2 text-sm text-light-dark">
                <i class="fas fa-info-circle mr-1 text-info"></i>
                数据质量评分基于完整性、准确性、一致性和及时性四个维度
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
    
    <!-- 数据质量问题模态框 -->
    <QualityIssuesModal 
      v-if="showQualityModal"
      :source="selectedSource"
      @close="showQualityModal = false"
      @export="handleExportIssues"
    />
    
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'
import QualityIssuesModal from '@/components/QualityIssuesModal.vue'

interface DataSource {
  id: string
  name: string
  icon: string
  status: 'normal' | 'warning' | 'error'
  statusText: string
  connection: string
  lastSync: string
  qualityIssues: number
  progress: number
  collected: string
  estimatedComplete?: string
  lastFailure?: string
  isCollecting: boolean
  error?: string
  warning?: string
}

const searchKeyword = ref('')
const statusFilter = ref('all')
const activePreviewTab = ref('trade')
const showQualityModal = ref(false)
const selectedSource = ref<DataSource | null>(null)

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

let refreshTimer: number | null = null

const previewTabs = [
  { value: 'trade', label: '交易数据' },
  { value: 'user', label: '用户行为' },
  { value: 'image', label: '图像数据' },
  { value: 'device', label: '设备数据' }
]

const dataSources = ref<DataSource[]>([
  {
    id: '1',
    name: '交易数据中心',
    icon: 'fas fa-exchange-alt',
    status: 'normal',
    statusText: '正常',
    connection: 'db-trade-01.internal',
    lastSync: '2023-06-15 14:32:18',
    qualityIssues: 12,
    progress: 78,
    collected: '148,562',
    estimatedComplete: '14:45',
    isCollecting: true
  },
  {
    id: '2',
    name: '用户行为分析平台',
    icon: 'fas fa-user',
    status: 'normal',
    statusText: '正常',
    connection: 'api-user-behavior.vpc',
    lastSync: '2023-06-15 14:31:56',
    qualityIssues: 5,
    progress: 45,
    collected: '326,891',
    estimatedComplete: '15:30',
    isCollecting: true
  },
  {
    id: '3',
    name: '图像存储服务',
    icon: 'fas fa-image',
    status: 'error',
    statusText: '异常',
    connection: 'img-storage-02',
    lastSync: '2023-06-15 13:15:08',
    qualityIssues: 0,
    progress: 32,
    collected: '8,452',
    lastFailure: '13:20',
    isCollecting: false,
    error: '错误: 连接超时，已尝试 5 次重连'
  },
  {
    id: '4',
    name: '设备指纹系统',
    icon: 'fas fa-mobile-alt',
    status: 'normal',
    statusText: '正常',
    connection: 'device-fingerprint-service',
    lastSync: '2023-06-15 14:33:02',
    qualityIssues: 0,
    progress: 92,
    collected: '67,321',
    estimatedComplete: '14:40',
    isCollecting: true
  },
  {
    id: '5',
    name: '第三方信用评估接口',
    icon: 'fas fa-credit-card',
    status: 'warning',
    statusText: '警告',
    connection: 'api.thirdparty-credit.com',
    lastSync: '2023-06-15 14:28:45',
    qualityIssues: 39,
    progress: 23,
    collected: '12,456',
    estimatedComplete: '16:10',
    isCollecting: true,
    warning: 'API响应延迟较高，已超过阈值 2.5 秒'
  }
])

const previewData = ref([
  { id: 'TX2023061500123', userId: 'USER789456', amount: '¥2,560.00', time: '14:32:15', status: '成功' },
  { id: 'TX2023061500122', userId: 'USER123789', amount: '¥1,280.00', time: '14:31:58', status: '成功' },
  { id: 'TX2023061500121', userId: 'USER456123', amount: '¥5,690.00', time: '14:31:42', status: '处理中' },
  { id: 'TX2023061500120', userId: 'USER321654', amount: '¥890.00', time: '14:31:25', status: '失败' }
])

const qualityIssues = ref([
  { id: '1', title: '缺失关键字段', description: '用户行为数据中缺少地理位置信息', count: 32, severity: 'high', icon: 'fas fa-times-circle' },
  { id: '2', title: '格式错误', description: '第三方信用数据中日期格式不符合规范', count: 24, severity: 'high', icon: 'fas fa-exclamation-circle' },
  { id: '3', title: '值异常', description: '交易金额超出正常范围（>10万元）', count: 8, severity: 'medium', icon: 'fas fa-exclamation-triangle' },
  { id: '4', title: '数据不一致', description: '用户信息与历史记录不匹配', count: 5, severity: 'medium', icon: 'fas fa-question-circle' }
])

const getStatusIconClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success/10 text-success'
    case 'warning': return 'bg-warning/10 text-warning'
    case 'error': return 'bg-danger/10 text-danger'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success/10 text-success'
    case 'warning': return 'bg-warning/10 text-warning'
    case 'error': return 'bg-danger/10 text-danger'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getProgressBarClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success'
    case 'warning': return 'bg-warning'
    case 'error': return 'bg-danger'
    default: return 'bg-gray-400'
  }
}

const getTransactionStatusClass = (status: string) => {
  switch (status) {
    case '成功': return 'bg-success/10 text-success'
    case '处理中': return 'bg-warning/10 text-warning'
    case '失败': return 'bg-danger/10 text-danger'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const openQualityModal = (source: DataSource) => {
  selectedSource.value = source
  showQualityModal.value = true
}

const handleExportIssues = () => {
  showToast('数据质量问题列表已导出为CSV文件')
  showQualityModal.value = false
}

const refreshData = () => {
  showToast('数据已更新')
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

onMounted(() => {
  // 设置自动刷新
  refreshTimer = window.setInterval(() => {
    refreshData()
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
/* 组件样式 */
</style>

