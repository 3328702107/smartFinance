import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/monitor'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: '登录 - 风控管理系统', requiresAuth: false }
    },
    {
      path: '/monitor',
      name: 'monitor',
      component: () => import('../views/MonitorView.vue'),
      meta: { title: '实时监控 - 风控管理系统', requiresAuth: true }
    },
    {
      path: '/risk-warning',
      name: 'risk-warning',
      component: () => import('../views/RiskWarningView.vue'),
      meta: { title: '风险告警 - 风控管理系统', requiresAuth: true }
    },
    {
      path: '/data-collection',
      name: 'data-collection',
      component: () => import('../views/DataCollectionView.vue'),
      meta: { title: '数据采集 - 风控管理系统', requiresAuth: true }
    },
    {
      path: '/data-analysis',
      name: 'data-analysis',
      component: () => import('../views/DataAnalysisView.vue'),
      meta: { title: '事件分析 - 风控管理系统', requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { title: '个人资料 - 风控管理系统', requiresAuth: true }
    }
  ]
})

// 路由守卫 - 更新页面标题和认证检查
router.beforeEach((to, from, next) => {
  document.title = (to.meta.title as string) || '风控管理系统'
  
  // 检查是否需要登录
  const requiresAuth = to.meta.requiresAuth !== false
  const token = localStorage.getItem('token')
  
  // 如果需要登录但没有 token，跳转到登录页
  if (requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  }
  // 如果已登录但访问登录页，跳转到首页
  else if (to.path === '/login' && token) {
    next('/monitor')
  }
  else {
    next()
  }
})

export default router
