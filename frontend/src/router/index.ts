import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import ChatView from '@/views/ChatView.vue'
import MemoryView from '@/views/MemoryView.vue'
import DocumentsView from '@/views/DocumentsView.vue'
import ToolsView from '@/views/ToolsView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: ChatView,
    meta: { requiresAuth: true }
  },
  {
    path: '/memory',
    component: MemoryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    component: DocumentsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tools',
    component: ToolsView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
