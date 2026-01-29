import { requestWithoutApi } from './request'
import type {
  ApiResponse,
  PaginatedData,
  DataSource,
  DataSourceStatistics,
  DataSourceStatusDistribution,
  CollectionTrendData,
  QualityIssuesData,
  DataPreview,
  QualityScore
} from './types'

/**
 * 获取数据源列表
 */
export function getDataSources(params: {
  page?: number
  pageSize?: number
  status?: string
  keyword?: string
} = {}) {
  return requestWithoutApi.get<ApiResponse<PaginatedData<DataSource>>>('/data-collection/data-sources', {
    params: {
      page: params.page ?? 1,
      pageSize: params.pageSize ?? 10,
      status: params.status ?? 'all',
      keyword: params.keyword ?? ''
    }
  })
}

/**
 * 获取数据源统计
 */
export function getDataSourceStatistics() {
  return requestWithoutApi.get<ApiResponse<DataSourceStatistics>>('/data-collection/statistics')
}

/**
 * 获取数据源状态分布
 */
export function getDataSourceStatusDistribution() {
  return requestWithoutApi.get<ApiResponse<DataSourceStatusDistribution>>('/data-collection/status-distribution')
}

/**
 * 获取数据采集趋势
 */
export function getCollectionTrend(period: string = 'today') {
  return requestWithoutApi.get<ApiResponse<CollectionTrendData>>('/data-collection/collection-trend', {
    params: { period }
  })
}

/**
 * 获取数据质量问题
 */
export function getQualityIssues(
  sourceId: number,
  params: {
    page?: number
    pageSize?: number
    type?: string
  } = {}
) {
  return requestWithoutApi.get<ApiResponse<QualityIssuesData>>(
    `/data-collection/data-sources/${sourceId}/quality-issues`,
    {
      params: {
        page: params.page ?? 1,
        pageSize: params.pageSize ?? 10,
        type: params.type ?? 'all'
      }
    }
  )
}

/**
 * 获取数据预览
 */
export function getDataPreview(
  sourceId: number,
  params: {
    type?: string
    limit?: number
  } = {}
) {
  return requestWithoutApi.get<ApiResponse<DataPreview>>(
    `/data-collection/data-sources/${sourceId}/preview`,
    {
      params: {
        type: params.type ?? 'trade',
        limit: params.limit ?? 10
      }
    }
  )
}

/**
 * 获取数据质量评分
 */
export function getQualityScore(sourceId: number) {
  return requestWithoutApi.get<ApiResponse<QualityScore>>(
    `/data-collection/data-sources/${sourceId}/quality-score`
  )
}

/**
 * 重新连接数据源
 */
export function reconnectDataSource(sourceId: number) {
  return requestWithoutApi.post<ApiResponse<null>>(
    `/data-collection/data-sources/${sourceId}/reconnect`
  )
}

/**
 * 导出数据质量问题列表
 */
export function exportQualityIssues(
  sourceId: number,
  params: {
    type?: string
    format?: string
  } = {}
) {
  return requestWithoutApi.get(
    `/data-collection/data-sources/${sourceId}/quality-issues/export`,
    {
      params: {
        type: params.type ?? 'all',
        format: params.format ?? 'csv'
      },
      responseType: 'blob'
    }
  )
}

