<template>
  <div class="font-inter bg-gray-50 text-dark min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- 加载状态 -->
      <div v-if="loadingDetail" class="p-12 text-center">
        <svg class="w-8 h-8 mx-auto animate-spin text-primary" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-light-dark">加载事件详情中...</p>
      </div>
      
      <!-- 空状态：只有在没有事件ID时才提示从列表进入 -->
      <div v-else-if="!eventId" class="p-12 text-center">
        <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p class="mt-4 text-light-dark">请从风险告警页面选择事件查看详情</p>
      </div>
      
      <!-- 事件详情内容 -->
      <template v-else>
      <!-- 返回按钮和事件标题、基本信息 -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <button
            @click="$router.push('/risk-warning')"
            class="inline-flex items-center px-3 py-2 border border-gray-200 rounded-lg text-sm text-light-dark hover:bg-gray-50 transition-smooth"
          >
            <i class="fas fa-arrow-left mr-2"></i>返回风险告警列表
          </button>
        </div>
        <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
          <div>
            <div class="flex flex-wrap items-center gap-3 mb-2">
              <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-dark">
                {{ eventDetail?.title || '事件分析' }}
              </h2>
              <span 
                v-if="eventDetail?.levelName"
                class="px-3 py-1 text-sm rounded-full font-medium"
                :class="getLevelClass(eventDetail.level)"
              >
                {{ eventDetail.levelName }}
              </span>
              <span 
                v-if="eventDetail?.statusName"
                class="px-3 py-1 text-sm rounded-full font-medium"
                :class="getStatusClass(eventDetail.status)"
              >
                {{ eventDetail.statusName }}
              </span>
            </div>
            <p class="text-light-dark mb-4">
              事件ID: <span class="font-medium">{{ eventDetail?.id || eventId || '-' }}</span> | 
              检测时间: <span class="font-medium">{{ eventDetail?.detectTime || '-' }}</span>
            </p>
            
            <div class="flex flex-wrap gap-3">
              <button
                class="inline-flex items-center px-4 py-2 bg-success text-white rounded-lg hover:bg-success/90 transition-smooth text-sm"
                @click="markEventResolved"
              >
                <i class="fas fa-check mr-2"></i>标记为已处理
              </button>
              <button
                class="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm"
                @click="handleExportReport"
              >
                <i class="fas fa-download mr-2"></i>导出报告
              </button>
            </div>
          </div>
          
          <!-- 事件关键指标 -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4 w-full md:w-auto">
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">风险评分</div>
              <div 
                class="text-2xl font-semibold mt-1"
                :class="getRiskScoreClass(eventDetail?.riskScore)"
              >
                {{ eventDetail?.riskScore || '-' }}<span v-if="eventDetail?.riskScore" class="text-sm font-normal text-light-dark ml-1">/100</span>
              </div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">关联账户</div>
              <div class="text-2xl font-semibold mt-1">{{ eventDetail?.relatedAccounts ?? '-' }}</div>
            </div>
            <div class="bg-white rounded-lg p-4 card-shadow">
              <div class="text-light-dark text-sm">关联设备</div>
              <div class="text-2xl font-semibold mt-1">{{ eventDetail?.relatedDevices ?? '-' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 千帆模型辅助判断 -->
      <section class="mb-8">
        <div class="bg-white rounded-xl card-shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold">千帆模型辅助判断</h3>
              <p class="text-sm text-light-dark mt-1">输入事件描述，调用千帆 AppBuilder 获取风险判断结果</p>
            </div>
            <div class="text-sm">
              <span class="text-light-dark mr-2">服务状态</span>
              <span class="px-3 py-1 rounded-full text-xs font-medium" :class="qianfanServiceStatusClass">
                {{ qianfanServiceStatusText }}
              </span>
            </div>
          </div>

          <div class="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm text-light-dark mb-2">案件描述</label>
              <textarea
                v-model="qianfanQuery"
                rows="6"
                class="w-full border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth resize-y text-sm"
                placeholder="例如：用户在异地非常用设备登录后，尝试转出大额资金，请判断风险等级并给出处理建议。"
              ></textarea>

              <label class="block text-sm text-light-dark mt-4 mb-2">用户ID（可选）</label>
              <input
                v-model="qianfanUserId"
                type="text"
                class="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth text-sm"
                placeholder="如：USER-789456"
              />

              <p v-if="qianfanServiceMessage" class="text-xs text-light-dark mt-3">
                模型提示：{{ qianfanServiceMessage }}
              </p>
              <p v-if="qianfanError" class="text-sm text-danger mt-2">
                {{ qianfanError }}
              </p>

              <div class="flex flex-wrap gap-3 mt-4">
                <button
                  @click="submitQianfanJudge"
                  :disabled="qianfanLoading"
                  class="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-smooth text-sm"
                >
                  <i class="fas fa-robot mr-2"></i>{{ qianfanLoading ? '判断中...' : '调用千帆判断' }}
                </button>
                <button
                  @click="resetQianfanJudge"
                  class="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm"
                >
                  重置输入
                </button>
              </div>
            </div>

            <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <h4 class="font-medium mb-3">模型返回</h4>
              <div v-if="qianfanResult" class="space-y-3">
                <div class="flex flex-wrap items-center gap-3 text-sm">
                  <span
                    class="px-2.5 py-1 rounded-full font-medium"
                    :class="qianfanResult.available ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
                  >
                    {{ qianfanResult.available ? '可用' : '不可用' }}
                  </span>
                  <span>
                    风险级别：
                    <span class="font-semibold" :class="qianfanRiskLevelClass">
                      {{ qianfanResult.inferred_level || '未知' }}
                    </span>
                  </span>
                  <span class="text-light-dark">重试次数：{{ qianfanResult.attempts ?? '-' }}</span>
                </div>

                <p v-if="qianfanResult.message" class="text-sm text-light-dark">
                  {{ qianfanResult.message }}
                </p>
                <p class="text-sm leading-6 whitespace-pre-wrap">
                  {{ qianfanResult.answer || '暂无模型文本输出' }}
                </p>
                <a
                  v-if="qianfanResult.share_url"
                  :href="qianfanResult.share_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center text-sm text-primary hover:text-primary/80"
                >
                  打开千帆应用链接 <i class="fas fa-external-link-alt ml-1 text-xs"></i>
                </a>
              </div>
              <div v-else class="text-sm text-light-dark">
                暂未调用模型。输入案件描述后点击“调用千帆判断”查看结果。
              </div>
            </div>
          </div>
        </div>
      </section>
      
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
                  <i :class="event.iconClass" class="text-white text-xs"></i>
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
            
            <button 
              class="w-full mt-6 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm"
              @click="showAccountsModal = true"
            >
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
            
            <button 
              class="w-full mt-6 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth text-sm"
              @click="openTransactionsModal"
            >
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
            <h3 class="text-lg font-semibold">风险分析</h3>
            <p class="text-sm text-light-dark mt-1">基于事件分析的风险评估</p>
          </div>
          
          <div class="p-6">
            <div class="mb-6">
              <h4 class="font-medium mb-3">风险评估</h4>
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p v-if="riskAssessmentText" class="text-sm mb-4 text-gray-700">{{ riskAssessmentText }}</p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            
            <div>
              <h4 class="font-medium mb-3">处理记录</h4>
              <div class="space-y-4 max-h-[150px] overflow-y-auto pr-2">
                <div 
                  v-for="record in processingRecords" 
                  :key="record.id"
                  class="flex items-start"
                >
                  <img :src="getRecordAvatar(record)" alt="处理人头像" class="w-8 h-8 rounded-full object-cover mr-3 flex-shrink-0">
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
      </template>
    </main>

    <AppFooter />

    <!-- 所有关联账户弹窗 -->
    <div 
      v-if="showAccountsModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="showAccountsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-semibold">所有关联账户</h3>
          <button 
            class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center"
            @click="showAccountsModal = false"
          >
            <i class="fas fa-times text-gray-500"></i>
          </button>
        </div>
        <div class="p-6 overflow-y-auto flex-1">
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
          <p v-if="relatedAccounts.length === 0" class="text-center text-light-dark py-8">暂无关联账户</p>
        </div>
      </div>
    </div>

    <!-- 完整交易记录弹窗（分页） -->
    <div 
      v-if="showTransactionsModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="showTransactionsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-semibold">完整交易记录</h3>
          <button 
            class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center"
            @click="showTransactionsModal = false"
          >
            <i class="fas fa-times text-gray-500"></i>
          </button>
        </div>
        <div class="p-6 overflow-y-auto flex-1">
          <div v-if="transactionsModalLoading" class="py-12 text-center text-light-dark">
            <i class="fas fa-spinner fa-spin text-2xl"></i>
            <p class="mt-2">加载中...</p>
          </div>
          <template v-else>
            <div class="space-y-4">
              <div 
                v-for="tx in transactionsFullList" 
                :key="tx.id"
                class="p-4 rounded-lg border"
                :class="tx.isAbnormal ? 'border-danger/20 bg-danger/5' : 'border-gray-200'"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <div class="font-medium">{{ tx.type }}</div>
                    <div class="text-sm text-light-dark mt-1">{{ tx.description }}</div>
                  </div>
                  <span 
                    class="font-medium"
                    :class="tx.amount.startsWith('+') ? 'text-success' : 'text-danger'"
                  >
                    {{ tx.amount }}
                  </span>
                </div>
                <div class="flex flex-wrap justify-between gap-2 mt-3 text-xs text-light-dark">
                  <span>交易ID: {{ tx.id }}</span>
                  <span>状态: <span :class="tx.statusClass">{{ tx.status }}</span></span>
                  <span>时间: {{ tx.time }}</span>
                </div>
                <div 
                  v-if="tx.warning"
                  class="mt-2 text-xs bg-danger/10 text-danger px-2 py-1 rounded inline-block"
                >
                  {{ tx.warning }}
                </div>
              </div>
            </div>
            <p v-if="transactionsFullList.length === 0 && !transactionsModalLoading" class="text-center text-light-dark py-8">暂无交易记录</p>
            <div 
              v-if="transactionsFullTotal > 0" 
              class="mt-6 flex items-center justify-between border-t border-gray-200 pt-4"
            >
              <span class="text-sm text-light-dark">共 {{ transactionsFullTotal }} 条</span>
              <div class="flex gap-2">
                <button 
                  class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
                  :disabled="transactionsFullPage <= 1"
                  @click="fetchTransactionsPage(transactionsFullPage - 1)"
                >
                  上一页
                </button>
                <span class="px-3 py-1.5 text-sm text-light-dark">{{ transactionsFullPage }} / {{ transactionsFullTotalPages }}</span>
                <button 
                  class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
                  :disabled="transactionsFullPage >= transactionsFullTotalPages"
                  @click="fetchTransactionsPage(transactionsFullPage + 1)"
                >
                  下一页
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import Toast from '@/components/Toast.vue'
import { getModelStatus, qianfanRiskJudge } from '@/api/model'
import type { QianfanRiskJudgeResult } from '@/api/model'
import { getUserProfile } from '@/api/user'
import {
  getEventAnalysisDetail,
  getEventTimeline,
  getEventRelatedAccounts,
  getEventDevicesIps,
  getEventTransactions,
  getEventResponsibility,
  getEventRiskAnalysis,
  getEventProcessingRecords,
  addEventProcessingRecord,
  updateEventStatus,
  exportEventReport
} from '@/api/eventAnalysis'
import type {
  EventAnalysisDetail,
  EventTimelineItem,
  EventRelatedAccount,
  EventIpAnalysisItem,
  EventTransaction,
  EventResponsibilityAnalysisItem,
  EventRiskAnalysisData,
  EventProcessingRecord
} from '@/api/types'

const route = useRoute()

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')
const newProcessingNote = ref('')
// 当前登录用户显示名与头像，用于添加处理记录时作为处理人
const currentUserDisplayName = ref('当前用户')
const currentUserAvatar = ref('')

let refreshTimer: number | null = null

// 事件 ID（从路由 query 中获取，优先使用 eventId，其次兼容 alertId）
const eventId = computed(() => {
  return (route.query.eventId as string | undefined) || (route.query.alertId as string | undefined)
})

// 事件详情数据
const eventDetail = ref<EventAnalysisDetail | null>(null)
const loadingDetail = ref(false)

type QianfanServiceStatus = 'loading' | 'normal' | 'abnormal' | 'not_configured' | 'unknown'

const qianfanQuery = ref(
  '用户账户在非常用设备异地登录并尝试转账50000元，请判断风险等级并给出处理建议。'
)
const qianfanUserId = ref('USER-789456')
const qianfanLoading = ref(false)
const qianfanError = ref('')
const qianfanResult = ref<QianfanRiskJudgeResult | null>(null)
const qianfanServiceStatus = ref<QianfanServiceStatus>('loading')
const qianfanServiceMessage = ref('')

const qianfanServiceStatusText = computed(() => {
  switch (qianfanServiceStatus.value) {
    case 'normal':
      return '正常'
    case 'not_configured':
      return '未配置'
    case 'abnormal':
      return '异常'
    case 'loading':
      return '检测中'
    default:
      return '未知'
  }
})

const qianfanServiceStatusClass = computed(() => {
  switch (qianfanServiceStatus.value) {
    case 'normal':
      return 'bg-success/10 text-success'
    case 'not_configured':
      return 'bg-warning/10 text-warning'
    case 'abnormal':
      return 'bg-danger/10 text-danger'
    case 'loading':
      return 'bg-gray-100 text-light-dark'
    default:
      return 'bg-gray-100 text-light-dark'
  }
})

const qianfanRiskLevelClass = computed(() => {
  switch (qianfanResult.value?.inferred_level) {
    case '高':
      return 'text-danger'
    case '中':
      return 'text-warning'
    case '低':
      return 'text-success'
    default:
      return 'text-light-dark'
  }
})

// 接口数据：时间线
const timelineEvents = ref<
  Array<
    EventTimelineItem & {
      iconClass: string
      iconBgClass: string
      title: string
    }
  >
>([])

// 接口数据：关联账户
const relatedAccounts = ref<
  Array<{
    id: string
    name: string
    avatar: string
    tag: string
    tagClass: string
    userId: string
    info: Array<{ label: string; value: string; class?: string }>
  }>
>([])

// 接口数据：设备和 IP
const normalDevice = ref<Array<{ label: string; value: string }>>([])
const abnormalDevice = ref<Array<{ label: string; value: string }>>([])
const ipAnalysis = ref<
  Array<{
    address: string
    riskLevel: string
    riskClass: string
    barClass: string
    riskPercent: number
    history: string
  }>
>([])

// 接口数据：交易记录
const transactions = ref<
  Array<{
    id: string
    type: string
    description: string
    amount: string
    status: string
    statusClass: string
    time: string
    isAbnormal: boolean
    warning?: string
  }>
>([])

// 接口数据：责任追溯
const responsibilityAnalysis = ref<
  Array<{
    title: string
    description: string
    icon: string
    iconBgClass: string
  }>
>([])

// 接口数据：风险评估和处理建议
const riskAssessment = ref<
  Array<{
    label: string
    percent: number
    level: string
    barClass: string
    textClass: string
  }>
>([])
// 接口返回的风险评估文案（7.8 risk-analysis）
const riskAssessmentText = ref('')

// 接口数据：处理记录
const processingRecords = ref<
  Array<{
    id: number
    handler: string
    avatar: string
    time: string
    content: string
  }>
>([])

// 弹窗：所有关联账户 / 完整交易记录
const showAccountsModal = ref(false)
const showTransactionsModal = ref(false)
const transactionsFullList = ref<
  Array<{
    id: string
    type: string
    description: string
    amount: string
    status: string
    statusClass: string
    time: string
    isAbnormal: boolean
    warning?: string
  }>
>([])
const transactionsFullTotal = ref(0)
const transactionsFullPage = ref(1)
const transactionsFullPageSize = 10
const transactionsFullTotalPages = computed(() =>
  Math.max(1, Math.ceil(transactionsFullTotal.value / transactionsFullPageSize))
)
const transactionsModalLoading = ref(false)

const saveProcessingNote = async () => {
  const note = newProcessingNote.value.trim()
  if (!note) return
  if (!eventId.value) {
    showToast('缺少事件ID，无法保存处理记录', 'warning')
    return
  }

  try {
    const { data: res } = await addEventProcessingRecord(eventId.value, {
      note,
      operator: currentUserDisplayName.value
    })
    if (res.code === 200 && res.data) {
      const r = res.data
      processingRecords.value.unshift({
        id: r.id,
        handler: r.handlerName || r.handler || '当前用户',
        avatar: r.handlerAvatar || currentUserAvatar.value,
        time: r.time,
        content: r.note
      })
      newProcessingNote.value = ''
      showToast('处理记录已保存')
    }
  } catch (error) {
    console.error('保存处理记录失败:', error)
    showToast('保存处理记录失败', 'warning')
  }
}

// 标记事件为已处理（后端会同步更新该事件关联的所有告警状态）
const markEventResolved = async () => {
  if (!eventId.value) {
    showToast('缺少事件ID，无法更新状态', 'warning')
    return
  }
  try {
    const { data: res } = await updateEventStatus(eventId.value, 'resolved')
    if (res.code === 200) {
      if (eventDetail.value) {
        eventDetail.value.status = 'resolved'
        eventDetail.value.statusName = '已解决'
      }
      const n = (res.data as { syncedAlerts?: number } | null)?.syncedAlerts
      const msg = n != null && n > 0
        ? `事件与 ${n} 条关联告警已标记为已解决，可刷新告警列表查看`
        : '事件已标记为已解决'
      showToast(msg)
    }
  } catch (error) {
    console.error('更新事件状态失败:', error)
    showToast('更新事件状态失败', 'warning')
  }
}

// 导出事件报告（触发浏览器下载到本地）
const handleExportReport = async () => {
  if (!eventId.value) {
    showToast('缺少事件ID，无法导出报告', 'warning')
    return
  }
  try {
    const response = await exportEventReport(eventId.value)
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data], { type: 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `event_${eventId.value}_report.txt`
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    // 延迟释放，确保浏览器已开始下载
    setTimeout(() => {
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }, 200)
    showToast('报告已开始下载')
  } catch (error) {
    console.error('导出事件报告失败:', error)
    showToast('导出事件报告失败', 'warning')
  }
}

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

const resolveErrorMessage = (error: unknown) => {
  if (error instanceof Error && error.message) {
    return error.message
  }
  return '请求失败，请稍后重试'
}

const loadQianfanServiceStatus = async () => {
  qianfanServiceStatus.value = 'loading'
  qianfanServiceMessage.value = ''
  try {
    const response = await getModelStatus()
    const services = response.data.data?.services ?? []
    const serviceInfo = services.find((item) => item.service === 'qianfan_appbuilder')
    qianfanServiceStatus.value = (serviceInfo?.status as QianfanServiceStatus) || 'unknown'
    qianfanServiceMessage.value = serviceInfo?.message || ''
  } catch (error) {
    qianfanServiceStatus.value = 'abnormal'
    qianfanServiceMessage.value = resolveErrorMessage(error)
  }
}

const submitQianfanJudge = async () => {
  const query = qianfanQuery.value.trim()
  if (!query) {
    showToast('请先输入案件描述', 'warning')
    return
  }

  qianfanLoading.value = true
  qianfanError.value = ''

  try {
    const response = await qianfanRiskJudge({
      query,
      user_id: qianfanUserId.value.trim() || undefined
    })
    qianfanResult.value = response.data.data
    if (qianfanResult.value.available) {
      showToast('千帆判断完成')
    } else {
      qianfanError.value = qianfanResult.value.message || '千帆模型当前不可用'
      showToast('千帆模型当前不可用', 'warning')
    }
  } catch (error) {
    qianfanResult.value = null
    qianfanError.value = resolveErrorMessage(error)
    showToast('千帆调用失败', 'warning')
  } finally {
    qianfanLoading.value = false
  }
}

const resetQianfanJudge = () => {
  qianfanQuery.value = ''
  qianfanError.value = ''
  qianfanResult.value = null
}

// ==== 加载事件分析相关数据（7.x 接口） ====

// 7.1 事件详情
const fetchEventDetail = async (id: string) => {
  loadingDetail.value = true
  try {
    const { data: res } = await getEventAnalysisDetail(id)
    if (res.code === 200 && res.data) {
      eventDetail.value = res.data
    }
  } catch (error) {
    console.error('获取事件详情失败:', error)
    showToast('获取事件详情失败', 'warning')
  } finally {
    loadingDetail.value = false
  }
}

// 7.2 时间线
const fetchTimeline = async (id: string) => {
  try {
    const { data: res } = await getEventTimeline(id)
    if (res.code === 200 && res.data) {
      timelineEvents.value = (res.data.timeline || []).map((item: EventTimelineItem) => {
        let iconClass = 'fas fa-info-circle'
        let iconBgClass = 'bg-gray-400'
        switch (item.type) {
          case 'normal':
            iconBgClass = 'bg-primary'
            iconClass = 'fas fa-user'
            break
          case 'warning':
            iconBgClass = 'bg-warning'
            iconClass = 'fas fa-exclamation-triangle'
            break
          case 'danger':
            iconBgClass = 'bg-danger'
            iconClass = 'fas fa-exclamation-circle'
            break
          case 'info':
          default:
            iconBgClass = 'bg-gray-400'
            iconClass = 'fas fa-info-circle'
        }
        return {
          ...item,
          title: item.typeName,
          iconClass,
          iconBgClass
        }
      })
    }
  } catch (error) {
    console.error('获取事件时间线失败:', error)
  }
}

// 7.4 关联账户
const fetchRelatedAccounts = async (id: string) => {
  try {
    const { data: res } = await getEventRelatedAccounts(id)
    if (res.code === 200 && res.data) {
      relatedAccounts.value = (res.data.list || []).map((item: EventRelatedAccount, index: number) => {
        const tagClassMap: Record<string, string> = {
          victim: 'bg-primary/10 text-primary',
          suspicious: 'bg-warning/10 text-warning'
        }
        const tagName = item.roleName || '关联账户'
        const avatarId = 1005 + index
        return {
          id: item.id,
          name: item.name,
          avatar: `https://picsum.photos/id/${avatarId}/200/200`,
          tag: tagName,
          tagClass: tagClassMap[item.role] || 'bg-gray-100 text-light-dark',
          userId: item.id,
          info: [
            { label: '注册时间', value: item.registerTime },
            { label: '账户等级', value: item.level },
            { label: '联系电话', value: item.phone },
            { label: '邮箱', value: item.email }
          ]
        }
      })
    }
  } catch (error) {
    console.error('获取关联账户失败:', error)
  }
}

// 7.5 设备和 IP
const fetchDevicesAndIps = async (id: string) => {
  try {
    const { data: res } = await getEventDevicesIps(id)
    if (res.code === 200 && res.data) {
      const { commonDevices = [], abnormalDevices = [], ipAnalysis: ipList = [] } = res.data

      normalDevice.value = commonDevices.map((d) => ({
        label: d.name || '常用设备',
        value: `${d.os || ''} ${d.browser || ''}`.trim() || '-'
      }))

      abnormalDevice.value = abnormalDevices.map((d) => ({
        label: d.name || '异常设备',
        value: `${d.os || ''} ${d.browser || ''}`.trim() || '-'
      }))

      ipAnalysis.value = (ipList as EventIpAnalysisItem[]).map((ip) => {
        let riskClass = 'text-success'
        let barClass = 'bg-success'
        switch (ip.riskLevel) {
          case 'high':
            riskClass = 'text-danger'
            barClass = 'bg-danger'
            break
          case 'medium':
            riskClass = 'text-warning'
            barClass = 'bg-warning'
            break
          case 'low':
          default:
            riskClass = 'text-success'
            barClass = 'bg-success'
        }
        return {
          address: ip.ip,
          riskLevel: ip.riskLevel,
          riskClass,
          barClass,
          riskPercent: ip.riskScore,
          history: ip.description
        }
      })
    }
  } catch (error) {
    console.error('获取设备和 IP 信息失败:', error)
  }
}

// 7.6 交易记录
const fetchTransactions = async (id: string) => {
  try {
    const { data: res } = await getEventTransactions(id, { page: 1, pageSize: 10 })
    if (res.code === 200 && res.data) {
      transactions.value = (res.data.list || []).map((t: EventTransaction) => {
        const amountPrefix = t.amount >= 0 ? '+' : '-'
        const amountAbs = Math.abs(t.amount).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })
        const amountStr = `${amountPrefix}¥${amountAbs}`

        let statusClass = 'text-light-dark'
        if (t.status === 'success') statusClass = 'text-success'
        else if (t.status === 'processing') statusClass = 'text-warning'

        return {
          id: t.id,
          type: t.typeName,
          description: `${t.fromAccountName} → ${t.toAccountName}`,
          amount: amountStr,
          status: t.statusName,
          statusClass,
          time: t.time,
          isAbnormal: t.isAbnormal,
          warning: t.isAbnormal ? t.abnormalReason : undefined
        }
      })
    }
  } catch (error) {
    console.error('获取交易记录失败:', error)
  }
}

