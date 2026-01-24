import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/monitor'
    },
    {
      path: '/monitor',
      name: 'monitor',
      component: () => import('../views/MonitorView.vue'),
      meta: { title: '实时监控 - 风控管理系统' }
    },
    {
      path: '/risk-warning',
      name: 'risk-warning',
      component: () => import('../views/RiskWarningView.vue'),
      meta: { title: '风险告警 - 风控管理系统' }
    },
    {
      path: '/data-collection',
      name: 'data-collection',
      component: () => import('../views/DataCollectionView.vue'),
      meta: { title: '数据采集 - 风控管理系统' }
    },
    {
      path: '/data-analysis',
      name: 'data-analysis',
      component: () => import('../views/DataAnalysisView.vue'),
      meta: { title: '事件分析 - 风控管理系统' }
    }
  ]
})

// 路由守卫 - 更新页面标题
router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || '风控管理系统'
  next()
})

export default router
