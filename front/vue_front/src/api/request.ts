import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse } from './types'
import router from '@/router'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    
    // 业务状态码判断
    if (data.code === 200) {
      return response
    }
    
    // 401 未授权 - token 过期或无效
    if (data.code === 401) {
      localStorage.removeItem('token')
      // 跳转到登录页（排除登录页本身）
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
      console.warn('登录已过期，请重新登录')
    }
    
    // 其他业务错误
    console.error('业务错误:', data.message)
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  (error) => {
    // 网络错误等
    if (error.response) {
      const { status } = error.response
      switch (status) {
        case 401:
          localStorage.removeItem('token')
          // 跳转到登录页（排除登录页本身）
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login')
          }
          console.warn('未授权，请登录')
          break
        case 403:
          console.warn('拒绝访问')
          break
        case 404:
          console.warn('请求的资源不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求错误: ${status}`)
      }
    } else if (error.message.includes('timeout')) {
      console.error('请求超时')
    } else {
      console.error('网络错误:', error.message)
    }
    return Promise.reject(error)
  }
)

// 创建不带 /api 前缀的 axios 实例（用于数据采集接口）
export const requestWithoutApi = axios.create({
  baseURL: '',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
requestWithoutApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
requestWithoutApi.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    
    // 业务状态码判断
    if (data.code === 200) {
      return response
    }
    
    // 401 未授权 - token 过期或无效
    if (data.code === 401) {
      localStorage.removeItem('token')
      // 跳转到登录页（排除登录页本身）
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
      console.warn('登录已过期，请重新登录')
    }
    
    // 其他业务错误
    console.error('业务错误:', data.message)
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  (error) => {
    // 网络错误等
    if (error.response) {
      const { status } = error.response
      switch (status) {
        case 401:
          localStorage.removeItem('token')
          // 跳转到登录页（排除登录页本身）
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login')
          }
          console.warn('未授权，请登录')
          break
        case 403:
          console.warn('拒绝访问')
          break
        case 404:
          console.warn('请求的资源不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求错误: ${status}`)
      }
    } else if (error.message.includes('timeout')) {
      console.error('请求超时')
    } else {
      console.error('网络错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default request

