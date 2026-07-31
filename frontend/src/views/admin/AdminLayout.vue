<template>
  <div class="admin-shell">
    <TopBar model-name="Qwen3.6-35B" :online="true" :username="username" @logout="handleLogout" />

    <div class="admin-body">
      <main class="admin-content">
        <router-view />
      </main>

      <nav class="admin-nav">
        <router-link to="/admin/users" class="admin-nav__item">Users</router-link>
        <router-link to="/admin/reports" class="admin-nav__item">Reports</router-link>
        <!-- Add more sections here as they're built — gate any
             permission-restricted ones with v-if="auth.isAdmin" etc. -->
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '../../components/layout/TopBar.vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref(localStorage.getItem('username') || '')

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.admin-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

.admin-content {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}

.admin-nav {
  width: 200px;
  flex-shrink: 0;
  border-left: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  gap: 4px;
}

.admin-nav__item {
  padding: 10px 14px;
  border-radius: 8px;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 600;
}

.admin-nav__item:hover {
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
}

.admin-nav__item.router-link-active {
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
}
</style>
