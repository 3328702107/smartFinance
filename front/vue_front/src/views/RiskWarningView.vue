<template>
  <div class="font-inter bg-gray-50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- 筛选工具栏 -->
      <section class="mb-6 bg-white rounded-xl p-4 card-shadow">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex flex-wrap gap-3">
            <!-- 事件类型筛选 -->
            <div>
              <label class="block text-sm text-light-dark mb-1">事件类型</label>
              <select 
                v-model="filters.eventType" 
                @change="handleFilterChange"
                class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-48"
              >
                <option value="all">全部类型</option>
                <option value="account">账户风险</option>
                <option value="transaction">交易风险</option>
                <option value="identity">身份验证</option>
                <option value="device">设备异常</option>
                <option value="behavior">行为异常</option>
              </select>
            </div>
            
            <!-- 告警级别筛选 -->
            <div>
              <label class="block text-sm text-light-dark mb-1">告警级别</label>
              <select 
                v-model="filters.level" 
                @change="handleFilterChange"
                class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-36"
              >
                <option value="all">全部级别</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
            
            <!-- 状态筛选 -->
            <div>
              <label class="block text-sm text-light-dark mb-1">处理状态</label>
              <select 
                v-model="filters.status" 
                @change="handleFilterChange"
                class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-36"
              >
                <option value="all">全部状态</option>
                <option value="pending">待处理</option>
                <option value="processing">处理中</option>
                <option value="resolved">已解决</option>
                <option value="ignored">已忽略</option>
              </select>
            </div>
            
            <!-- 时间筛选 -->
            <div>
              <label class="block text-sm text-light-dark mb-1">时间范围</label>
              <select 
                v-model="filters.timeRange" 
                @change="handleFilterChange"
                class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-40"
              >
                <option value="all">全部时间</option>
                <option value="today">今日</option>
                <option value="yesterday">昨日</option>
                <option value="7days">近7天</option>
                <option value="30days">近30天</option>
              </select>
            </div>
          </div>
          
          <div class="flex flex-wrap gap-3">
            <!-- 搜索框 -->
            <div class="relative">
              <input 
                v-model="searchKeyword"
                @keyup.enter="handleSearch"
                type="text" 
                placeholder="搜索告警ID/关键词..." 
                class="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-64"
              >
              <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-light-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            
            <!-- 批量操作 -->
            <div class="relative">
              <button 
                @click="toggleBatchMenu"
                class="flex items-center justify-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:border-primary hover:text-primary transition-smooth"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                批量操作
              </button>
              <div 
                v-show="showBatchMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-100"
              >
                <a href="#" @click.prevent="batchAction('resolve')" class="block px-4 py-2 text-sm text-light-dark hover:bg-primary hover:text-white transition-smooth">批量标记为已解决</a>
                <a href="#" @click.prevent="batchAction('ignore')" class="block px-4 py-2 text-sm text-light-dark hover:bg-primary hover:text-white transition-smooth">批量标记为已忽略</a>
                <a href="#" @click.prevent="batchAction('process')" class="block px-4 py-2 text-sm text-light-dark hover:bg-primary hover:text-white transition-smooth">批量标记为处理中</a>
                <div class="border-t border-gray-100 my-1"></div>
                <a href="#" @click.prevent="batchAction('delete')" class="block px-4 py-2 text-sm text-danger hover:bg-danger hover:text-white transition-smooth">批量删除</a>
              </div>
            </div>
            
            <!-- 刷新按钮 -->
            <button 
              @click="fetchAlertList"
              :disabled="loading"
              class="flex items-center justify-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50"
            >
              <svg 
                class="w-4 h-4 mr-2" 
                :class="loading ? 'animate-spin' : ''"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新
            </button>
          </div>
        </div>
      </section>
      
      <!-- 告警列表 -->
      <section class="bg-white rounded-xl card-shadow overflow-hidden">
        <!-- 加载状态 -->
        <div v-if="loading" class="p-12 text-center">
          <svg class="w-8 h-8 mx-auto animate-spin text-primary" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-2 text-light-dark">加载中...</p>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="alertList.length === 0" class="p-12 text-center">
          <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="mt-4 text-light-dark">暂无告警数据</p>
        </div>
        
        <!-- 告警表格 -->
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50 border-b border-gray-200">
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider w-12">
                  <input 
                    type="checkbox" 
                    v-model="selectAll"
                    @change="toggleSelectAll"
                    class="rounded text-primary focus:ring-primary"
                  >
                </th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">告警ID</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">事件类型</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">告警级别</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">触发时间</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">状态</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-light-dark uppercase tracking-wider">处理人</th>
                <th class="px-6 py-4 text-right text-xs font-medium text-light-dark uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr 
                v-for="alert in alertList" 
                :key="alert.id"
                class="hover:bg-gray-50 transition-smooth cursor-pointer"
                @click="openAlertDetails(alert)"
              >
                <td class="px-6 py-4 whitespace-nowrap" @click.stop>
                  <input 
                    type="checkbox" 
                    v-model="alert.selected"
                    class="rounded text-primary focus:ring-primary"
                  >
                </td>
                <td class="px-6 py-4 whitespace-nowrap font-medium text-primary">{{ alert.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ alert.eventTypeName }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getLevelClass(alert.level)"
                  >
                    {{ alert.levelName }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-light-dark">{{ alert.triggerTime }}</td>
                <td class="px-6 py-4 whitespace-nowrap" @click.stop>
                  <select 
                    v-model="alert.status"
                    @change="handleUpdateStatus(alert)"
                    class="border-none bg-transparent font-medium focus:outline-none focus:ring-0 cursor-pointer"
                    :class="getStatusClass(alert.status)"
                  >
                    <option value="pending">待处理</option>
                    <option value="processing">处理中</option>
                    <option value="resolved">已解决</option>
                    <option value="ignored">已忽略</option>
                  </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-light-dark">{{ alert.handlerName || '-' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium" @click.stop>
                  <button 
                    @click="openAlertDetails(alert)"
                    class="text-primary hover:text-primary/80 mr-3"
                  >
                    查看
                  </button>
                  <button 
                    @click="handleQuickResolve(alert)"
                    class="text-success hover:text-success/80"
                  >
                    处理
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分页 -->
        <div v-if="!loading && alertList.length > 0" class="p-6 border-t border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-sm text-light-dark">
            显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalCount) }} 条，共 {{ totalCount }} 条
          </div>
          <div class="flex items-center gap-2">
            <button 
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
              class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </button>
            <button 
              v-for="page in displayedPages" 
              :key="page"
              @click="goToPage(page)"
              class="w-9 h-9 flex items-center justify-center rounded-md transition-smooth"
              :class="currentPage === page 
                ? 'bg-primary text-white' 
                : 'border border-gray-200 hover:border-primary hover:text-primary'"
            >
              {{ page }}
            </button>
            <button 
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
              class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
    
    <!-- 告警详情模态框 -->
    <AlertDetailsModal 
      v-if="showAlertModal"
      :alert="selectedAlert"
      :alert-detail="alertDetail"
      :loading-detail="loadingDetail"
      @close="showAlertModal = false"
      @ignore="handleIgnore"
      @investigate="handleInvestigate"
      @resolve="handleResolve"
    />
    
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'
import AlertDetailsModal from '@/components/AlertDetailsModal.vue'

