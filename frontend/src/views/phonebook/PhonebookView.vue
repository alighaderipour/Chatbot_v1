<template>
  <div class="phonebook-shell">
    <TopBar model-name="Qwen3.6-35B" :online="true" :username="username" @logout="handleLogout" />

    <div class="phonebook">
      <router-link to="/entry" class="back-link">← Back to apps</router-link>
      <h1>Phonebook</h1>

      <input
        v-model="query"
        class="search-input"
        type="text"
        placeholder="Search by name, username, department, or section…"
        autofocus
      />

      <p v-if="loading" class="hint">Searching…</p>
      <p v-else-if="query && !people.length && !sections.length" class="hint">No results.</p>

      <section v-if="people.length" class="results">
        <h2>People</h2>
        <div v-for="p in people" :key="p.id" class="card">
          <div class="card__main">
            <span class="card__name">{{ p.first_name }} {{ p.last_name }}</span>
            <span class="card__meta">{{ p.department_name || '—' }} · {{ p.section_name || '—' }}</span>
          </div>
          <div class="card__phones">
            <span v-if="p.personal_phone" class="phone-chip">📱 {{ p.personal_phone }}</span>
            <span v-for="ph in p.section_phones" :key="ph.id" class="phone-chip">
              {{ ph.phone_type_name }}: {{ ph.phone_number }}
            </span>
          </div>
        </div>
      </section>

      <section v-if="sections.length" class="results">
        <h2>Sections</h2>
        <div v-for="s in sections" :key="s.id" class="card">
          <div class="card__main">
            <span class="card__name">{{ s.name }}</span>
            <span class="card__meta">{{ s.department_name || '—' }}</span>
          </div>
          <div class="card__phones">
            <span v-for="ph in s.phones" :key="ph.id" class="phone-chip">
              {{ ph.phone_type_name }}: {{ ph.phone_number }}
            </span>
            <span v-if="!s.phones.length" class="hint">No phones on file</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '../../components/layout/TopBar.vue'
import { useAuthStore } from '../../stores/auth'
import { searchPhonebook } from '../../api/phonebook'

const router = useRouter()
const auth = useAuthStore()
const username = ref(localStorage.getItem('username') || '')

const query = ref('')
const people = ref([])
const sections = ref([])
const loading = ref(false)
let debounceTimer = null

watch(query, (value) => {
  clearTimeout(debounceTimer)
  if (!value.trim()) {
    people.value = []
    sections.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      const { data } = await searchPhonebook(value.trim())
      people.value = data.people
      sections.value = data.sections
    } finally {
      loading.value = false
    }
  }, 300)
})

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.phonebook-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.phonebook {
  max-width: 720px;
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

.phonebook h1 {
  margin: 0 0 16px;
  font-size: 22px;
  color: var(--color-text-primary);
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 14px;
  background: var(--color-surface);
}

.search-input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.hint {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-top: 16px;
}

.results {
  margin-top: 24px;
}

.results h2 {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 8px;
}

.card__main {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.card__name {
  font-weight: 700;
  font-size: 14.5px;
  color: var(--color-text-primary);
}

.card__meta {
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.card__phones {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.phone-chip {
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  font-size: 12px;
  font-family: var(--font-mono);
  padding: 3px 9px;
  border-radius: 999px;
}
</style>
