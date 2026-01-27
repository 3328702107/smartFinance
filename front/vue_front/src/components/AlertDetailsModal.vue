<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
      <!-- 模态框头部 -->
      <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-gray-50 to-white">
        <div>
          <h3 class="text-xl font-bold text-dark">告警详情</h3>
          <p class="text-sm text-light-dark mt-0.5">{{ alert?.id }}</p>
        </div>
        <button 
          @click="$emit('close')" 
          class="w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      <!-- 模态框内容 -->
      <div class="flex-grow overflow-y-auto p-6">
        <!-- 加载状态 -->
        <div v-if="loadingDetail" class="py-12 text-center">
          <svg class="w-8 h-8 mx-auto animate-spin text-primary" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-2 text-light-dark">加载详情中...</p>
        </div>
        
        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <!-- 基本信息 -->
            <div class="bg-gray-50 rounded-xl p-5">
              <h4 class="text-base font-semibold mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                基本信息
              </h4>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-light-dark">告警ID:</span>
                  <span class="font-medium">{{ alertDetail?.id || alert?.id }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">事件类型:</span>
                  <span>{{ alertDetail?.eventTypeName || alert?.eventTypeName }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-light-dark">告警级别:</span>
                  <span 
                    class="px-2.5 py-0.5 text-xs font-medium rounded-full"
                    :class="getLevelClass(alertDetail?.level || alert?.level || '')"
                  >
                    {{ alertDetail?.levelName || alert?.levelName }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">触发时间:</span>
                  <span>{{ alertDetail?.triggerTime || alert?.triggerTime }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-light-dark">当前状态:</span>
                  <span 
                    class="px-2.5 py-0.5 text-xs font-medium rounded-full"
                    :class="getStatusBadgeClass(alertDetail?.status || alert?.status || '')"
                  >
                    {{ getStatusText(alertDetail?.status || alert?.status || '') }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">触发规则:</span>
                  <span>{{ alertDetail?.rule || '系统自动检测' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">风险评分:</span>
                  <span class="font-semibold" :class="getRiskScoreClass(alertDetail?.riskScore)">
                    {{ alertDetail?.riskScore || '-' }}分
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 用户信息 -->
            <div class="bg-gray-50 rounded-xl p-5">
              <h4 class="text-base font-semibold mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                用户信息
              </h4>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-light-dark">用户ID:</span>
                  <span class="font-medium">{{ alertDetail?.userInfo?.userId || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">用户名:</span>
                  <span>{{ alertDetail?.userInfo?.username || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">姓名:</span>
                  <span>{{ alertDetail?.userInfo?.name || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">注册时间:</span>
                  <span>{{ alertDetail?.userInfo?.registerTime || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">账户等级:</span>
                  <span>{{ alertDetail?.userInfo?.level || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">联系电话:</span>
                  <span>{{ alertDetail?.userInfo?.phone || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-light-dark">最近登录:</span>
                  <span>{{ alertDetail?.userInfo?.lastLogin || '-' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 事件详情 -->
          <div class="mb-6">
            <h4 class="text-base font-semibold mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              事件详情
            </h4>
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-5 rounded-xl border border-blue-100">
              <p class="text-sm mb-4 text-dark leading-relaxed">
                {{ alertDetail?.riskAssessment || '暂无详细描述' }}
              </p>
              
              <div v-if="alertDetail?.eventDetails" class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-sm">
                <div class="bg-white p-4 rounded-lg">
                  <h5 class="font-medium mb-3 text-dark flex items-center">
                    <span class="w-2 h-2 bg-danger rounded-full mr-2"></span>
                    异常登录信息
                  </h5>
                  <div class="space-y-2">
                    <div class="flex justify-between">
                      <span class="text-light-dark">IP地址:</span>
                      <span>{{ alertDetail?.eventDetails?.abnormalLogin?.ip || alertDetail?.eventDetails?.loginIp || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">登录地点:</span>
                      <span>{{ alertDetail?.eventDetails?.abnormalLogin?.location || alertDetail?.eventDetails?.loginLocation || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">登录设备:</span>
                      <span>{{ alertDetail?.eventDetails?.abnormalLogin?.device || alertDetail?.eventDetails?.device || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">登录方式:</span>
                      <span>{{ alertDetail?.eventDetails?.abnormalLogin?.loginMethod || '-' }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg">
                  <h5 class="font-medium mb-3 text-dark flex items-center">
                    <span class="w-2 h-2 bg-success rounded-full mr-2"></span>
                    正常登录模式
                  </h5>
                  <div class="space-y-2">
                    <div class="flex justify-between">
                      <span class="text-light-dark">常用IP:</span>
                      <span>{{ alertDetail?.eventDetails?.normalPattern?.commonIp || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">常用地点:</span>
                      <span>{{ alertDetail?.eventDetails?.normalPattern?.commonLocation || alertDetail?.eventDetails?.commonLocation || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">常用设备:</span>
                      <span>{{ alertDetail?.eventDetails?.normalPattern?.commonDevice || alertDetail?.eventDetails?.commonDevice || '-' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-light-dark">常用时间:</span>
                      <span>{{ alertDetail?.eventDetails?.normalPattern?.commonTime || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 处理记录 -->
          <div>
            <h4 class="text-base font-semibold mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
              </svg>
              处理记录
            </h4>
            <div class="space-y-3">
              <div 
                v-for="(record, index) in alertDetail?.processingRecords || []" 
                :key="index"
                class="bg-gray-50 p-4 rounded-xl border border-gray-100"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center">
                    <span 
                      class="text-xs font-medium px-2 py-0.5 rounded-full"
                      :class="record.type === 'system' ? 'bg-gray-200 text-gray-600' : 'bg-primary/10 text-primary'"
                    >
                      {{ record.typeName }}
                    </span>
                    <span class="ml-2 text-sm font-medium">{{ record.handlerName }}</span>
                  </div>
                  <span class="text-xs text-light-dark">{{ record.time }}</span>
                </div>
                <p class="text-sm text-light-dark">{{ record.note }}</p>
              </div>
              
              <!-- 无记录提示 -->
              <div 
                v-if="!alertDetail?.processingRecords?.length"
                class="bg-gray-50 p-4 rounded-xl border border-gray-100 text-center text-light-dark text-sm"
              >
                暂无处理记录
              </div>
            </div>
            
            <!-- 处理记录输入框 -->
            <div class="mt-4">
              <textarea 
                v-model="processingNote"
                rows="3" 
                class="w-full border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-smooth resize-none" 
                placeholder="请输入处理备注..."
              ></textarea>
            </div>
          </div>
        </template>
      </div>
      
      <!-- 模态框底部 -->
      <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3 bg-gray-50">
        <button 
          @click="$emit('ignore')"
          class="px-5 py-2.5 border border-gray-200 rounded-xl text-light-dark hover:bg-white transition-smooth font-medium"
        >
          忽略
        </button>
        <button 
          @click="$emit('investigate')"
          class="px-5 py-2.5 border-2 border-warning text-warning rounded-xl hover:bg-warning hover:text-white transition-smooth font-medium"
        >
          进一步调查
        </button>
        <button 
          @click="$emit('resolve')"
          class="px-5 py-2.5 bg-gradient-to-r from-success to-emerald-500 text-white rounded-xl hover:shadow-lg hover:shadow-success/25 transition-smooth font-medium"
        >
          标记为已处理
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface AlertItem {
  id: string
  eventType?: string
  eventTypeName?: string
  level?: string
  levelName?: string
  status?: string
  statusName?: string
  triggerTime?: string
  handler?: string
  handlerName?: string
  selected?: boolean
}

interface AlertDetail {
  id: string
  eventType: string
  eventTypeName: string
  level: string
  levelName: string
  status: string
  statusName: string
  triggerTime: string
  rule: string
  riskScore: number
  basicInfo?: {
    alertId?: string
    eventType?: string
    level?: string
    triggerTime?: string
    status?: string
    rule?: string
    riskScore?: number
    phone?: string
    email?: string
  }
  userInfo?: {
    userId: string
    username: string
    name: string
    registerTime: string
    level: string
    phone?: string
    lastLogin: string | null
  }
  eventDetails?: {
    description?: string
    // 后端返回嵌套格式
    abnormalLogin?: {
      ip?: string
      location?: string
      device?: string
      loginMethod?: string
    }
    normalPattern?: {
      commonIp?: string
      commonLocation?: string
      commonDevice?: string
      commonTime?: string
    }
    // 兼容扁平格式
    loginIp?: string
    loginLocation?: string
    commonLocation?: string
    device?: string
    commonDevice?: string
  }
  riskAssessment?: string
  processingRecords?: Array<{
    type: string
    typeName: string
    handler: string
    handlerName: string
    time: string
    note: string
  }>
}

defineProps<{
  alert: AlertItem | null
  alertDetail?: AlertDetail | null
  loadingDetail?: boolean
}>()

defineEmits<{
  close: []
  ignore: []
  investigate: []
  resolve: []
}>()

const processingNote = ref('')

const getLevelClass = (level: string) => {
  switch (level) {
    case 'high': return 'bg-danger/10 text-danger'
    case 'medium': return 'bg-warning/10 text-warning'
    case 'low': return 'bg-info/10 text-info'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'pending': return 'bg-warning/10 text-warning'
    case 'processing': return 'bg-primary/10 text-primary'
    case 'resolved': return 'bg-success/10 text-success'
    case 'ignored': return 'bg-gray-100 text-light-dark'
    default: return 'bg-gray-100 text-light-dark'
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    ignored: '已忽略'
  }
  return statusMap[status] || status
}

const getRiskScoreClass = (score?: number) => {
  if (!score) return 'text-gray-400'
  if (score >= 80) return 'text-danger'
  if (score >= 50) return 'text-warning'
  return 'text-success'
}
</script>
