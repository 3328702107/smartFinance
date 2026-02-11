import request from './request'
import type { ApiResponse } from './types'

export interface QianfanRiskJudgeParams {
  query: string
  user_id?: string
  conversation_id?: string
  inputs?: Record<string, unknown>
}

export interface QianfanRiskJudgeResult {
  available: boolean
  service: string
  share_url?: string
  answer?: string
  inferred_level?: string
  score_delta?: number
  attempts?: number
  message?: string
  raw?: Record<string, unknown>
}

export interface ModelStatusSummary {
  overall_status: 'normal' | 'abnormal' | 'degraded'
  services: Array<{
    service: string
    status: string
    message: string
    share_url?: string
  }>
}

/**
 * 获取模型服务状态
 */
export function getModelStatus() {
  return request.get<ApiResponse<ModelStatusSummary>>('/model/status')
}

/**
 * 千帆风控判断
 */
export function qianfanRiskJudge(params: QianfanRiskJudgeParams) {
  return request.post<ApiResponse<QianfanRiskJudgeResult>>('/model/qianfan-risk-judge', params)
}
