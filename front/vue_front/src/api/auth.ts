import request from './request'
import type { ApiResponse } from './types'

// 登录请求参数（与后端完全匹配）
export interface LoginParams {
  username: string
  password: string
  device_id?: string
  ip_address?: string
  client_type?: string
  login_location?: string
}

// 登录响应数据（与后端完全匹配）
export interface LoginResponse {
  token: string
  refreshToken: string
  userInfo: {
    id: string
    username: string
    name: string
    email: string
    phone: string
    avatar: string
    role: string
    department: string
    employeeId: string
  }
  expiresIn: number
}

// 注册请求参数（与后端完全匹配）
export interface RegisterParams {
  username: string
  password: string
  phone?: string
  email?: string
}

// 注册响应数据（与后端完全匹配）
export interface RegisterResponse {
  user_id: string
  username: string
  token: string
}

/**
 * 用户登录
 * @param data 登录参数
 */
export function login(data: LoginParams) {
  return request.post<ApiResponse<LoginResponse>>('/auth/login', data)
}

/**
 * 用户注册
 * @param data 注册参数
 */
export function register(data: RegisterParams) {
  return request.post<ApiResponse<RegisterResponse>>('/auth/register', data)
}

/**
 * 获取当前登录信息
 */
export function getCurrentUser() {
  return request.get<ApiResponse<{
    user_id: string
    username: string
    phone: string
    email: string
    status: string
    account_level: string
  }>>('/auth/me')
}

/**
 * 用户登出
 */
export function logout() {
  return request.post<ApiResponse<null>>('/auth/logout')
}

/**
 * 刷新 Token
 * @param refreshToken 刷新令牌
 */
export function refreshToken(refreshToken: string) {
  return request.post<ApiResponse<{ token: string; expiresIn: number }>>('/auth/refresh', {
    refreshToken
  })
}

/**
 * 修改密码
 */
export function changePassword(data: { oldPassword: string; newPassword: string }) {
  return request.post<ApiResponse<null>>('/auth/change-password', data)
}

/**
 * 发送验证码（忘记密码）
 */
export function sendVerificationCode(contact: string) {
  return request.post<ApiResponse<{ expiresIn: number }>>('/auth/send-verification-code', {
    contact
  })
}

/**
 * 重置密码
 */
export function resetPassword(data: {
  contact: string
  verificationCode: string
  newPassword: string
}) {
  return request.post<ApiResponse<null>>('/auth/reset-password', data)
}
