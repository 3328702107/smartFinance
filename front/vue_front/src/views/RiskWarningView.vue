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
              <select v-model="filters.eventType" class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-48">
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
              <select v-model="filters.alertLevel" class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-36">
                <option value="all">全部级别</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
            
            <!-- 状态筛选 -->
            <div>
              <label class="block text-sm text-light-dark mb-1">处理状态</label>
              <select v-model="filters.status" class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-36">
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
              <select v-model="filters.timeRange" class="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-40">
                <option value="today">今日</option>
                <option value="yesterday">昨日</option>
                <option value="7days">近7天</option>
                <option value="30days">近30天</option>
                <option value="custom">自定义</option>
              </select>
            </div>
          </div>
          
          <div class="flex flex-wrap gap-3">
            <!-- 搜索框 -->
            <div class="relative">
              <input 
                v-model="searchKeyword"
                type="text" 
                placeholder="搜索告警ID/关键词..." 
                class="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth w-full md:w-64"
              >
              <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-light-dark"></i>
            </div>
            
            <!-- 批量操作 -->
            <div class="relative">
              <button 
                @click="toggleBatchMenu"
                class="flex items-center justify-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:border-primary hover:text-primary transition-smooth"
              >
                <i class="fas fa-cog mr-2"></i>批量操作
              </button>
              <div 
                v-show="showBatchMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10"
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
              @click="refreshData"
              class="flex items-center justify-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:border-primary hover:text-primary transition-smooth"
            >
              <i class="fas fa-refresh mr-2"></i>刷新
            </button>
          </div>
        </div>
      </section>
      
      <!-- 告警列表 -->
      <section class="bg-white rounded-xl card-shadow overflow-hidden">
        <div class="overflow-x-auto">
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
                class="table-hover-row cursor-pointer"
                @click="openAlertDetails(alert)"
              >
                <td class="px-6 py-4 whitespace-nowrap" @click.stop>
                  <input 
                    type="checkbox" 
                    v-model="alert.selected"
                    class="rounded text-primary focus:ring-primary"
                  >
                </td>
                <td class="px-6 py-4 whitespace-nowrap font-medium">{{ alert.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ alert.eventType }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getLevelClass(alert.level)"
                  >
                    {{ alert.level }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-light-dark">{{ alert.triggerTime }}</td>
                <td class="px-6 py-4 whitespace-nowrap" @click.stop>
                  <select 
                    v-model="alert.status"
                    @change="updateAlertStatus(alert)"
                    class="border-none bg-transparent font-medium focus:outline-none focus:ring-0"
                    :class="getStatusClass(alert.status)"
                  >
                    <option value="pending">待处理</option>
                    <option value="processing">处理中</option>
                    <option value="resolved">已解决</option>
                    <option value="ignored">已忽略</option>
                  </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-light-dark">{{ alert.handler || '-' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium" @click.stop>
                  <button 
                    @click="openAlertDetails(alert)"
                    class="text-primary hover:text-primary/80 mr-3"
                  >
                    查看
                  </button>
                  <button class="text-light-dark hover:text-dark">
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分页 -->
        <div class="p-6 border-t border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-sm text-light-dark">
            显示 1-5 条，共 {{ totalCount }} 条
          </div>
          <div class="flex space-x-1">
            <button 
              :disabled="currentPage === 1"
              @click="currentPage--"
              class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-angle-left"></i>
            </button>
            <button 
              v-for="page in totalPages" 
              :key="page"
              @click="currentPage = page"
              class="w-9 h-9 flex items-center justify-center rounded-md transition-smooth"
              :class="currentPage === page 
                ? 'bg-primary text-white' 
                : 'border border-gray-200 hover:border-primary hover:text-primary'"
            >
              {{ page }}
            </button>
            <button 
              :disabled="currentPage === totalPages"
              @click="currentPage++"
              class="w-9 h-9 flex items-center justify-center rounded-md border border-gray-200 text-light-dark hover:border-primary hover:text-primary transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-angle-right"></i>
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
      @close="showAlertModal = false"
      @ignore="handleIgnore"
      @investigate="handleInvestigate"
      @resolve="handleResolve"
    />
    
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'
import AlertDetailsModal from '@/components/AlertDetailsModal.vue'

interface Alert {
  id: string
  eventType: string
  level: string
  triggerTime: string
  status: string
  handler: string
  selected: boolean
}

const filters = reactive({
  eventType: 'all',
  alertLevel: 'all',
  status: 'all',
  timeRange: 'today'
})

const searchKeyword = ref('')
const showBatchMenu = ref(false)
const selectAll = ref(false)
const currentPage = ref(1)
const totalCount = ref(147)
const showAlertModal = ref(false)
const selectedAlert = ref<Alert | null>(null)

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

const alertList = ref<Alert[]>([
  { id: 'ALERT-20230615-001', eventType: '账户盗用风险', level: '高', triggerTime: '2023-06-15 10:24:35', status: 'pending', handler: '', selected: false },
  { id: 'ALERT-20230615-002', eventType: '异常交易', level: '中', triggerTime: '2023-06-15 09:15:22', status: 'pending', handler: '', selected: false },
  { id: 'ALERT-20230615-003', eventType: '证件伪造嫌疑', level: '低', triggerTime: '2023-06-15 08:42:17', status: 'resolved', handler: '李审核', selected: false },
  { id: 'ALERT-20230615-004', eventType: '批量恶意注册', level: '高', triggerTime: '2023-06-15 07:36:51', status: 'processing', handler: '王风控', selected: false },
  { id: 'ALERT-20230614-056', eventType: '设备异常登录', level: '中', triggerTime: '2023-06-14 22:18:44', status: 'ignored', handler: '张经理', selected: false }
])

const totalPages = computed(() => Math.ceil(totalCount.value / 5))

const getLevelClass = (level: string) => {
  switch (level) {
    case '高': return 'bg-danger/10 text-danger'
    case '中': return 'bg-warning/10 text-warning'
    case '低': return 'bg-info/10 text-info'
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

const batchAction = (action: string) => {
  const selectedCount = alertList.value.filter(a => a.selected).length
  if (selectedCount === 0) {
    showToast('请先选择要操作的告警', 'warning')
    return
  }
  
  let actionText = ''
  switch (action) {
    case 'resolve': actionText = '已批量标记为已解决'; break
    case 'ignore': actionText = '已批量标记为已忽略'; break
    case 'process': actionText = '已批量标记为处理中'; break
    case 'delete': actionText = '已批量删除选中告警'; break
  }
  
  showToast(`${actionText} (共 ${selectedCount} 项)`)
  showBatchMenu.value = false
}

const updateAlertStatus = (alert: Alert) => {
  const statusText = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    ignored: '已忽略'
  }[alert.status]
  showToast(`告警 ${alert.id} 已更新为 ${statusText}`)
}

const openAlertDetails = (alert: Alert) => {
  selectedAlert.value = alert
  showAlertModal.value = true
}

const handleIgnore = () => {
  showToast('已标记为忽略')
  showAlertModal.value = false
}

const handleInvestigate = () => {
  showToast('已标记为进一步调查')
  showAlertModal.value = false
}

const handleResolve = () => {
  showToast('已标记为已处理')
  showAlertModal.value = false
}

const refreshData = () => {
  showToast('数据已更新')
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}
</script>

<style scoped>
/* 组件样式 */
</style>