// API 导入
import { 
  getAlertList, 
  getAlertDetail, 
  updateAlertStatus as apiUpdateAlertStatus, 
  batchOperateAlerts 
} from '@/api/alerts'

// 告警项接口
interface AlertListItem {
  id: string
  eventType: string
  eventTypeName: string
  level: string
  levelName: string
  status: string
  statusName: string
  triggerTime: string
  handler: string
  handlerName: string
  selected: boolean
}

// 筛选条件
const filters = reactive({
  eventType: 'all',
  level: 'all',
  status: 'all',
  timeRange: 'all'
})

// 状态
const searchKeyword = ref('')
const showBatchMenu = ref(false)
const selectAll = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const loading = ref(false)
const loadingDetail = ref(false)
const showAlertModal = ref(false)
const selectedAlert = ref<AlertListItem | null>(null)
const alertDetail = ref<any>(null)

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

const alertList = ref<AlertListItem[]>([])

// 计算属性
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

const displayedPages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(5, total)
    } else {
      start = Math.max(1, total - 4)
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// API 调用
const fetchAlertList = async () => {
  loading.value = true
  try {
    const { data: res } = await getAlertList({
      page: currentPage.value,
      pageSize: pageSize.value,
      eventType: filters.eventType,
      level: filters.level,
      status: filters.status,
      timeRange: filters.timeRange,
      keyword: searchKeyword.value
    })
    
    if (res.code === 200 && res.data) {
      alertList.value = res.data.list.map((item: any) => ({
        ...item,
        selected: false
      }))
      totalCount.value = res.data.total
    }
  } catch (error) {
    console.error('获取告警列表失败:', error)
    showToast('获取告警列表失败', 'warning')
  } finally {
    loading.value = false
  }
}

const fetchAlertDetail = async (alertId: string) => {
  loadingDetail.value = true
  try {
    const { data: res } = await getAlertDetail(alertId)
    if (res.code === 200 && res.data) {
      alertDetail.value = res.data
    }
  } catch (error) {
    console.error('获取告警详情失败:', error)
  } finally {
    loadingDetail.value = false
  }
}

// 事件处理
const handleFilterChange = () => {
  currentPage.value = 1
  fetchAlertList()
}

const handleSearch = () => {
  currentPage.value = 1
  fetchAlertList()
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchAlertList()
  }
}

