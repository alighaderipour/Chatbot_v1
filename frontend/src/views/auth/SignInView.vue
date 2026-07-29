<template>
  <div class="signin" dir="rtl" lang="fa">
    <div class="signin__header">
      <img :src="logo" alt="Company logo" class="signin__logo" />
      <h1 class="signin__title">هوش مصنوعی بیمارستان حضرت فاطمه (س) کرمان</h1>
    </div>

    <form class="signin__card" @submit.prevent="handleLogin">
      <h2>ورود</h2>
      <p class="subtitle">برای ورود نام کاربری و رمز عبور خود را وارد کنید</p>

      <label class="field">
        <span class="field__label">نام کاربری</span>
        <input v-model="username" type="text" autocomplete="username" autofocus />
      </label>

      <label class="field">
        <span class="field__label">رمز عبور</span>
        <div class="field__control">
          <input v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" />
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
        {{ loading ? 'در حال ورود…' : 'ورود' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <p class="footnote">دسترسی امن، مخصوص کارکنان تأییدشده</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import logo from '@/assets/images/bhf_logo.jpg'

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
    error.value = 'نام کاربری یا رمز عبور اشتباه است'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signin {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 48px 24px;
  background: var(--color-sidebar-bg);
}

.signin__header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.signin__logo {
  height: 52px;
  width: auto;
  object-fit: contain;
  border-radius: 8px;
}

.signin__title {
  margin: 0;
  color: var(--color-text-inverse);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  text-align: center;
}

.signin__card {
  width: 100%;
  max-width: 360px;
  background: var(--color-surface);
  border-radius: 16px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
}

h2 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: -8px 0 4px;
  color: var(--color-text-secondary);
  font-size: 13.5px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.field input {
  padding: 11px 13px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-primary);
}

.field input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.field__control {
  position: relative;
  display: flex;
  align-items: center;
}

.field__control input {
  width: 100%;
  padding-inline-end: 40px;
}

.field__toggle {
  position: absolute;
  inset-inline-end: 8px;
  background: none;
  border: none;
  padding: 6px;
  color: var(--color-text-secondary);
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
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 14px;
}

.submit:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: var(--color-danger);
  font-size: 12.5px;
  margin: 0;
}

.footnote {
  margin: 0;
  color: rgba(231, 235, 240, 0.4);
  font-size: 11.5px;
  text-align: center;
}
</style>