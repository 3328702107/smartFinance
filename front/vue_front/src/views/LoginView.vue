<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo 和标题 -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-indigo-600 rounded-2xl shadow-lg mb-4">
          <i class="fas fa-shield-alt text-white text-2xl"></i>
        </div>
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary to-indigo-600 bg-clip-text text-transparent">
          风控管理系统
        </h1>
        <p class="text-light-dark mt-2">请登录您的账户</p>
      </div>
      
      <!-- 登录卡片 -->
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-100">
        <div class="p-8">
          <!-- Tab 切换 -->
          <div class="flex mb-6 bg-gray-50 rounded-xl p-1">
            <button
              @click="isLogin = true"
              class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all"
              :class="isLogin 
                ? 'bg-white text-primary shadow-sm' 
                : 'text-light-dark hover:text-dark'"
            >
              登录
            </button>
            <button
              @click="isLogin = false"
              class="flex-1 py-2.5 text-sm font-medium rounded-lg transition-all"
              :class="!isLogin 
                ? 'bg-white text-primary shadow-sm' 
                : 'text-light-dark hover:text-dark'"
            >
              注册
            </button>
          </div>
          
          <!-- 登录表单 -->
          <form v-if="isLogin" @submit.prevent="handleLogin" class="space-y-5">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">用户名</label>
              <div class="relative">
                <input
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入用户名"
                  required
                  class="w-full px-4 py-3 pl-11 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
            </div>
            
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">密码</label>
              <div class="relative">
                <input
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  required
                  class="w-full px-4 py-3 pl-11 pr-11 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                >
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="flex items-center justify-between text-sm">
              <label class="flex items-center cursor-pointer">
                <input type="checkbox" class="rounded text-primary focus:ring-primary">
                <span class="ml-2 text-light-dark">记住我</span>
              </label>
              <a href="#" class="text-primary hover:text-primary/80">忘记密码？</a>
            </div>
            
            <button
              type="submit"
              :disabled="logging"
              class="w-full py-3 bg-gradient-to-r from-primary to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="logging" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ logging ? '登录中...' : '登录' }}
            </button>
          </form>
          
          <!-- 注册表单 -->
          <form v-else @submit.prevent="handleRegister" class="space-y-5">
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">用户名</label>
              <input
                v-model="registerForm.username"
                type="text"
                placeholder="请输入用户名"
                required
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              >
            </div>
            
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">密码</label>
              <input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                required
                minlength="6"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              >
            </div>
            
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">邮箱 <span class="text-light-dark font-normal">(可选)</span></label>
              <input
                v-model="registerForm.email"
                type="email"
                placeholder="请输入邮箱地址"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              >
            </div>
            
            <div class="space-y-2">
              <label class="block text-sm font-semibold text-dark">手机号 <span class="text-light-dark font-normal">(可选)</span></label>
              <input
                v-model="registerForm.phone"
                type="tel"
                placeholder="请输入手机号码"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              >
            </div>
            
            <button
              type="submit"
              :disabled="registering"
              class="w-full py-3 bg-gradient-to-r from-primary to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="registering" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ registering ? '注册中...' : '注册' }}
            </button>
          </form>
        </div>
      </div>
      
      <!-- Toast 提示 -->
      <Toast ref="toastRef" :message="toastMessage" :type="toastType" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login, register, type LoginParams, type RegisterParams } from '@/api/auth'
import Toast from '@/components/Toast.vue'

const router = useRouter()

const isLogin = ref(true)
const showPassword = ref(false)
const logging = ref(false)
const registering = ref(false)

const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const toastMessage = ref('')
const toastType = ref<'success' | 'warning'>('success')

const loginForm = reactive<LoginParams>({
  username: '',
  password: ''
})

const registerForm = reactive<RegisterParams>({
  username: '',
  password: '',
  email: '',
  phone: ''
})

const showToast = (message: string, type: 'success' | 'warning' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastRef.value?.show()
}

const handleLogin = async () => {
  logging.value = true
  try {
    const { data: res } = await login(loginForm)
    if (res.code === 200 && res.data) {
      // 保存 token
      localStorage.setItem('token', res.data.token)
      showToast('登录成功')
      // 跳转到首页
      setTimeout(() => {
        router.push('/monitor')
      }, 500)
    } else {
      showToast(res.message || '登录失败', 'warning')
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    const message = error.response?.data?.message || error.message || '登录失败，请检查用户名和密码'
    showToast(message, 'warning')
  } finally {
    logging.value = false
  }
}

const handleRegister = async () => {
  if (registerForm.password.length < 6) {
    showToast('密码长度至少为 6 位', 'warning')
    return
  }
  
  registering.value = true
  try {
    const { data: res } = await register(registerForm)
    if (res.code === 200) {
      showToast('注册成功，请登录')
      // 切换到登录 tab，不自动登录
      setTimeout(() => {
        isLogin.value = true
        // 将注册的用户名填入登录表单
        loginForm.username = registerForm.username
        loginForm.password = ''
        // 清空注册表单
        registerForm.username = ''
        registerForm.password = ''
        registerForm.email = ''
        registerForm.phone = ''
      }, 500)
    } else {
      showToast(res.message || '注册失败', 'warning')
    }
  } catch (error: any) {
    console.error('注册失败:', error)
    const message = error.response?.data?.message || error.message || '注册失败'
    showToast(message, 'warning')
  } finally {
    registering.value = false
  }
}
</script>

<style scoped>
/* 组件样式 */
</style>

