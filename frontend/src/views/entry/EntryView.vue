<template>
  <div class="entry-shell">
    <TopBar model-name="Qwen3.6-35B" :online="true" :username="username" @logout="handleLogout" />

    <div class="entry">
      <header class="entry__header">
        <h1>Internal Tools</h1>
        <p class="subtitle">Choose what you'd like to use.</p>
      </header>

      <div class="app-grid">
        <router-link
          v-for="app in apps"
          :key="app.path"
          :to="app.path"
          class="app-card"
          :class="{ 'app-card--disabled': app.comingSoon }"
          @click.prevent="app.comingSoon ? null : $router.push(app.path)"
        >
          <span class="app-card__icon">{{ app.icon }}</span>
          <span class="app-card__name">{{ app.name }}</span>
          <span class="app-card__description">{{ app.description }}</span>
          <span v-if="app.comingSoon" class="app-card__badge">Coming soon</span>
        </router-link>
      </div>
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

// Single source of truth for what shows up on the entry page. Add a new
// app here (and its route in router/index.js) and it appears automatically
// — this is the one place to touch when adding /phonebook etc. later.
// Set comingSoon: true for a card that's visible but not clickable yet.
const apps = [
  {
    name: 'Chatbot',
    path: '/chatbot',
    icon: '💬',
    description: 'Chat with the internal AI assistant',
  },
  {
    name: 'MRI Request',
    path: '/mrirequest',
    icon: '🩻',
    description: 'Submit and track MRI requests',
  },
  {
    name: 'Phonebook',
    path: '/phonebook',
    icon: '📇',
    description: 'Look up coworker contact info',
  },
]

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.entry-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.entry {
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 48px 24px 64px;
}

.entry__header {
  margin-bottom: 32px;
}

.entry__header h1 {
  margin: 0 0 6px;
  font-size: 24px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.app-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  text-decoration: none;
  transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  position: relative;
}

.app-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
}

.app-card--disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.app-card--disabled:hover {
  transform: none;
  box-shadow: none;
  border-color: var(--color-border);
}

.app-card__icon {
  font-size: 26px;
}

.app-card__name {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.app-card__description {
  font-size: 12.5px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.app-card__badge {
  position: absolute;
  top: 14px;
  right: 14px;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
</style>
