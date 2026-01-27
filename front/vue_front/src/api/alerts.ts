import request from './request'
import type { 
  ApiResponse, 
  AlertStatistics, 
  AlertLevelDistribution, 
  AlertTypeTrendData,
  AlertItem,
  PaginatedData 
} from './types'

/**
 * 获取告警统计
 */
export function getAlertStatistics(timeRange?: string) {
  return request.get<ApiResponse<AlertStatistics>>('/alerts/statistics', {
    params: timeRange ? { timeRange } : {}
  })
}

/**
 * 获取告警级别分布
 */
export function getAlertLevelDistribution() {
  return request.get<ApiResponse<AlertLevelDistribution>>('/alerts/level-distribution')
}

/**
 * 获取告警类型趋势
 * @param days - 天数，默认 6
 */
export function getAlertTypeTrend(days: number = 6) {
  return request.get<ApiResponse<AlertTypeTrendData>>('/alerts/type-trend', {
    params: { days }
  })
}

/**
 * 获取告警列表
 */
export function getAlertList(params: {
  page?: number
  pageSize?: number
  eventType?: string
  level?: string
  status?: string
  timeRange?: string
  startTime?: string
  endTime?: string
  keyword?: string
} = {}) {
  // 注意：后端路由定义为 /api/alerts/，需要带斜杠
  return request.get<ApiResponse<PaginatedData<AlertItem>>>('/alerts/', {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 10,
      eventType: params.eventType ?? 'all',
      level: params.level ?? 'all',
      status: params.status ?? 'all',
      timeRange: params.timeRange ?? 'all',
      keyword: params.keyword ?? ''
    }
  })
}

/**
 * 获取告警详情
 */
export function getAlertDetail(alertId: string) {
  return request.get<ApiResponse<AlertItem>>(`/alerts/${alertId}`)
}

/**
 * 更新告警状态
 */
export function updateAlertStatus(alertId: string, status: string) {
  return request.patch<ApiResponse<null>>(`/alerts/${alertId}/status`, { status })
}

/**
 * 批量操作告警
 */
export function batchOperateAlerts(data: { alertIds: string[]; action: string }) {
  return request.post<ApiResponse<{ successCount: number; failCount: number }>>('/alerts/batch-operation', data)
}

/**
 * 添加告警处理记录
 */
export function addProcessingRecord(alertId: string, data: { note: string; action?: string }) {
  return request.post<ApiResponse<null>>(`/alerts/${alertId}/processing-record`, data)
}

