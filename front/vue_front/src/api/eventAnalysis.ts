import request from './request'
import type {
  ApiResponse,
  EventAnalysisDetail,
  EventTimelineResponse,
  EventRelatedAccountList,
  EventDevicesIpsData,
  EventTransactionList,
  EventResponsibilityData,
  EventRiskAnalysisData,
  EventProcessingRecordList,
  EventProcessingRecord
} from './types'

// 7.1 获取事件详情
export function getEventAnalysisDetail(eventId: string) {
  return request.get<ApiResponse<EventAnalysisDetail>>(`/event-analysis/events/${eventId}`)
}

// 7.2 获取事件时间线
export function getEventTimeline(eventId: string) {
  return request.get<ApiResponse<EventTimelineResponse>>(`/event-analysis/events/${eventId}/timeline`)
}

// 7.4 获取关联账户信息
export function getEventRelatedAccounts(eventId: string) {
  return request.get<ApiResponse<EventRelatedAccountList>>(`/event-analysis/events/${eventId}/related-accounts`)
}

// 7.5 获取关联设备和 IP 信息
export function getEventDevicesIps(eventId: string) {
  return request.get<ApiResponse<EventDevicesIpsData>>(`/event-analysis/events/${eventId}/devices-ips`)
}

// 7.6 获取关联交易记录
export function getEventTransactions(eventId: string, params: { page?: number; pageSize?: number } = {}) {
  return request.get<ApiResponse<EventTransactionList>>(`/event-analysis/events/${eventId}/transactions`, {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 10
    }
  })
}

// 7.7 获取责任追溯信息
export function getEventResponsibility(eventId: string) {
  return request.get<ApiResponse<EventResponsibilityData>>(`/event-analysis/events/${eventId}/responsibility`)
}

// 7.8 获取风险分析和处理建议
export function getEventRiskAnalysis(eventId: string) {
  return request.get<ApiResponse<EventRiskAnalysisData>>(`/event-analysis/events/${eventId}/risk-analysis`)
}

// 7.9 获取处理记录
export function getEventProcessingRecords(eventId: string) {
  return request.get<ApiResponse<EventProcessingRecordList>>(`/event-analysis/events/${eventId}/processing-records`)
}

// 7.10 添加处理记录
export function addEventProcessingRecord(eventId: string, data: { note: string; action?: string; operator?: string }) {
  return request.post<ApiResponse<EventProcessingRecord>>(`/event-analysis/events/${eventId}/processing-records`, data)
}

// 7.11 更新事件状态
export function updateEventStatus(eventId: string, status: string) {
  return request.put<ApiResponse<null>>(`/event-analysis/events/${eventId}/status`, { status })
}

// 7.12 编辑事件信息
export function updateEvent(eventId: string, data: { level?: string; note?: string; description?: string }) {
  return request.put<ApiResponse<null>>(`/event-analysis/events/${eventId}`, data)
}

// 7.13 导出事件报告（返回文本流，由前端触发下载）
export function exportEventReport(eventId: string) {
  return request.get(`/event-analysis/events/${eventId}/export`, {
    responseType: 'blob'
  })
}