// 完整交易记录弹窗：打开时加载第一页
const openTransactionsModal = () => {
  showTransactionsModal.value = true
  fetchTransactionsPage(1)
}

// 完整交易记录分页请求
const fetchTransactionsPage = async (page: number) => {
  const id = eventId.value
  if (!id) return
  transactionsModalLoading.value = true
  try {
    const { data: res } = await getEventTransactions(id, {
      page,
      pageSize: transactionsFullPageSize
    })
    if (res.code === 200 && res.data) {
      transactionsFullList.value = (res.data.list || []).map((t: EventTransaction) => {
        const amountPrefix = t.amount >= 0 ? '+' : '-'
        const amountAbs = Math.abs(t.amount).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })
        const amountStr = `${amountPrefix}¥${amountAbs}`
        let statusClass = 'text-light-dark'
        if (t.status === 'success') statusClass = 'text-success'
        else if (t.status === 'processing') statusClass = 'text-warning'
        return {
          id: t.id,
          type: t.typeName,
          description: `${t.fromAccountName} → ${t.toAccountName}`,
          amount: amountStr,
          status: t.statusName,
          statusClass,
          time: t.time,
          isAbnormal: t.isAbnormal,
          warning: t.isAbnormal ? t.abnormalReason : undefined
        }
      })
      transactionsFullTotal.value = res.data.total ?? 0
      transactionsFullPage.value = page
    }
  } catch (error) {
    console.error('获取完整交易记录失败:', error)
  } finally {
    transactionsModalLoading.value = false
  }
}

