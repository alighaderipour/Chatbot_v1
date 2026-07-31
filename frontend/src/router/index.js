import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/chat/ChatView.vue'
import SignInView from '../views/auth/SignInView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import UsersPanel from '../views/admin/UsersPanel.vue'
import ReportsView from '../views/admin/ReportsView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: SignInView },
    {
      path: '/',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: { name: 'admin-users' } },
        { path: 'users', name: 'admin-users', component: UsersPanel },
        { path: 'reports', name: 'admin-reports', component: ReportsView },
        // Add more sections here as they're built — matches the nav items
        // in AdminLayout.vue's right-side bar.
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.requiresAdmin) {
    const auth = useAuthStore()
    // On a hard page refresh, the store is freshly created and doesn't know
    // the user's admin status yet even though their token is still valid —
    // fetch it once before deciding whether to let them through.
    if (!auth.me) {
      try {
        await auth.loadMe()
      } catch (e) {
        return { name: 'login' }
      }
    }
    if (!auth.isStaff) {
      return { name: 'chat' }
    }
  }
})

export default router
