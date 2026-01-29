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
              <div class="text-xl font-semibold mt-1">{{ statistics.total || 0 }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">正常运行</div>
              <div class="text-xl font-semibold text-success mt-1">{{ statistics.normal || 0 }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">异常数据源</div>
              <div class="text-xl font-semibold text-danger mt-1">{{ statistics.abnormal || 0 }}</div>
            </div>
            <div class="bg-white rounded-lg p-3 card-shadow">
              <div class="text-light-dark text-sm">数据质量问题</div>
              <div class="text-xl font-semibold text-warning mt-1">{{ statistics.qualityIssues || 0 }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 文件上传区域 -->
      <section class="mb-6">
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h3 class="text-lg font-semibold mb-2">数据文件上传</h3>
                <p class="text-sm text-light-dark">支持上传 CSV、Excel、JSON 等格式的数据文件进行采集</p>
              </div>
              <div class="flex items-center gap-3">
                <label 
                  for="file-upload"
                  class="flex items-center justify-center px-6 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-smooth cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="{ 'opacity-50 cursor-not-allowed': uploading }"
                >
                  <i class="fas fa-cloud-upload-alt mr-2" :class="{ 'fa-spin': uploading }"></i>
                  {{ uploading ? '上传中...' : '选择文件' }}
                </label>
                <input
                  id="file-upload"
                  type="file"
                  ref="fileInputRef"
                  @change="handleFileSelect"
                  :disabled="uploading"
                  accept=".csv,.xlsx,.xls,.json,.txt"
                  class="hidden"
                >
                <div v-if="selectedFile" class="flex items-center gap-2 text-sm">
                  <i class="fas fa-file text-primary"></i>
                  <span class="text-light-dark">{{ selectedFile.name }}</span>
                  <span class="text-light-dark">({{ formatFileSize(selectedFile.size) }})</span>
                  <button 
                    @click="clearSelectedFile"
                    class="text-danger hover:text-danger/80 transition-smooth"
                    :disabled="uploading"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mt-4">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-light-dark">上传进度</span>
                <span class="text-sm font-medium text-primary">{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-primary h-2 rounded-full transition-all duration-300"
                  :style="{ width: uploadProgress + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
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
                    <i :class="getDataSourceIcon(source.type)"></i>
                  </div>
                  <div>
                    <div class="flex flex-wrap items-center gap-2">
                      <h4 class="font-medium text-lg">{{ source.name }}</h4>
                      <span 
                        class="px-2 py-0.5 text-xs rounded-full"
                        :class="getStatusBadgeClass(source.status)"
                      >
                        {{ source.statusName }}
                      </span>
                      <span 
                        v-if="source.collectionStatus === 'running'"
                        class="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full pulse-animation"
                      >
                        {{ source.collectionStatusName }}
                      </span>
                      <span 
                        v-if="source.status === 'error' || source.status === 'stopped'"
                        class="px-2 py-0.5 bg-gray-200 text-light-dark text-xs rounded-full"
                      >
                        采集已停止
                      </span>
                    </div>
                    <p class="text-sm text-light-dark mt-1">
                      <i class="fas fa-database mr-1"></i>
                      连接: {{ source.connection }} <span class="mx-2">|</span>
                      <i class="far fa-clock mr-1"></i>
                      最后同步: {{ source.lastSyncTime }}
                    </p>
                    
                    <!-- 数据质量问题提示 -->
                    <div 
                      v-if="source.qualityIssuesCount > 0"
                      @click="openQualityModal(source)"
                      class="mt-3 flex items-center text-sm cursor-pointer"
                      :class="source.qualityIssuesCount > 10 ? 'text-danger' : 'text-warning'"
                    >
                      <i :class="source.qualityIssuesCount > 10 ? 'fas fa-exclamation-circle' : 'fas fa-exclamation-triangle'" class="mr-1"></i>
                      检测到 {{ source.qualityIssuesCount }} 个数据质量问题 <i class="fas fa-angle-right ml-1"></i>
                    </div>
                    <div 
                      v-else-if="source.status !== 'error' && source.status !== 'stopped'"
                      class="mt-3 flex items-center text-light-dark text-sm"
                    >
                      <i class="fas fa-check-circle mr-1 text-success"></i>
                      未检测到数据质量问题
                    </div>
                    
                    <!-- 错误信息 -->
                    <div 
                      v-if="source.errorMessage"
                      class="mt-3 flex items-center text-danger text-sm"
                    >
                      <i class="fas fa-times-circle mr-1"></i>
                      {{ source.errorMessage }}
                    </div>
                    
                    <!-- 重新连接按钮 -->
                    <div v-if="source.status === 'error'" class="mt-3">
                      <button 
                        @click="handleReconnect(source.id)"
                        :disabled="reconnectingIds.includes(source.id)"
                        class="px-3 py-1 bg-primary text-white text-sm rounded hover:bg-primary/90 transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <i class="fas fa-refresh mr-1" :class="{ 'fa-spin': reconnectingIds.includes(source.id) }"></i>
                        {{ reconnectingIds.includes(source.id) ? '连接中...' : '重新连接' }}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="w-full md:w-1/3 mt-4 md:mt-0">
                  <div class="mb-1 flex justify-between items-center">
                    <span class="text-sm text-light-dark">采集进度</span>
                    <span 
                      class="text-sm font-medium"
                      :class="source.status === 'error' || source.status === 'stopped' ? 'text-danger' : ''"
                    >
                      {{ source.status === 'error' || source.status === 'stopped' ? '中断' : source.progress + '%' }}
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
                    <span>今日已采集: {{ formatNumber(source.todayCollected) }} 条</span>
                    <span>{{ source.status === 'error' || source.status === 'stopped' ? '' : (source.estimatedCompletion ? '预计完成: ' + source.estimatedCompletion : '') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <div class="p-6 border-t border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="text-sm text-light-dark">
              显示 {{ (pagination.page - 1) * pagination.pageSize + 1 }}-{{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} 条，共 {{ pagination.total }} 条
            </div>
            <div class="flex space-x-1">
              <button 
                @click="handlePageChange(pagination.page - 1)"
                :disabled="pagination.page <= 1"
                class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <i class="fas fa-angle-left"></i>
              </button>
              <button 
                v-for="page in visiblePages"
                :key="page"
                @click="handlePageChange(page)"
                class="w-9 h-9 flex items-center justify-center rounded-md transition-smooth"
                :class="page === pagination.page 
                  ? 'bg-primary text-white' 
                  : 'border border-gray-200 hover:border-primary hover:text-primary'"
              >
                {{ page }}
              </button>
              <button 
                @click="handlePageChange(pagination.page + 1)"
                :disabled="pagination.page >= totalPages"
                class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
              >
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
                @click="handlePreviewTabChange(tab.value)"
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
                  <tr v-for="(item, index) in previewData" :key="index">
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.transactionId || item.id || '-' }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.userId || '-' }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.amount ? formatAmount(item.amount) : '-' }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">{{ item.time || '-' }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-sm">
                      <span 
                        class="px-2 py-0.5 text-xs rounded-full"
                        :class="getTransactionStatusClass(item.status || '')"
                      >
                        {{ item.status || '-' }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="previewData.length === 0">
                    <td colspan="5" class="px-4 py-8 text-center text-light-dark text-sm">暂无数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="mt-4 text-sm text-light-dark text-center">
              显示最新 {{ previewData.length }} 条数据，共 {{ previewTotal }} 条
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
                v-for="issue in qualityIssuesSummary"
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
              <div v-if="qualityIssuesSummary.every(issue => issue.count === 0)" class="text-center text-light-dark text-sm py-8">
                暂无数据质量问题
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t border-gray-200">
              <div class="flex justify-between items-center mb-3">
                <h4 class="font-medium">数据质量评分</h4>
                <span class="text-xl font-bold" :class="qualityScore.score >= 80 ? 'text-success' : qualityScore.score >= 60 ? 'text-warning' : 'text-danger'">
                  {{ qualityScore.score }}/{{ qualityScore.maxScore }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  class="h-2.5 rounded-full transition-all"
                  :class="qualityScore.score >= 80 ? 'bg-success' : qualityScore.score >= 60 ? 'bg-warning' : 'bg-danger'"
                  :style="{ width: (qualityScore.score / qualityScore.maxScore * 100) + '%' }"
                ></div>
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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'
import QualityIssuesModal from '@/components/QualityIssuesModal.vue'
import {
  getDataSources,
  getDataSourceStatistics,
  getDataPreview,
  getQualityScore,
  getQualityIssues,
  reconnectDataSource,
  exportQualityIssues
} from '@/api/dataCollection'
import { uploadFile } from '@/api/common'
import type { DataSource as ApiDataSource, DataSourceStatistics, DataPreviewItem, QualityScore } from '@/api/types'

// 响应式数据
const searchKeyword = ref('')
const statusFilter = ref('all')
const activePreviewTab = ref('trade')
const showQualityModal = ref(false)
const selectedSource = ref<ApiDataSource | null>(null)
const loading = ref(false)
const reconnectingIds = ref<number[]>([])

// 统计数据
const statistics = ref<DataSourceStatistics>({
  total: 0,
  normal: 0,
  abnormal: 0,
  qualityIssues: 0
})

// 数据源列表
const dataSources = ref<ApiDataSource[]>([])
const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// 预览数据
const previewData = ref<DataPreviewItem[]>([])
const previewTotal = ref(0)
const selectedSourceId = ref<number | null>(null)

// 质量问题汇总
const qualityIssuesSummary = ref([
  { id: '1', title: '缺失关键字段', description: '数据中缺少必填字段', count: 0, severity: 'high' as const, icon: 'fas fa-times-circle' },
  { id: '2', title: '格式错误', description: '数据格式不符合规范', count: 0, severity: 'high' as const, icon: 'fas fa-exclamation-circle' },
  { id: '3', title: '值异常', description: '数据值超出正常范围', count: 0, severity: 'medium' as const, icon: 'fas fa-exclamation-triangle' },
  { id: '4', title: '数据不一致', description: '数据与历史记录不匹配', count: 0, severity: 'medium' as const, icon: 'fas fa-question-circle' }
])

// 质量评分
const qualityScore = ref<QualityScore>({
  score: 100,
  maxScore: 100,
  dimensions: {
    completeness: 100,
    accuracy: 100,
    consistency: 100,
    timeliness: 100
  }
})

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

// 文件上传相关
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)

let refreshTimer: number | null = null
let searchTimer: number | null = null

const previewTabs = [
  { value: 'trade', label: '交易数据' },
  { value: 'user', label: '用户行为' },
  { value: 'image', label: '图像数据' },
  { value: 'device', label: '设备数据' }
]

// 计算属性
const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.pageSize))

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = pagination.value.page
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
    } else if (current >= total - 2) {
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      for (let i = current - 2; i <= current + 2; i++) {
        pages.push(i)
      }
    }
  }
  
  return pages
})

