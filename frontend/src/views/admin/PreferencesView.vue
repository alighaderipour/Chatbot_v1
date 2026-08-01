<template>
  <div class="preferences">
    <h1>Preferences</h1>
    <p class="subtitle">Org-wide settings that apply to everyone.</p>

    <section class="panel">
      <h2>Daily message limit reset</h2>
      <p class="subtitle">
        Every user's message count resets to 0 at this time, every day.
      </p>

      <form class="reset-form" @submit.prevent="handleSave">
        <label>
          Reset time
          <input v-model="resetTime" type="time" required />
        </label>
        <button type="submit" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
      </form>

      <p v-if="lastResetDate" class="last-reset">
        Last ran: {{ lastResetDate }}
      </p>
      <p v-if="saved" class="saved-note">✅ Saved.</p>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchAppSettings, updateAppSettings } from '../../api/settings'

const resetTime = ref('07:00')
const lastResetDate = ref(null)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

async function load() {
  try {
    const { data } = await fetchAppSettings()
    // Backend sends "HH:MM:SS" — the <input type="time"> wants "HH:MM".
    resetTime.value = data.daily_reset_time.slice(0, 5)
    lastResetDate.value = data.last_reset_date
  } catch (e) {
    error.value = 'Could not load preferences.'
  }
}

async function handleSave() {
  error.value = ''
  saved.value = false
  saving.value = true
  try {
    await updateAppSettings({ daily_reset_time: resetTime.value })
    saved.value = true
  } catch (e) {
    error.value = 'Could not save — please try again.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.preferences {
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px 64px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preferences h1 {
  margin: 0 0 4px;
  font-size: 22px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13.5px;
}

.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}

.panel h2 {
  margin: 0 0 4px;
  font-size: 16px;
  color: var(--color-text-primary);
}

.reset-form {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.reset-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.reset-form input {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
}

.reset-form input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.reset-form button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 13.5px;
}

.reset-form button:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.reset-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-reset {
  margin: 14px 0 0;
  font-size: 12.5px;
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.saved-note {
  margin: 10px 0 0;
  color: var(--color-accent-strong);
  font-size: 13px;
}

.error {
  margin: 10px 0 0;
  color: var(--color-danger);
  font-size: 13px;
}
</style>