// 7.7 责任追溯
const fetchResponsibility = async (id: string) => {
  try {
    const { data: res } = await getEventResponsibility(id)
    if (res.code === 200 && res.data) {
      const analysis = res.data.analysis || []
      responsibilityAnalysis.value = (analysis as EventResponsibilityAnalysisItem[]).map((item) => {
        let icon = 'fas fa-user'
        let iconBgClass = 'bg-info/10 text-info'
        switch (item.type) {
          case 'attacker':
            icon = 'fas fa-user-secret'
            iconBgClass = 'bg-danger/10 text-danger'
            break
          case 'user':
            icon = 'fas fa-user-circle'
            iconBgClass = 'bg-warning/10 text-warning'
            break
          case 'system':
            icon = 'fas fa-shield-alt'
            iconBgClass = 'bg-info/10 text-info'
            break
          default:
            icon = 'fas fa-info-circle'
            iconBgClass = 'bg-gray-100 text-light-dark'
        }
        return {
          title: item.typeName,
          description: item.description,
          icon,
          iconBgClass
        }
      })
    }
  } catch (error) {
    console.error('获取责任追溯失败:', error)
  }
}

// 7.8 风险分析与建议
const fetchRiskAnalysis = async (id: string) => {
  riskAssessmentText.value = ''
  try {
    const { data: res } = await getEventRiskAnalysis(id)
    if (res.code === 200 && res.data) {
      const data: EventRiskAnalysisData = res.data
      riskAssessmentText.value = data.riskAssessment || ''
      // 风险评估文本填充到千帆默认查询
      if (data.riskAssessment) {
        qianfanQuery.value = data.riskAssessment
      }

      const scores = data.riskScores
      riskAssessment.value = [
        {
          label: '账户安全风险',
          percent: scores.accountSecurity,
          level: scores.accountSecurityLevel,
          barClass: 'bg-danger',
          textClass: 'text-danger'
        },
        {
          label: '资金损失风险',
          percent: scores.fundLoss,
          level: scores.fundLossLevel,
          barClass: 'bg-danger',
          textClass: 'text-danger'
        },
        {
          label: '信息泄露风险',
          percent: scores.infoLeak,
          level: scores.infoLeakLevel,
          barClass: 'bg-warning',
          textClass: 'text-warning'
        }
      ]
    }
  } catch (error) {
    console.error('获取风险分析失败:', error)
  }
}

