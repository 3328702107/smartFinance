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
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">缺失值</div>
              <div class="text-xl font-semibold text-danger mt-1">{{ statistics.missing }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">格式错误</div>
              <div class="text-xl font-semibold text-danger mt-1">{{ statistics.formatError }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">值异常</div>
              <div class="text-xl font-semibold text-warning mt-1">{{ statistics.abnormal }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-light-dark text-sm">数据不一致</div>
              <div class="text-xl font-semibold text-warning mt-1">{{ statistics.inconsistent || 0 }}</div>
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
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.id }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">
                    <span 
                      class="px-2 py-0.5 text-xs rounded-full"
                      :class="issue.type === 'missing' || issue.type === 'format' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'"
                    >
                      {{ issue.typeName }}
                    </span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.field || '-' }}</td>
                  <td class="px-4 py-3 text-sm">{{ issue.description }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm">{{ issue.time }}</td>
                </tr>
                <tr v-if="issuesList.length === 0 && !loading">
                  <td colspan="5" class="px-4 py-8 text-center text-light-dark text-sm">暂无数据质量问题</td>
                </tr>
                <tr v-if="loading">
                  <td colspan="5" class="px-4 py-8 text-center text-light-dark text-sm">加载中...</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="mt-4 text-sm text-light-dark text-center">
            显示 {{ issuesList.length }} 条问题，共 {{ pagination.total }} 条
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
import { ref, onMounted, watch } from 'vue'
import { getQualityIssues } from '@/api/dataCollection'
import type { DataSource, QualityIssue } from '@/api/types'

const props = defineProps<{
  source: DataSource | null
}>()

defineEmits<{
  close: []
  export: []
}>()

const issuesList = ref<QualityIssue[]>([])
const statistics = ref({
  missing: 0,
  formatError: 0,
  abnormal: 0,
  inconsistent: 0
})
const loading = ref(false)
const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const loadQualityIssues = async () => {
  if (!props.source?.id) return
  
  try {
    loading.value = true
    const response = await getQualityIssues(props.source.id, {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      type: 'all'
    })
    
    if (response.data.code === 200) {
      issuesList.value = response.data.data.list
      statistics.value = response.data.data.statistics
      pagination.value.total = response.data.data.total
    }
  } catch (error) {
    console.error('加载质量问题失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.source?.id) {
    loadQualityIssues()
  }
})

watch(() => props.source, (newSource) => {
  if (newSource?.id) {
    loadQualityIssues()
  }
}, { deep: true })
</script>

