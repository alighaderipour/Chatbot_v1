<template>
  <div class="mri-shell">
    <TopBar model-name="Qwen3.6-35B" :online="true" :username="username" @logout="handleLogout" />

    <div class="mri">
      <router-link to="/entry" class="back-link">← Back to apps</router-link>
      <h1>MRI Request</h1>
      <p class="subtitle">Coming soon.</p>
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
.mri-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.mri {
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.back-link {
  display: inline-block;
  margin-bottom: 16px;
  color: var(--color-accent-strong);
  font-size: 13px;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

.mri h1 {
  margin: 0 0 6px;
  font-size: 22px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13.5px;
}
</style>
