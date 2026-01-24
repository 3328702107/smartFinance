<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-xl font-bold">告警详情 - {{ alert?.id }}</h3>
        <button @click="$emit('close')" class="text-light-dark hover:text-dark transition-smooth">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>
      
      <!-- 模态框内容 -->
      <div class="flex-grow overflow-y-auto p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h4 class="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">基本信息</h4>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-light-dark">告警ID:</span>
                <span>{{ alert?.id }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">事件类型:</span>
                <span>{{ alert?.eventType }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">告警级别:</span>
                <span>
                  <span 
                    class="px-2 py-0.5 text-xs rounded-full"
                    :class="getLevelClass(alert?.level || '')"
                  >
                    {{ alert?.level }}
                  </span>
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">触发时间:</span>
                <span>{{ alert?.triggerTime }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">当前状态:</span>
                <span>
                  <span 
                    class="px-2 py-0.5 text-xs rounded-full"
                    :class="getStatusBadgeClass(alert?.status || '')"
                  >
                    {{ getStatusText(alert?.status || '') }}
                  </span>
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">触发规则:</span>
                <span>异地异常登录检测规则 v2.3</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">风险评分:</span>
                <span class="font-medium text-danger">92分</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 class="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">用户信息</h4>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-light-dark">用户ID:</span>
                <span>USER-789456</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">用户名:</span>
                <span>wangxiaoming</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">注册时间:</span>
                <span>2022-03-15</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">账户等级:</span>
                <span>VIP会员</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">联系电话:</span>
                <span>138****5678</span>
              </div>
              <div class="flex justify-between">
                <span class="text-light-dark">最近登录:</span>
                <span>2023-06-14 20:15:32 (上海)</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mb-6">
          <h4 class="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">事件详情</h4>
          <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-4">
            <p class="text-sm mb-3">该用户账户在异地IP地址登录，与常用登录地差异较大，且登录设备为新设备。登录IP地址为185.173.89.xxx，地理位置显示为俄罗斯莫斯科，而用户常用登录地为中国上海。</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <h5 class="font-medium mb-2">异常登录信息</h5>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="text-light-dark">IP地址:</span>
                    <span>185.173.89.xxx</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">登录地点:</span>
                    <span>俄罗斯 莫斯科</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">登录设备:</span>
                    <span>Windows 10 / Chrome 112.0.5615.138</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">登录方式:</span>
                    <span>密码登录</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h5 class="font-medium mb-2">历史正常登录模式</h5>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="text-light-dark">常用IP段:</span>
                    <span>101.89.*.* / 116.23.*.*</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">常用地点:</span>
                    <span>中国 上海</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">常用设备:</span>
                    <span>iPhone 13 / Safari</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-light-dark">常用时段:</span>
                    <span>19:00 - 22:00</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mb-6">
          <h4 class="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">检测结果与建议</h4>
          <div class="bg-white p-4 rounded-lg border border-gray-200 mb-4">
            <h5 class="font-medium mb-2">风险评估</h5>
            <p class="text-sm mb-4">该用户账户在异地IP地址登录，与常用登录地差异较大，且登录设备为新设备。历史上该用户无类似异常行为记录，存在账户盗用风险，建议立即采取验证措施。</p>
            
            <h5 class="font-medium mb-2">处理建议</h5>
            <ul class="text-sm list-disc pl-5 space-y-1 mb-4">
              <li>向用户注册手机发送验证码，要求二次验证</li>
              <li>暂时冻结账户敏感操作权限</li>
              <li>联系用户确认是否为本人操作</li>
              <li>如确认非本人操作，立即锁定账户并引导用户修改密码</li>
            </ul>
          </div>
        </div>
        
        <div>
          <h4 class="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">处理记录</h4>
          <div class="space-y-4">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="flex justify-between items-start mb-2">
                <div class="flex items-center">
                  <span class="text-xs font-medium px-2 py-0.5 bg-gray-200 text-light-dark rounded-full">系统创建</span>
                  <span class="ml-2 text-sm font-medium">系统自动生成告警</span>
                </div>
                <span class="text-xs text-light-dark">2023-06-15 10:24:35</span>
              </div>
              <p class="text-sm text-light-dark">系统检测到异常登录行为，自动创建高风险告警</p>
            </div>
          </div>
          
          <!-- 处理记录输入框 -->
          <div class="mt-4">
            <textarea 
              v-model="processingNote"
              rows="3" 
              class="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth resize-none" 
              placeholder="请输入处理记录..."
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- 模态框底部 -->
      <div class="p-6 border-t border-gray-200 flex justify-end space-x-3">
        <button 
          @click="$emit('ignore')"
          class="px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth"
        >
          忽略
        </button>
        <button 
          @click="$emit('investigate')"
          class="px-4 py-2 border border-warning text-warning rounded-lg hover:bg-warning/5 transition-smooth"
        >
          进一步调查
        </button>
        <button 
          @click="$emit('resolve')"
          class="px-4 py-2 bg-success text-white rounded-lg hover:bg-success/90 transition-smooth"
        >
          标记为已处理
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Alert {
  id: string
  eventType: string
  level: string
  triggerTime: string
  status: string
  handler: string
  selected: boolean
}

defineProps<{
  alert: Alert | null
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
    case '高': return 'bg-danger/10 text-danger'
    case '中': return 'bg-warning/10 text-warning'
    case '低': return 'bg-info/10 text-info'
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
  switch (status) {
    case 'pending': return '待处理'
    case 'processing': return '处理中'
    case 'resolved': return '已解决'
    case 'ignored': return '已忽略'
    default: return status
  }
}
</script>

