import { createRouter, createWebHistory } from 'vue-router'
import EntryView from '../views/entry/EntryView.vue'
import ChatView from '../views/chat/ChatView.vue'
import MriRequestView from '../views/mri/MriRequestView.vue'
import PhonebookView from '../views/phonebook/PhonebookView.vue'
import SignInView from '../views/auth/SignInView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import UsersPanel from '../views/admin/UsersPanel.vue'
import ReportsView from '../views/admin/ReportsView.vue'
import PreferencesView from '../views/admin/PreferencesView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: SignInView },
    {
      // The entry hub is the new "home" after login — each feature below
      // (chatbot, mrirequest, and whatever gets added later) is its own
      // top-level route so it can be linked to directly, not nested under
      // entry. '/' just redirects here for convenience.
      path: '/',
      redirect: { name: 'entry' },
    },
    {
      path: '/entry',
      name: 'entry',
      component: EntryView,
      meta: { requiresAuth: true },
    },
    {
      path: '/chatbot',
      name: 'chatbot',
      component: ChatView,
      meta: { requiresAuth: true },
    },
    {
      path: '/mrirequest',
      name: 'mrirequest',
      component: MriRequestView,
      meta: { requiresAuth: true },
    },
    {
      path: '/phonebook',
      name: 'phonebook',
      component: PhonebookView,
      meta: { requiresAuth: true },
    },
    // Add new apps here as they're built (e.g. /phonebook), and add a
    // matching card in views/entry/EntryView.vue's `apps` list.
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: { name: 'admin-users' } },
        { path: 'users', name: 'admin-users', component: UsersPanel },
        { path: 'reports', name: 'admin-reports', component: ReportsView },
        {
          path: 'preferences',
          name: 'admin-preferences',
          component: PreferencesView,
          meta: { requiresAuth: true, requiresAdmin: true, requiresSuperAdmin: true },
        },
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
      return { name: 'entry' }
    }
    if (to.meta.requiresSuperAdmin && !auth.isAdmin) {
      return { name: 'admin-users' }
    }
  }
})

export default router
