// 通用 API 响应格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  timestamp: number
}

// 分页响应格式
export interface PaginatedData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// ============ 实时监控相关类型 ============

// 系统状态
export interface SystemStatus {
  modelStatus: 'normal' | 'abnormal'
  modelStatusName: string
  dataStatus: 'normal' | 'abnormal'
  dataStatusName: string
}

// 风险趋势数据
export interface RiskTrendDataset {
  label: string
  data: number[]
}

export interface RiskTrendData {
  labels: string[]
  datasets: RiskTrendDataset[]
}

// ============ 告警相关类型 ============

// 告警统计
export interface AlertStatistics {
  total: number
  pending: number
  resolved: number
  highRisk: number
  mediumRisk: number
  lowRisk: number
}

// 告警级别分布
export interface AlertLevelDistribution {
  high: number
  medium: number
  low: number
}

// 告警类型趋势
export interface AlertTypeTrendDataset {
  label: string
  data: number[]
}

export interface AlertTypeTrendData {
  labels: string[]
  datasets: AlertTypeTrendDataset[]
}

// 告警项
export interface AlertItem {
  id: string
  eventType: string
  eventTypeName: string
  level: 'high' | 'medium' | 'low'
  levelName: string
  status: 'pending' | 'processing' | 'resolved' | 'ignored'
  statusName: string
  triggerTime: string
  handler: string
  handlerName: string
}

// ============ 风险事件相关类型 ============

export interface RiskEvent {
  id: string
  type: string
  typeName: string
  level: 'high' | 'medium' | 'low'
  levelName: string
  status: 'pending' | 'processing' | 'resolved' | 'ignored'
  statusName: string
  riskScore: number
  detectTime: string
  description: string
  userId: string
  username: string
  userName: string
}