const getLevelClass = (level: string) => {
  switch (level) {
    case 'high': return 'bg-danger/10 text-danger'
    case 'medium': return 'bg-warning/10 text-warning'
    case 'low': return 'bg-info/10 text-info'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'pending': return 'text-warning'
    case 'processing': return 'text-primary'
    case 'resolved': return 'text-success'
    case 'ignored': return 'text-light-dark'
    default: return 'text-light-dark'
  }
}

const toggleBatchMenu = () => {
  showBatchMenu.value = !showBatchMenu.value
}

const toggleSelectAll = () => {
  alertList.value.forEach(alert => {
    alert.selected = selectAll.value
  })
}

const batchAction = async (action: string) => {
  const selectedIds = alertList.value.filter(a => a.selected).map(a => a.id)
  if (selectedIds.length === 0) {
    showToast('请先选择要操作的告警', 'warning')
    return
  }
  
  try {
    const { data: res } = await batchOperateAlerts({
      alertIds: selectedIds,
      action
    })
    
    if (res.code === 200) {
      const actionText: Record<string, string> = {
        resolve: '已批量标记为已解决',
        ignore: '已批量标记为已忽略',
        process: '已批量标记为处理中',
        delete: '已批量删除'
      }
      showToast(`${actionText[action]} (成功 ${res.data?.successCount || selectedIds.length} 项)`)
      fetchAlertList()
    }
  } catch (error) {
    showToast('批量操作失败', 'warning')
  }
  
  showBatchMenu.value = false
}

const handleUpdateStatus = async (alert: AlertListItem) => {
  try {
    const { data: res } = await apiUpdateAlertStatus(alert.id, alert.status)
    if (res.code === 200) {
      const statusText: Record<string, string> = {
        pending: '待处理',
        processing: '处理中',
        resolved: '已解决',
        ignored: '已忽略'
      }
      showToast(`告警 ${alert.id} 已更新为 ${statusText[alert.status]}`)
    }
  } catch (error) {
    showToast('更新状态失败', 'warning')
    fetchAlertList() // 回滚状态
  }
}

const handleQuickResolve = async (alert: AlertListItem) => {
  try {
    const { data: res } = await apiUpdateAlertStatus(alert.id, 'resolved')
    if (res.code === 200) {
      alert.status = 'resolved'
      showToast(`告警 ${alert.id} 已标记为已解决`)
    }
  } catch (error) {
    showToast('操作失败', 'warning')
  }
}

const openAlertDetails = (alert: AlertListItem) => {
  selectedAlert.value = alert
  alertDetail.value = null
  showAlertModal.value = true
  fetchAlertDetail(alert.id)
}

const handleIgnore = async () => {
  if (selectedAlert.value) {
    try {
      await apiUpdateAlertStatus(selectedAlert.value.id, 'ignored')
      showToast('已标记为忽略')
      showAlertModal.value = false
      // 刷新列表以获取最新的处理人信息
      fetchAlertList()
    } catch (error) {
      showToast('操作失败', 'warning')
    }
  }
}

const handleInvestigate = async () => {
  if (selectedAlert.value) {
    try {
      await apiUpdateAlertStatus(selectedAlert.value.id, 'processing')
      showToast('已标记为处理中')
      showAlertModal.value = false
      // 刷新列表以获取最新的处理人信息
      fetchAlertList()
    } catch (error) {
      showToast('操作失败', 'warning')
    }
  }
}

const handleResolve = async () => {
  if (selectedAlert.value) {
    try {
      await apiUpdateAlertStatus(selectedAlert.value.id, 'resolved')
      showToast('已标记为已解决')
      showAlertModal.value = false
      // 刷新列表以获取最新的处理人信息
      fetchAlertList()
    } catch (error) {
      showToast('操作失败', 'warning')
    }
  }
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

// 监听点击外部关闭批量菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showBatchMenu.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchAlertList()
  document.addEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 组件样式 */
</style>
