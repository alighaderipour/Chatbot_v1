<template>
  <div class="signin">
    <div class="signin__backdrop" aria-hidden="true">
      <span class="orb orb--one"></span>
      <span class="orb orb--two"></span>
      <span class="orb orb--three"></span>
      <div class="grid-overlay"></div>
    </div>

    <form class="signin__card" @submit.prevent="handleLogin">
      <div class="signin__brand">
        <span class="mark">◆</span>
        <span>Internal Assistant</span>
      </div>

      <h1>Welcome back</h1>
      <p class="subtitle">Sign in with your company account to continue.</p>

      <label class="field">
        <span class="field__label">Username</span>
        <div class="field__control">
          <svg class="field__icon" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0 2c-4.4 0-8 2.2-8 5v1h16v-1c0-2.8-3.6-5-8-5Z"
              fill="currentColor"
            />
          </svg>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="jane.doe"
            autofocus
          />
        </div>
      </label>

      <label class="field">
        <span class="field__label">Password</span>
        <div class="field__control">
          <svg class="field__icon" viewBox="0 0 24 24" fill="none">
            <path
              d="M6 10V8a6 6 0 1 1 12 0v2h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h1Zm2 0h8V8a4 4 0 1 0-8 0v2Z"
              fill="currentColor"
            />
          </svg>
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            placeholder="••••••••"
          />
          <button
            type="button"
            class="field__toggle"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            @click="showPassword = !showPassword"
          >
            <svg v-if="showPassword" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M6.6 6.7C4.5 8.1 3 10 2 12c1.6 3.6 5.4 7 10 7 1.6 0 3.1-.4 4.4-1.1M9.9 4.2A10.6 10.6 0 0 1 12 4c4.6 0 8.4 3.4 10 7-.6 1.3-1.4 2.5-2.4 3.6"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <path
                d="M2 12c1.6-3.6 5.4-7 10-7s8.4 3.4 10 7c-1.6 3.6-5.4 7-10 7s-8.4-3.4-10-7Z"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linejoin="round"
              />
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8" />
            </svg>
          </button>
        </div>
      </label>

      <button type="submit" class="submit" :disabled="loading">
        <span v-if="!loading">Sign in</span>
        <span v-else class="spinner" aria-hidden="true"></span>
      </button>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="footnote">Secure access for verified employees only.</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
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
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--color-sidebar-bg);
  padding: 24px;
}

/* ---- animated backdrop ---- */
.signin__backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.55;
  animation: drift 16s ease-in-out infinite;
}

.orb--one {
  width: 420px;
  height: 420px;
  background: var(--color-accent);
  top: -120px;
  left: -100px;
  animation-duration: 18s;
}

.orb--two {
  width: 360px;
  height: 360px;
  background: #6366f1;
  bottom: -140px;
  right: -80px;
  animation-duration: 22s;
  animation-delay: -6s;
}

.orb--three {
  width: 260px;
  height: 260px;
  background: #0d9488;
  top: 40%;
  right: 15%;
  animation-duration: 20s;
  animation-delay: -3s;
}

@keyframes drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.06); }
  66% { transform: translate(-20px, 25px) scale(0.96); }
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(circle at center, black 0%, transparent 75%);
}

/* ---- glass card ---- */
.signin__card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 380px;
  background: rgba(16, 24, 38, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 40px 34px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.signin__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
  margin-bottom: 4px;
}

h1 {
  margin: 0;
  font-size: 26px;
  color: var(--color-text-inverse);
  letter-spacing: -0.01em;
}

.subtitle {
  margin: -6px 0 6px;
  color: rgba(231, 235, 240, 0.6);
  font-size: 13.5px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.field__label {
  font-size: 12px;
  color: rgba(231, 235, 240, 0.65);
}

.field__control {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.field__control:focus-within {
  border-color: var(--color-accent);
  background: rgba(255, 255, 255, 0.07);
}

.field__icon {
  width: 18px;
  height: 18px;
  margin-left: 13px;
  color: rgba(231, 235, 240, 0.4);
  flex-shrink: 0;
}

.field__control input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 12px;
  font-size: 14px;
  color: var(--color-text-inverse);
}

.field__control input:focus {
  outline: none;
}

.field__control input::placeholder {
  color: rgba(231, 235, 240, 0.3);
}

.field__toggle {
  background: none;
  border: none;
  padding: 8px 12px;
  color: rgba(231, 235, 240, 0.45);
  display: flex;
}

.field__toggle:hover {
  color: var(--color-accent);
}

.field__toggle svg {
  width: 18px;
  height: 18px;
}

.submit {
  margin-top: 6px;
  padding: 13px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-strong));
  color: #06120f;
  font-weight: 700;
  font-size: 14.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
  box-shadow: 0 8px 24px rgba(20, 184, 166, 0.25);
}

.submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(20, 184, 166, 0.35);
}

.submit:active:not(:disabled) {
  transform: translateY(0);
}

.submit:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(6, 18, 15, 0.35);
  border-top-color: #06120f;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error {
  color: #f87171;
  font-size: 12.5px;
  margin: 0;
}

.footnote {
  margin: 8px 0 0;
  text-align: center;
  font-size: 11.5px;
  color: rgba(231, 235, 240, 0.35);
}

@media (prefers-reduced-motion: reduce) {
  .orb {
    animation: none;
  }
}
</style>