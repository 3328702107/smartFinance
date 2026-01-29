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

// ============ 数据采集相关类型 ============

// 数据源
export interface DataSource {
  id: number
  name: string
  type: string
  connection: string
  status: 'normal' | 'warning' | 'error' | 'stopped'
  statusName: string
  collectionStatus: 'running' | 'stopped'
  collectionStatusName: string
  lastSyncTime: string
  progress: number
  todayCollected: number
  estimatedCompletion?: string
  qualityIssuesCount: number
  errorMessage?: string | null
}

// 数据源统计
export interface DataSourceStatistics {
  total: number
  normal: number
  abnormal: number
  qualityIssues: number
}

// 数据源状态分布
export interface DataSourceStatusDistribution {
  normal: number
  warning: number
  error: number
  stopped: number
}

// 数据采集趋势
export interface CollectionTrendDataset {
  label: string
  data: number[]
}

export interface CollectionTrendData {
  labels: string[]
  datasets: CollectionTrendDataset[]
}

// 数据质量问题
export interface QualityIssue {
  id: string
  type: 'missing' | 'format' | 'abnormal' | 'inconsistent'
  typeName: string
  field: string | null
  description: string
  time: string
}

export interface QualityIssuesData {
  list: QualityIssue[]
  statistics: {
    missing: number
    formatError: number
    abnormal: number
    inconsistent?: number
  }
  total: number
  page: number
  pageSize: number
}

// 数据预览项
export interface DataPreviewItem {
  transactionId?: string
  userId?: string
  amount?: number
  time?: string
  status?: string
  [key: string]: any
}

export interface DataPreview {
  list: DataPreviewItem[]
  total: number
}

// 数据质量评分
export interface QualityScore {
  score: number
  maxScore: number
  dimensions: {
    completeness: number
    accuracy: number
    consistency: number
    timeliness: number
  }
}


