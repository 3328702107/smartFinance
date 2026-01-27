import request from './request'
import type { ApiResponse } from './types'

// 用户资料类型
export interface UserProfile {
  id: string
  username: string
  name: string
  email: string
  phone: string
  avatar: string
  gender: string
  birthday: string
  bio: string
  role: string
  department: string
  employeeId: string
  joinDate: string
}

// 更新用户资料参数
export interface UpdateProfileParams {
  name?: string
  email?: string
  phone?: string
  gender?: string
  birthday?: string
  bio?: string
}

// 头像上传响应
export interface AvatarUploadResult {
  avatar: string
}

/**
 * 获取当前用户资料
 */
export function getUserProfile() {
  return request.get<ApiResponse<UserProfile>>('/user/profile')
}

/**
 * 更新用户资料
 */
export function updateUserProfile(data: UpdateProfileParams) {
  return request.put<ApiResponse<UserProfile>>('/user/profile', data)
}

/**
 * 上传用户头像
 */
export function uploadAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post<ApiResponse<AvatarUploadResult>>('/user/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

