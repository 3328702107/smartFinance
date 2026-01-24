<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
      <!-- 模态框头部 -->
      <div class="p-6 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-xl font-bold">数据质量问题 - {{ source?.name }}</h3>
        <button @click="$emit('close')" class="text-light-dark hover:text-dark transition-smooth">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>
      
      <!-- 模态框内容 -->
      <div class="flex-grow overflow-y-auto p-6">
        <div class="mb-6">
          <h4 class="text-lg font-semibold mb-3">问题统计</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">缺失值</div>
              <div class="text-xl font-semibold text-danger mt-1">8</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">格式错误</div>
              <div class="text-xl font-semibold text-danger mt-1">3</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">值异常</div>
              <div class="text-xl font-semibold text-warning mt-1">1</div>
            </div>
          </div>
        </div>
        
        <div>
          <h4 class="text-lg font-semibold mb-3">详细问题列表</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-light-dark uppercase tracking-wider">记录ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-light-dark uppercase tracking-wider">问题类型</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-light-dark uppercase tracking-wider">字段</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-light-dark uppercase tracking-wider">描述</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-light-dark uppercase tracking-wider">时间</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="issue in issuesList" :key="issue.id">
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.recordId }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">
                    <span 
                      class="px-2 py-0.5 text-xs rounded-full"
                      :class="issue.type === '缺失值' || issue.type === '格式错误' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'"
                    >
                      {{ issue.type }}
                    </span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.field }}</td>
                  <td class="px-4 py-3 text-sm">{{ issue.description }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.time }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="mt-4 text-sm text-light-dark text-center">
            显示前 4 条问题 | <a href="#" class="text-primary hover:underline">查看全部 {{ source?.qualityIssues }} 条</a>
          </div>
        </div>
      </div>
      
      <!-- 模态框底部 -->
      <div class="p-6 border-t border-gray-200 flex justify-end space-x-3">
        <button 
          @click="$emit('export')"
          class="px-4 py-2 border border-gray-200 rounded-lg text-light-dark hover:bg-gray-50 transition-smooth"
        >
          <i class="fas fa-download mr-2"></i>导出问题列表
        </button>
        <button 
          @click="$emit('close')"
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-smooth"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface DataSource {
  id: string
  name: string
  qualityIssues: number
}

defineProps<{
  source: DataSource | null
}>()

defineEmits<{
  close: []
  export: []
}>()

const issuesList = ref([
  { id: '1', recordId: 'REC-87654', type: '缺失值', field: '交易地点', description: '交易记录中缺少交易地点信息', time: '14:28:15' },
  { id: '2', recordId: 'REC-87651', type: '缺失值', field: '支付方式', description: '交易记录中缺少支付方式信息', time: '14:27:42' },
  { id: '3', recordId: 'REC-87645', type: '格式错误', field: '交易时间', description: '时间格式不符合ISO标准，应为YYYY-MM-DD HH:MM:SS', time: '14:26:18' },
  { id: '4', recordId: 'REC-87632', type: '值异常', field: '交易金额', description: '交易金额为负数，不符合业务规则', time: '14:25:03' }
])
</script>

