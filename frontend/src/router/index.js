import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/chat/ChatView.vue'
import SignInView from '../views/auth/SignInView.vue'

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
  ],
})

router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }
})

export default router