// 获取数据源图标
const getDataSourceIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    database: 'fas fa-database',
    api: 'fas fa-cloud',
    file: 'fas fa-file-alt',
    stream: 'fas fa-stream'
  }
  return iconMap[type] || 'fas fa-database'
}

// 获取状态样式
const getStatusIconClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success/10 text-success'
    case 'warning': return 'bg-warning/10 text-warning'
    case 'error': return 'bg-danger/10 text-danger'
    case 'stopped': return 'bg-gray-100 text-gray-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success/10 text-success'
    case 'warning': return 'bg-warning/10 text-warning'
    case 'error': return 'bg-danger/10 text-danger'
    case 'stopped': return 'bg-gray-100 text-gray-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getProgressBarClass = (status: string) => {
  switch (status) {
    case 'normal': return 'bg-success'
    case 'warning': return 'bg-warning'
    case 'error': return 'bg-danger'
    case 'stopped': return 'bg-gray-400'
    default: return 'bg-gray-400'
  }
}

const getTransactionStatusClass = (status: string) => {
  if (!status) return 'bg-gray-100 text-gray-600'
  const statusLower = status.toLowerCase()
  if (statusLower.includes('成功') || statusLower === 'success') return 'bg-success/10 text-success'
  if (statusLower.includes('处理') || statusLower === 'processing') return 'bg-warning/10 text-warning'
  if (statusLower.includes('失败') || statusLower === 'failed' || statusLower === 'fail') return 'bg-danger/10 text-danger'
  return 'bg-gray-100 text-gray-600'
}

