<template>
  <div class="signin">
    <section class="signin__story" aria-hidden="true">
      <svg class="signin__graph" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid slice">
        <g class="graph__lines">
          <line x1="60" y1="80" x2="180" y2="40" />
          <line x1="180" y1="40" x2="320" y2="90" />
          <line x1="60" y1="80" x2="70" y2="220" />
          <line x1="180" y1="40" x2="200" y2="180" />
          <line x1="320" y1="90" x2="330" y2="240" />
          <line x1="70" y1="220" x2="200" y2="180" />
          <line x1="200" y1="180" x2="330" y2="240" />
          <line x1="70" y1="220" x2="120" y2="340" />
          <line x1="200" y1="180" x2="280" y2="330" />
          <line x1="330" y1="240" x2="280" y2="330" />
          <line x1="120" y1="340" x2="280" y2="330" />
        </g>
        <g class="graph__nodes">
          <circle cx="60" cy="80" r="5" style="animation-delay: 0s" />
          <circle cx="180" cy="40" r="4" style="animation-delay: 0.3s" />
          <circle cx="320" cy="90" r="6" style="animation-delay: 0.6s" />
          <circle cx="70" cy="220" r="4" style="animation-delay: 0.9s" />
          <circle cx="200" cy="180" r="7" style="animation-delay: 1.2s" />
          <circle cx="330" cy="240" r="5" style="animation-delay: 1.5s" />
          <circle cx="120" cy="340" r="4" style="animation-delay: 1.8s" />
          <circle cx="280" cy="330" r="5" style="animation-delay: 2.1s" />
        </g>
      </svg>

      <div class="signin__story-content">
        <div class="signin__brand">
          <span class="mark">◆</span>
          <span>Internal Assistant</span>
        </div>
        <h1>Company knowledge,<br />one message away.</h1>
        <ul class="signin__features">
          <li>Answers grounded in how your team actually works</li>
          <li>Available to every department, around the clock</li>
          <li>Runs entirely on our own infrastructure — nothing leaves the building</li>
        </ul>
      </div>
    </section>

    <section class="signin__form-panel">
      <form class="signin__form" @submit.prevent="handleLogin">
        <h2>Sign in</h2>
        <p class="subtitle">Use your company account to continue.</p>

        <label>
          Username
          <input v-model="username" autocomplete="username" autofocus />
        </label>
        <label>
          Password
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    localStorage.setItem('username', username.value)
    router.push({ name: 'chat' })
  } catch (e) {
    error.value = 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signin {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
}

/* ---- Left: story panel ---- */
.signin__story {
  position: relative;
  background: radial-gradient(circle at 20% 20%, #16212f 0%, var(--color-sidebar-bg) 55%, #0a0f17 100%);
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 64px;
}

.signin__graph {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.9;
}

.graph__lines line {
  stroke: rgba(20, 184, 166, 0.18);
  stroke-width: 1;
}

.graph__nodes circle {
  fill: var(--color-accent);
  animation: node-pulse 3.2s ease-in-out infinite;
}

@keyframes node-pulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}

.signin__story-content {
  position: relative;
  z-index: 1;
  max-width: 420px;
}

.signin__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-accent);
  margin-bottom: 28px;
}

.signin__story h1 {
  font-size: 34px;
  line-height: 1.25;
  margin: 0 0 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.signin__features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.signin__features li {
  position: relative;
  padding-left: 20px;
  font-size: 14px;
  line-height: 1.5;
  color: rgba(231, 235, 240, 0.8);
}

.signin__features li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 7px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
}

/* ---- Right: form panel ---- */
.signin__form-panel {
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.signin__form {
  width: 100%;
  max-width: 340px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.signin__form h2 {
  margin: 0;
  font-size: 24px;
}

.subtitle {
  margin: -8px 0 4px;
  color: var(--color-text-secondary);
  font-size: 13.5px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

input {
  padding: 11px 13px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-primary);
}

input:focus {
  border-color: var(--color-accent);
  outline: none;
}

button {
  margin-top: 8px;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 14px;
  transition: background 0.15s ease;
}

button:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: var(--color-danger);
  font-size: 12.5px;
  margin: 0;
}

/* ---- Responsive: stack on narrow viewports ---- */
@media (max-width: 860px) {
  .signin {
    grid-template-columns: 1fr;
  }
  .signin__story {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .graph__nodes circle {
    animation: none;
    opacity: 0.8;
  }
}
</style>