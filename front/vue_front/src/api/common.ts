import request from './request'
import type { ApiResponse } from './types'

// 文件上传响应
export interface FileUploadResult {
  url: string
  filename: string
  originalName: string
  size: number
}

/**
 * 通用文件上传
 * @param file - 要上传的文件
 * @param type - 文件类型：image/document/other，默认 image
 */
export function uploadFile(file: File, type: string = 'image') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', type)
  
  return request.post<ApiResponse<FileUploadResult>>('/common/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