// 格式化数字
const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN')
}

// 格式化金额
const formatAmount = (amount: number | string) => {
  if (typeof amount === 'string') return amount
  return `¥${amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// API 调用函数
const loadStatistics = async () => {
  try {
    const response = await getDataSourceStatistics()
    if (response.data.code === 200) {
      statistics.value = response.data.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadDataSources = async () => {
  try {
    loading.value = true
    const response = await getDataSources({
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      status: statusFilter.value === 'all' ? undefined : statusFilter.value,
      keyword: searchKeyword.value || undefined
    })
    
    if (response.data.code === 200) {
      dataSources.value = response.data.data.list
      pagination.value.total = response.data.data.total
      pagination.value.page = response.data.data.page
      pagination.value.pageSize = response.data.data.pageSize
      
      // 如果有数据源，默认选择第一个来加载预览和质量评分
      if (dataSources.value.length > 0 && !selectedSourceId.value) {
        selectedSourceId.value = dataSources.value[0].id
        loadPreviewData()
        loadQualityScore()
        loadQualityIssuesSummary()
      }
    }
  } catch (error) {
    console.error('加载数据源列表失败:', error)
    showToast('加载数据源列表失败', 'warning')
  } finally {
    loading.value = false
  }
}

const loadPreviewData = async () => {
  if (!selectedSourceId.value) return
  
  try {
    const response = await getDataPreview(selectedSourceId.value, {
      type: activePreviewTab.value,
      limit: 4
    })
    
    if (response.data.code === 200) {
      previewData.value = response.data.data.list
      previewTotal.value = response.data.data.total
    }
  } catch (error) {
    console.error('加载预览数据失败:', error)
  }
}

const loadQualityScore = async () => {
  if (!selectedSourceId.value) return
  
  try {
    const response = await getQualityScore(selectedSourceId.value)
    if (response.data.code === 200) {
      qualityScore.value = response.data.data
    }
  } catch (error) {
    console.error('加载质量评分失败:', error)
  }
}

const loadQualityIssuesSummary = async () => {
  if (!selectedSourceId.value) return
  
  try {
    const response = await getQualityIssues(selectedSourceId.value, {
      page: 1,
      pageSize: 1, // 只需要统计数据，不需要列表数据
      type: 'all'
    })
    
    if (response.data.code === 200) {
      const stats = response.data.data.statistics
      qualityIssuesSummary.value = [
        { id: '1', title: '缺失关键字段', description: '数据中缺少必填字段', count: stats.missing || 0, severity: 'high' as const, icon: 'fas fa-times-circle' },
        { id: '2', title: '格式错误', description: '数据格式不符合规范', count: stats.formatError || 0, severity: 'high' as const, icon: 'fas fa-exclamation-circle' },
        { id: '3', title: '值异常', description: '数据值超出正常范围', count: stats.abnormal || 0, severity: 'medium' as const, icon: 'fas fa-exclamation-triangle' },
        { id: '4', title: '数据不一致', description: '数据与历史记录不匹配', count: stats.inconsistent || 0, severity: 'medium' as const, icon: 'fas fa-question-circle' }
      ]
    }
  } catch (error) {
    console.error('加载质量问题汇总失败:', error)
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 文件选择处理
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    // 检查文件类型
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedExtensions.includes(fileExtension)) {
      showToast('不支持的文件格式，请上传 CSV、Excel、JSON 或 TXT 文件', 'warning')
      target.value = ''
      return
    }
    
    // 检查文件大小（限制为 50MB）
    const maxSize = 50 * 1024 * 1024
    if (file.size > maxSize) {
      showToast('文件大小不能超过 50MB', 'warning')
      target.value = ''
      return
    }
    
    selectedFile.value = file
    // 自动上传
    handleFileUpload()
  }
}

// 清除选中的文件
const clearSelectedFile = () => {
  selectedFile.value = null
  uploadProgress.value = 0
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 文件上传处理
const handleFileUpload = async () => {
  if (!selectedFile.value || uploading.value) return
  
  try {
    uploading.value = true
    uploadProgress.value = 10
    
    // 根据文件扩展名确定文件类型
    const fileExtension = selectedFile.value.name.split('.').pop()?.toLowerCase()
    let fileType = 'document'
    
    if (['csv', 'xlsx', 'xls'].includes(fileExtension || '')) {
      fileType = 'document'
    } else if (['json', 'txt'].includes(fileExtension || '')) {
      fileType = 'other'
    }
    
    uploadProgress.value = 30
    
    const response = await uploadFile(selectedFile.value, fileType)
    
    uploadProgress.value = 80
    
    if (response.data.code === 200) {
      uploadProgress.value = 100
      showToast(`文件上传成功：${response.data.data.originalName}`)
      
      // 上传成功后刷新数据源列表
      setTimeout(() => {
        clearSelectedFile()
        refreshData()
      }, 1000)
    } else {
      showToast(response.data.message || '上传失败', 'warning')
      uploadProgress.value = 0
    }
  } catch (error: any) {
    console.error('文件上传失败:', error)
    showToast(error.message || '文件上传失败', 'warning')
    uploadProgress.value = 0
  } finally {
    uploading.value = false
  }
}

// 事件处理函数
const openQualityModal = (source: ApiDataSource) => {
  selectedSource.value = source
  showQualityModal.value = true
}

const handleExportIssues = async () => {
  if (!selectedSource.value) return
  
  try {
    const response = await exportQualityIssues(selectedSource.value.id, {
      type: 'all',
      format: 'csv'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `数据质量问题_${selectedSource.value.name}_${new Date().getTime()}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    showToast('数据质量问题列表已导出为CSV文件')
    showQualityModal.value = false
  } catch (error) {
    console.error('导出失败:', error)
    showToast('导出失败', 'warning')
  }
}

