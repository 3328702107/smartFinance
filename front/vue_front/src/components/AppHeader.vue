<template>
  <header class="bg-white shadow-sm sticky top-0 z-50 transition-smooth">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- 左侧Logo和标题 -->
        <div class="flex items-center space-x-2">
          <div class="text-primary text-2xl">
            <i class="fas fa-shield-alt"></i>
          </div>
          <h1 class="text-xl font-bold text-primary">风控管理系统</h1>
        </div>
        
        <!-- 中间导航菜单 -->
        <nav class="hidden md:flex space-x-8">
          <router-link 
            to="/monitor" 
            class="px-1 py-5 transition-smooth"
            :class="currentRoute === '/monitor' ? 'text-primary font-medium border-b-2 border-primary' : 'text-light-dark hover:text-primary'"
          >
            实时监控
          </router-link>
          <router-link 
            to="/risk-warning" 
            class="px-1 py-5 transition-smooth"
            :class="currentRoute === '/risk-warning' ? 'text-primary font-medium border-b-2 border-primary' : 'text-light-dark hover:text-primary'"
          >
            风险告警
          </router-link>
          <router-link 
            to="/data-collection" 
            class="px-1 py-5 transition-smooth"
            :class="currentRoute === '/data-collection' ? 'text-primary font-medium border-b-2 border-primary' : 'text-light-dark hover:text-primary'"
          >
            数据采集
          </router-link>
          <router-link 
            to="/data-analysis" 
            class="px-1 py-5 transition-smooth"
            :class="currentRoute === '/data-analysis' ? 'text-primary font-medium border-b-2 border-primary' : 'text-light-dark hover:text-primary'"
          >
            事件分析
          </router-link>
        </nav>
        
        <!-- 右侧用户信息 -->
        <div class="flex items-center space-x-4">
          <div class="relative">
            <button 
              @click="toggleUserMenu"
              class="flex items-center space-x-2 focus:outline-none"
            >
              <img 
                :src="avatarUrl" 
                alt="用户头像" 
                class="w-8 h-8 rounded-full object-cover border-2 border-primary"
              >
              <span class="hidden md:inline text-sm font-medium">{{ displayName }}</span>
              <i class="fas fa-angle-down text-light-dark"></i>
            </button>
            <div 
              v-show="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10"
            >
              <router-link 
                to="/profile" 
                class="block px-4 py-2 text-sm text-light-dark hover:bg-primary hover:text-white transition-smooth"
                @click="showUserMenu = false"
              >
                <i class="fas fa-user mr-2"></i>个人资料
              </router-link>
              <div class="border-t border-gray-100 my-1"></div>
              <a 
                href="#" 
                @click.prevent="handleLogout"
                class="block px-4 py-2 text-sm text-danger hover:bg-danger hover:text-white transition-smooth"
              >
                <i class="fas fa-sign-out-alt mr-2"></i>登出
              </a>
            </div>
          </div>
          
          <!-- 移动端菜单按钮 -->
          <button 
            @click="toggleMobileMenu"
            class="md:hidden text-light-dark hover:text-primary transition-smooth"
          >
            <i class="fas fa-bars text-xl"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 移动端导航菜单 -->
    <div 
      v-show="showMobileMenu"
      class="md:hidden bg-white border-t border-gray-100"
    >
      <div class="px-4 py-3 space-y-3">
        <router-link 
          to="/monitor" 
          class="block py-2 transition-smooth"
          :class="currentRoute === '/monitor' ? 'text-primary font-medium' : 'text-light-dark hover:text-primary'"
          @click="showMobileMenu = false"
        >
          实时监控
        </router-link>
        <router-link 
          to="/risk-warning" 
          class="block py-2 transition-smooth"
          :class="currentRoute === '/risk-warning' ? 'text-primary font-medium' : 'text-light-dark hover:text-primary'"
          @click="showMobileMenu = false"
        >
          风险告警
        </router-link>
        <router-link 
          to="/data-collection" 
          class="block py-2 transition-smooth"
          :class="currentRoute === '/data-collection' ? 'text-primary font-medium' : 'text-light-dark hover:text-primary'"
          @click="showMobileMenu = false"
        >
          数据采集
        </router-link>
        <router-link 
          to="/data-analysis" 
          class="block py-2 transition-smooth"
          :class="currentRoute === '/data-analysis' ? 'text-primary font-medium' : 'text-light-dark hover:text-primary'"
          @click="showMobileMenu = false"
        >
          事件分析
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUserProfile, type UserProfile } from '@/api/user'

const route = useRoute()
const router = useRouter()
const currentRoute = computed(() => route.path)

const showUserMenu = ref(false)
const showMobileMenu = ref(false)

// 用户信息
const userInfo = ref<Partial<UserProfile>>({
  username: '',
  name: '',
  avatar: ''
})

// 显示名称（优先显示 name，如果没有则显示 username）
const displayName = computed(() => {
  return userInfo.value.name || userInfo.value.username || '用户'
})

// 头像 URL
const avatarUrl = computed(() => {
  if (userInfo.value.avatar) {
    if (userInfo.value.avatar.startsWith('/')) {
      return `http://localhost:5000${userInfo.value.avatar}`
    }
    return userInfo.value.avatar
  }
  return 'https://picsum.photos/id/1005/200/200'
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return
    
    const { data: res } = await getUserProfile()
    if (res.code === 200 && res.data) {
      userInfo.value = {
        username: res.data.username,
        name: res.data.name,
        avatar: res.data.avatar
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showMobileMenu.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
  showUserMenu.value = false
}

const handleLogout = () => {
  // 清除 token
  localStorage.removeItem('token')
  // 跳转到登录页
  router.push('/login')
  showUserMenu.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
    showMobileMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchUserInfo()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