// 7.9 处理记录
const fetchProcessingRecords = async (id: string) => {
  try {
    const { data: res } = await getEventProcessingRecords(id)
    if (res.code === 200 && res.data) {
      processingRecords.value = (res.data.list || []).map((r: EventProcessingRecord) => {
        const handlerName = r.handlerName || r.handler
        const avatar =
          r.handlerAvatar ||
          (handlerName === currentUserDisplayName.value ? currentUserAvatar.value : '')
        return {
          id: r.id,
          handler: handlerName,
          avatar,
          time: r.time,
          content: r.note
        }
      })
    }
  } catch (error) {
    console.error('获取处理记录失败:', error)
  }
}

// 工具函数
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
    case 'pending': return 'bg-warning/10 text-warning'
    case 'processing': return 'bg-primary/10 text-primary'
    case 'resolved': return 'bg-success/10 text-success'
    case 'ignored': return 'bg-gray-100 text-light-dark'
    default: return 'bg-gray-100 text-light-dark'
  }
}

const getRiskScoreClass = (score?: number) => {
  if (!score) return 'text-gray-400'
  if (score >= 80) return 'text-danger'
  if (score >= 50) return 'text-warning'
  return 'text-success'
}

/** 处理记录头像：优先使用接口返回或当前用户头像，否则用首字母生成（非随机） */
function getRecordAvatar(record: { avatar?: string; handler?: string }): string {
  if (record.avatar) return record.avatar
  const name = (record.handler || '').trim() || '?'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=e0e7eb&color=374151&size=64`
}

// 加载整个事件分析模块数据
const loadEventAnalysisAll = async (id: string) => {
  await Promise.all([
    fetchEventDetail(id),
    fetchTimeline(id),
    fetchRelatedAccounts(id),
    fetchDevicesAndIps(id),
    fetchTransactions(id),
    fetchResponsibility(id),
    fetchRiskAnalysis(id),
    fetchProcessingRecords(id)
  ])
}

// 只根据 eventId 加载，不监听 alertId，避免发出 alert 请求
watch(
  () => eventId.value,
  (id) => {
    if (id && typeof id === 'string') {
      void loadEventAnalysisAll(id)
    }
  },
  { immediate: true }
)

onMounted(() => {
  void loadQianfanServiceStatus()
  // 获取当前登录用户，用于处理记录显示为当前用户而非“系统”
  getUserProfile().then(({ data: res }) => {
    if (res.code === 200 && res.data) {
      currentUserDisplayName.value = res.data.name || res.data.username || '当前用户'
      const av = res.data.avatar
      currentUserAvatar.value = av
        ? (av.startsWith('http') ? av : `${import.meta.env.VITE_APP_API_BASE || 'http://localhost:5000'}${av}`)
        : ''
    }
  }).catch(() => {})
  // 数据由 watch(eventId) 统一加载，此处不再重复调用
  // 设置自动刷新（仅提示数据已更新，实际可按需重新拉取）
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