const handleReconnect = async (sourceId: number) => {
  if (reconnectingIds.value.includes(sourceId)) return
  
  try {
    reconnectingIds.value.push(sourceId)
    const response = await reconnectDataSource(sourceId)
    
    if (response.data.code === 200) {
      showToast('重新连接成功')
      // 重新加载数据
      await loadDataSources()
      await loadStatistics()
    }
  } catch (error) {
    console.error('重新连接失败:', error)
    showToast('重新连接失败', 'warning')
  } finally {
    reconnectingIds.value = reconnectingIds.value.filter(id => id !== sourceId)
  }
}

const handlePageChange = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  pagination.value.page = page
  loadDataSources()
}

const refreshData = async () => {
  await Promise.all([
    loadStatistics(),
    loadDataSources()
  ])
  
  if (selectedSourceId.value) {
    await Promise.all([
      loadPreviewData(),
      loadQualityScore(),
      loadQualityIssuesSummary()
    ])
  }
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

// 监听搜索关键词变化
watch(searchKeyword, () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = window.setTimeout(() => {
    pagination.value.page = 1
    loadDataSources()
  }, 500)
})

// 监听状态筛选变化
watch(statusFilter, () => {
  pagination.value.page = 1
  loadDataSources()
})

// 事件处理函数
const handlePreviewTabChange = (tab: string) => {
  activePreviewTab.value = tab
  if (selectedSourceId.value) {
    loadPreviewData()
  }
}

// 监听数据源选择变化
watch(() => dataSources.value, (newSources) => {
  if (newSources.length > 0 && !selectedSourceId.value) {
    selectedSourceId.value = newSources[0].id
    loadPreviewData()
    loadQualityScore()
    loadQualityIssuesSummary()
  }
}, { deep: true })

// 监听选中的数据源ID变化
watch(selectedSourceId, (newId) => {
  if (newId) {
    loadPreviewData()
    loadQualityScore()
    loadQualityIssuesSummary()
  }
})

onMounted(async () => {
  await refreshData()
  
  // 设置自动刷新
  refreshTimer = window.setInterval(() => {
    refreshData()
  }, 30000) // 30秒刷新一次
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})
</script>

<style scoped>
/* 组件样式 */
</style>

