<template>
  <div class="font-inter bg-gray-50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- 事件标题和基本信息 -->
      <div class="mb-6">
        <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
          <div>
            <div class="flex flex-wrap items-center gap-3 mb-2">
              <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-dark">疑似账户盗用事件分析</h2>
              <span class="px-3 py-1 bg-danger/10 text-danger text-sm rounded-full font-medium">高风险</span>
              <span class="px-3 py-1 bg-warning/10 text-warning text-sm rounded-full font-medium">待处理</span>
            </div>
            <p class="text-light-dark mb-4">事件ID: <span class="font-medium">EVT-20230615-001</span> | 检测时间: <span class="font-medium">2023-06-15 10:24:35</span></p>
            
            <div class="flex flex-wrap gap-3">
              <button class="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-smooth text-sm">
                <i class="fas fa-edit mr-2"></i>编辑事件
              </button>
              <button class="inline-flex items-center px-4 py-2 bg-success text-white rounded-lg hover:bg-success/90 transition-smooth text-sm">
                <i class="fas fa-check mr-2"></i>标记为已处理
              </button>
              <button class="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm">
                <i class="fas fa-history mr-2"></i>查看历史
              </button>
              <button class="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm">
                <i class="fas fa-download mr-2"></i>导出报告
              </button>
            </div>
          </div>
          
          <!-- 事件关键指标 -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4 w-full md:w-auto">
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">风险评分</div>
              <div class="text-2xl font-semibold text-danger mt-1">92<span class="text-sm font-normal text-light-dark ml-1">/100</span></div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">关联账户</div>
              <div class="text-2xl font-semibold mt-1">3</div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">关联设备</div>
              <div class="text-2xl font-semibold mt-1">2</div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">影响范围</div>
              <div class="text-2xl font-semibold mt-1">中</div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">处理优先级</div>
              <div class="text-2xl font-semibold text-danger mt-1">高</div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">持续时间</div>
              <div class="text-2xl font-semibold mt-1">2h 15m</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 溯源路径分析 -->
      <section class="mb-8">
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">事件溯源路径</h3>
            <p class="text-sm text-light-dark mt-1">风险事件的完整发展路径和时间线</p>
          </div>
          
          <div class="p-6">
            <!-- 详细时间线 -->
            <h4 class="font-medium text-lg mb-4">事件时间线</h4>
            <div class="relative">
              <!-- 时间线垂直线 -->
              <div class="timeline-line"></div>
              
              <!-- 时间线节点 -->
              <div 
                v-for="(event, index) in timelineEvents" 
                :key="event.id"
                class="relative pl-10"
                :class="index !== timelineEvents.length - 1 ? 'pb-8' : ''"
              >
                <div 
                  class="absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center z-10"
                  :class="event.iconBgClass"
                >
                  <i :class="event.icon" class="text-white text-xs"></i>
                </div>
                <div class="font-medium">{{ event.title }}</div>
                <div class="text-sm text-light-dark mt-1">{{ event.description }}</div>
                <div class="text-xs text-light-dark mt-2">{{ event.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 关联数据分析 -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <!-- 关联账户 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden lg:col-span-1">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">关联账户信息</h3>
            <p class="text-sm text-light-dark mt-1">与该风险事件相关的账户</p>
          </div>
          
          <div class="p-6">
            <div 
              v-for="(account, index) in relatedAccounts" 
              :key="account.id"
              :class="index !== relatedAccounts.length - 1 ? 'mb-6 pb-6 border-b border-gray-100' : ''"
            >
              <div class="flex items-start">
                <img :src="account.avatar" alt="用户头像" class="w-12 h-12 rounded-full object-cover mr-4">
                <div>
                  <div class="flex items-center">
                    <h4 class="font-medium">{{ account.name }}</h4>
                    <span 
                      class="ml-2 px-2 py-0.5 text-xs rounded-full"
                      :class="account.tagClass"
                    >
                      {{ account.tag }}
                    </span>
                  </div>
                  <p class="text-sm text-light-dark mt-1">{{ account.userId }}</p>
                  <div class="grid grid-cols-2 gap-2 mt-3 text-sm">
                    <div v-for="info in account.info" :key="info.label">
                      <span class="text-light-dark">{{ info.label }}:</span>
                      <span class="block" :class="info.class">{{ info.value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <button class="w-full mt-6 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm">
              查看所有关联账户 <i class="fas fa-angle-right ml-1"></i>
            </button>
          </div>
        </div>
        
        <!-- 关联设备和IP -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden lg:col-span-1">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">设备与网络信息</h3>
            <p class="text-sm text-light-dark mt-1">相关设备和网络连接信息</p>
          </div>
          
          <div class="p-6">
            <!-- 常用设备 -->
            <div class="mb-6 pb-6 border-b border-gray-100">
              <h4 class="font-medium mb-3 flex items-center">
                <i class="fas fa-mobile-alt text-success mr-2"></i>常用设备
              </h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div v-for="info in normalDevice" :key="info.label" class="flex justify-between mb-2 last:mb-0">
                  <span class="text-sm text-light-dark">{{ info.label }}</span>
                  <span class="text-sm">{{ info.value }}</span>
                </div>
              </div>
            </div>
            
            <!-- 异常设备 -->
            <div class="mb-6 pb-6 border-b border-gray-100">
              <h4 class="font-medium mb-3 flex items-center">
                <i class="fas fa-desktop text-danger mr-2"></i>异常设备
              </h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div v-for="info in abnormalDevice" :key="info.label" class="flex justify-between mb-2 last:mb-0">
                  <span class="text-sm text-light-dark">{{ info.label }}</span>
                  <span class="text-sm">{{ info.value }}</span>
                </div>
              </div>
            </div>
            
            <!-- IP地址分析 -->
            <div>
              <h4 class="font-medium mb-3 flex items-center">
                <i class="fas fa-globe text-info mr-2"></i>IP地址分析
              </h4>
              <div class="space-y-4">
                <div v-for="ip in ipAnalysis" :key="ip.address">
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-light-dark">{{ ip.address }}</span>
                    <span :class="ip.riskClass">{{ ip.riskLevel }}</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full"
                      :class="ip.barClass"
                      :style="{ width: ip.riskPercent + '%' }"
                    ></div>
                  </div>
                  <div class="text-xs text-light-dark mt-1">
                    {{ ip.history }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 交易记录 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden lg:col-span-1">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">关联交易记录</h3>
            <p class="text-sm text-light-dark mt-1">相关账户的交易流水</p>
          </div>
          
          <div class="p-6">
            <div class="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              <div 
                v-for="transaction in transactions" 
                :key="transaction.id"
                class="p-4 rounded-lg border"
                :class="transaction.isAbnormal ? 'border-danger/20 bg-danger/5' : 'border-gray-200'"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <div class="font-medium">{{ transaction.type }}</div>
                    <div class="text-sm text-light-dark mt-1">{{ transaction.description }}</div>
                  </div>
                  <span 
                    class="font-medium"
                    :class="transaction.amount.startsWith('+') ? 'text-success' : 'text-danger'"
                  >
                    {{ transaction.amount }}
                  </span>
                </div>
                <div class="flex flex-wrap justify-between gap-2 mt-3 text-xs text-light-dark">
                  <span>交易ID: {{ transaction.id }}</span>
                  <span>状态: <span :class="transaction.statusClass">{{ transaction.status }}</span></span>
                  <span>时间: {{ transaction.time }}</span>
                </div>
                <div 
                  v-if="transaction.warning"
                  class="mt-2 text-xs bg-danger/10 text-danger px-2 py-1 rounded inline-block"
                >
                  {{ transaction.warning }}
                </div>
              </div>
            </div>
            
            <button class="w-full mt-6 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm">
              查看完整交易记录 <i class="fas fa-angle-right ml-1"></i>
            </button>
          </div>
        </div>
      </section>
      
      <!-- 责任追溯和风险分析 -->
      <section class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <!-- 责任追溯 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden lg:col-span-2">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">责任追溯</h3>
            <p class="text-sm text-light-dark mt-1">事件相关责任主体和影响范围</p>
          </div>
          
          <div class="p-6">
            <div class="mt-6">
              <h4 class="font-medium mb-3">责任分析</h4>
              <div class="space-y-3 text-sm">
                <div 
                  v-for="item in responsibilityAnalysis" 
                  :key="item.title"
                  class="flex items-start"
                >
                  <div 
                    class="p-1 rounded-full mt-0.5 mr-3"
                    :class="item.iconBgClass"
                  >
                    <i :class="item.icon"></i>
                  </div>
                  <div>
                    <div class="font-medium">{{ item.title }}</div>
                    <div class="text-light-dark mt-1">{{ item.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 风险分析和建议 -->
        <div class="bg-white rounded-xl card-shadow overflow-hidden lg:col-span-3">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold">风险分析与处理建议</h3>
            <p class="text-sm text-light-dark mt-1">基于事件分析的风险评估和处理方案</p>
          </div>
          
          <div class="p-6">
            <div class="mb-6">
              <h4 class="font-medium mb-3">风险评估</h4>
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p class="text-sm mb-4">该事件属于典型的账户盗用案例，攻击者通过未知手段获取了用户的基本信息，并成功重置密码登录账户。从攻击路径来看，攻击者可能利用了用户在其他平台的信息泄露，使用相同的用户名和密码尝试登录。事件风险等级高，已造成潜在的资金损失风险。</p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div v-for="risk in riskAssessment" :key="risk.label">
                    <div class="text-light-dark text-xs mb-1">{{ risk.label }}</div>
                    <div class="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div 
                        class="h-2 rounded-full"
                        :class="risk.barClass"
                        :style="{ width: risk.percent + '%' }"
                      ></div>
                    </div>
                    <div class="text-xs" :class="risk.textClass">{{ risk.level }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mb-6">
              <h4 class="font-medium mb-3">处理建议</h4>
              <div class="space-y-3">
                <div 
                  v-for="(suggestion, index) in suggestions" 
                  :key="index"
                  class="flex items-start"
                >
                  <div class="bg-primary/10 text-primary p-1 rounded-full mt-0.5 mr-3 flex-shrink-0">
                    <span class="text-sm font-medium">{{ index + 1 }}</span>
                  </div>
                  <div>
                    <div class="font-medium">{{ suggestion.title }}</div>
                    <div class="text-sm text-light-dark mt-1">{{ suggestion.description }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 class="font-medium mb-3">处理记录</h4>
              <div class="space-y-4 max-h-[150px] overflow-y-auto pr-2">
                <div 
                  v-for="record in processingRecords" 
                  :key="record.id"
                  class="flex items-start"
                >
                  <img :src="record.avatar" alt="处理人头像" class="w-8 h-8 rounded-full object-cover mr-3 flex-shrink-0">
                  <div>
                    <div class="flex items-center">
                      <span class="font-medium text-sm">{{ record.handler }}</span>
                      <span class="ml-2 text-xs text-light-dark">{{ record.time }}</span>
                    </div>
                    <p class="text-sm text-light-dark mt-1">{{ record.content }}</p>
                  </div>
                </div>
              </div>
              
              <div class="mt-4">
                <textarea 
                  v-model="newProcessingNote"
                  rows="2" 
                  class="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth resize-none text-sm" 
                  placeholder="添加处理记录..."
                ></textarea>
                <div class="flex justify-end mt-2">
                  <button 
                    @click="saveProcessingNote"
                    class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-smooth text-sm"
                  >
                    保存记录
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')
const newProcessingNote = ref('')

let refreshTimer: number | null = null

const timelineEvents = ref([
  { id: 1, title: '正常登录', description: '用户在常用设备（iPhone 13）上登录账户，地点：上海', time: '2023-06-14 20:15:32', icon: 'fas fa-user', iconBgClass: 'bg-primary' },
  { id: 2, title: '用户登出', description: '用户主动登出账户', time: '2023-06-14 22:30:15', icon: 'fas fa-sign-out-alt', iconBgClass: 'bg-gray-400' },
  { id: 3, title: '异常登录尝试', description: '新设备（Windows 10）尝试登录，IP地址：185.173.89.xxx，地点：俄罗斯莫斯科', time: '2023-06-15 10:20:18', icon: 'fas fa-user-secret', iconBgClass: 'bg-warning' },
  { id: 4, title: '密码重置请求', description: '来自同一IP地址的密码重置请求，通过短信验证码验证', time: '2023-06-15 10:22:47', icon: 'fas fa-key', iconBgClass: 'bg-warning' },
  { id: 5, title: '异常登录成功', description: '使用新密码在新设备上登录成功', time: '2023-06-15 10:24:12', icon: 'fas fa-check-circle', iconBgClass: 'bg-danger' },
  { id: 6, title: '风险事件触发', description: '系统检测到异地异常登录行为，触发高风险告警', time: '2023-06-15 10:24:35', icon: 'fas fa-exclamation-triangle', iconBgClass: 'bg-danger' },
  { id: 7, title: '异常资金转移', description: '登录后尝试向陌生账户转移资金 50,000元', time: '2023-06-15 10:30:22', icon: 'fas fa-exchange-alt', iconBgClass: 'bg-danger' }
])

const relatedAccounts = ref([
  {
    id: 1,
    name: '王小明',
    avatar: 'https://picsum.photos/id/1012/200/200',
    tag: '受害者',
    tagClass: 'bg-primary/10 text-primary',
    userId: 'USER-789456',
    info: [
      { label: '注册时间', value: '2022-03-15' },
      { label: '账户等级', value: 'VIP会员' },
      { label: '联系电话', value: '138****5678' },
      { label: '邮箱', value: 'wang***@example.com' }
    ]
  },
  {
    id: 2,
    name: '李**',
    avatar: 'https://picsum.photos/id/1025/200/200',
    tag: '收款账户',
    tagClass: 'bg-danger/10 text-danger',
    userId: 'USER-123456',
    info: [
      { label: '注册时间', value: '2023-05-20' },
      { label: '账户状态', value: '已冻结', class: 'text-warning' },
      { label: '交易次数', value: '12次' },
      { label: '风险评分', value: '85分', class: 'text-danger' }
    ]
  },
  {
    id: 3,
    name: '张**',
    avatar: 'https://picsum.photos/id/1074/200/200',
    tag: '可疑关联',
    tagClass: 'bg-warning/10 text-warning',
    userId: 'USER-654321',
    info: [
      { label: '注册时间', value: '2023-01-05' },
      { label: '账户状态', value: '正常' },
      { label: '与受害者关系', value: '无明显关系' },
      { label: '风险评分', value: '62分', class: 'text-warning' }
    ]
  }
])

const normalDevice = ref([
  { label: '设备名称', value: 'iPhone 13' },
  { label: '操作系统', value: 'iOS 16.5' },
  { label: '浏览器', value: 'Safari 16.5' },
  { label: '常用IP', value: '101.89.xxx.xxx' },
  { label: '常用地点', value: '中国 上海' }
])

const abnormalDevice = ref([
  { label: '设备名称', value: '未知Windows设备' },
  { label: '操作系统', value: 'Windows 10' },
  { label: '浏览器', value: 'Chrome 112.0.5615.138' },
  { label: '登录IP', value: '185.173.89.xxx' },
  { label: '登录地点', value: '俄罗斯 莫斯科' }
])

const ipAnalysis = ref([
  { address: '185.173.89.xxx', riskLevel: '高风险', riskClass: 'text-danger', barClass: 'bg-danger', riskPercent: 92, history: '历史记录: 3次可疑登录 | 归属地: 俄罗斯 莫斯科' },
  { address: '101.89.xxx.xxx', riskLevel: '低风险', riskClass: 'text-success', barClass: 'bg-success', riskPercent: 15, history: '历史记录: 128次正常登录 | 归属地: 中国 上海' }
])

const transactions = ref([
  { id: 'TX2023061501234', type: '资金转出', description: '向账户 李** 转账', amount: '-¥50,000.00', status: '处理中', statusClass: 'text-warning', time: '2023-06-15 10:30:22', isAbnormal: true, warning: '可疑交易 - 已拦截' },
  { id: 'TX2023061008765', type: '资金转入', description: '来自账户 公司工资账户', amount: '+¥18,500.00', status: '成功', statusClass: 'text-success', time: '2023-06-10 09:30:00', isAbnormal: false },
  { id: 'TX2023060805432', type: '消费', description: '在线购物 - 电子产品', amount: '-¥3,299.00', status: '成功', statusClass: 'text-success', time: '2023-06-08 15:42:18', isAbnormal: false },
  { id: 'TX2023060509876', type: '资金转出', description: '向账户 王** 转账（亲属）', amount: '-¥10,000.00', status: '成功', statusClass: 'text-success', time: '2023-06-05 11:20:55', isAbnormal: false }
])

const responsibilityAnalysis = ref([
  { title: '主要责任主体', description: '疑似黑客攻击，通过非法手段获取用户信息并进行登录操作', icon: 'fas fa-user', iconBgClass: 'bg-danger/10 text-danger' },
  { title: '用户责任', description: '可能在其他平台使用相同密码，导致信息泄露；未开启二次验证', icon: 'fas fa-user-circle', iconBgClass: 'bg-warning/10 text-warning' },
  { title: '系统防护', description: '异地登录检测及时，但密码重置流程可进一步加强安全验证', icon: 'fas fa-shield-alt', iconBgClass: 'bg-info/10 text-info' }
])

const riskAssessment = ref([
  { label: '账户安全风险', percent: 95, level: '极高', barClass: 'bg-danger', textClass: 'text-danger' },
  { label: '资金损失风险', percent: 85, level: '高', barClass: 'bg-danger', textClass: 'text-danger' },
  { label: '信息泄露风险', percent: 65, level: '中', barClass: 'bg-warning', textClass: 'text-warning' }
])

const suggestions = ref([
  { title: '立即冻结账户', description: '暂时冻结账户所有操作权限，防止进一步损失' },
  { title: '联系用户核实', description: '通过注册手机和邮箱联系用户，确认是否为本人操作' },
  { title: '强制密码重置', description: '引导用户进行安全的密码重置，并建议开启二次验证' },
  { title: '调查收款账户', description: '对李**账户进行风险评估，必要时冻结并上报可疑交易' },
  { title: '加强异常检测', description: '针对此类攻击模式优化风控模型，加强密码重置环节的安全验证' }
])

const processingRecords = ref([
  { id: 1, handler: '系统自动处理', avatar: 'https://picsum.photos/id/1005/200/200', time: '2023-06-15 10:25:10', content: '检测到高风险事件，已自动拦截资金转移操作' },
  { id: 2, handler: '张经理', avatar: 'https://picsum.photos/id/1010/200/200', time: '2023-06-15 10:35:42', content: '已冻结用户账户和可疑收款账户，正在联系用户核实情况' }
])

const saveProcessingNote = () => {
  if (newProcessingNote.value.trim()) {
    processingRecords.value.push({
      id: processingRecords.value.length + 1,
      handler: '当前用户',
      avatar: 'https://picsum.photos/id/1005/200/200',
      time: new Date().toLocaleString('zh-CN'),
      content: newProcessingNote.value
    })
    newProcessingNote.value = ''
    showToast('处理记录已保存')
  }
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

onMounted(() => {
  // 设置自动刷新
  refreshTimer = window.setInterval(() => {
    showToast('数据已更新')
  }, 30000)
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

