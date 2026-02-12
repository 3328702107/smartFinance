import request from './request'
import type { ApiResponse, SystemStatus, RiskTrendData, RiskEvent, PaginatedData } from './types'

/**
 * 获取系统状态
 */
export function getSystemStatus() {
  return request.get<ApiResponse<SystemStatus>>('/monitor/system-status')
}

/**
 * 获取风险趋势数据（事件趋势）
 * @param period - 时间周期: today | week | month
 * @param hours - 仅在 period=today 时生效，默认 24，最大 72
 */
export function getRiskTrend(period: string = 'today', hours?: number) {
  const params: { period: string; hours?: number } = { period }
  if (period === 'today' && hours !== undefined) {
    params.hours = hours
  }
  return request.get<ApiResponse<RiskTrendData>>('/event-analysis/events/trend', {
    params
  })
}

/**
 * 获取风险事件列表
 */
export function getRiskEvents(params: {
  page?: number
  pageSize?: number
  type?: string
  status?: string
  keyword?: string
} = {}) {
  return request.get<ApiResponse<PaginatedData<RiskEvent>>>('/monitor/risk-events', {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 10,
      type: params.type ?? 'all',
      status: params.status ?? 'all',
      keyword: params.keyword ?? ''
    }
  })
}

/**
 * 获取风险事件详情
 */
export function getRiskEventDetail(eventId: string) {
  return request.get<ApiResponse<RiskEvent>>(`/monitor/risk-events/${eventId}`)
}

/**
 * 处理风险事件
 */
export function handleRiskEvent(eventId: string, data: { action: string; note?: string }) {
  return request.post<ApiResponse<null>>(`/monitor/risk-events/${eventId}/handle`, data)
}



