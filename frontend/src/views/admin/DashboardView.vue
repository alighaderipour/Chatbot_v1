<template>
  <div class="dashboard-shell">
    <TopBar model-name="Qwen3.6-35B" :online="true" :username="username" @logout="handleLogout" />

    <div class="dashboard">
      <header class="dashboard__header">
        <div>
          <h1>User management</h1>
          <p class="subtitle">Create accounts, set message limits, and manage access.</p>
        </div>
        <router-link to="/" class="back-link">← Back to chat</router-link>
      </header>

      <section v-if="auth.isAdmin" class="panel">
        <h2>Add a user</h2>
        <form class="new-user-form" @submit.prevent="handleCreate">
          <input v-model="newUser.username" placeholder="Username" required />
          <input v-model="newUser.first_name" placeholder="First name" />
          <input v-model="newUser.last_name" placeholder="Last name" />
          <input v-model="newUser.password" type="password" placeholder="Password" required />
          <input
            v-model.number="newUser.message_limit"
            type="number"
            min="0"
            placeholder="Message limit (blank = unlimited)"
          />
          <select v-model="newUser.role">
            <option value="user">User</option>
            <option value="staff">Staff</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" :disabled="creating">
            {{ creating ? 'Creating…' : 'Create user' }}
          </button>
        </form>
        <p v-if="createError" class="error">{{ createError }}</p>
      </section>

      <section v-if="auth.isAdmin" class="panel">
        <h2>Import from Excel</h2>
        <p class="subtitle">
          Required columns: <code>username</code>, <code>name</code>, <code>family</code>.
          Optional: <code>password</code> (defaults to the username if left blank) and
          <code>message_limit</code> (blank = unlimited).
        </p>
        <div class="import-row">
          <input type="file" accept=".xlsx" @change="onFileChange" />
          <button :disabled="!importFile || importing" @click="handleImport">
            {{ importing ? 'Importing…' : 'Import' }}
          </button>
        </div>
        <div v-if="importResult" class="import-result">
          <p v-if="importResult.created.length">
            ✅ Created {{ importResult.created.length }} user(s) — copy these passwords now,
            they won't be shown again:
          </p>
          <table v-if="importResult.created.length" class="mini-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Password</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in importResult.created" :key="u.username">
                <td>{{ u.username }}</td>
                <td><code>{{ u.password }}</code></td>
              </tr>
            </tbody>
          </table>
          <p v-if="importResult.skipped.length" class="skipped">
            ⚠️ Skipped (username already exists): {{ importResult.skipped.join(', ') }}
          </p>
        </div>
      </section>

      <p v-if="!auth.isAdmin" class="staff-note">
        You're signed in as staff. You can edit and (de)activate regular users below. Creating new
        accounts and importing from Excel requires an admin.
      </p>

      <section class="panel">
        <h2>All users ({{ store.users.length }})</h2>
        <table class="users-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Status</th>
              <th>Role</th>
              <th>Message limit</th>
              <th>Sent</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in store.users" :key="u.id">
              <template v-if="editingId === u.id">
                <td>{{ u.username }}</td>
                <td class="stacked-inputs">
                  <input v-model="editForm.first_name" placeholder="First name" />
                  <input v-model="editForm.last_name" placeholder="Last name" />
                  <input
                    v-if="auth.isAdmin"
                    v-model="editForm.password"
                    type="password"
                    placeholder="New password (leave blank to keep)"
                  />
                </td>
                <td>
                  <label class="checkbox">
                    <input v-model="editForm.is_active" type="checkbox" /> Active
                  </label>
                </td>
                <td>
                  <select v-if="auth.isAdmin" v-model="editForm.role">
                    <option value="user">User</option>
                    <option value="staff">Staff</option>
                    <option value="admin">Admin</option>
                  </select>
                  <span v-else class="badge" :class="roleBadgeClass(u)">{{ roleLabel(u) }}</span>
                </td>
                <td>
                  <input
                    v-model.number="editForm.message_limit"
                    type="number"
                    min="0"
                    placeholder="Unlimited"
                  />
                </td>
                <td>{{ u.message_count }}</td>
                <td class="actions">
                  <button @click="saveEdit(u)">Save</button>
                  <button class="ghost" @click="editingId = null">Cancel</button>
                </td>
              </template>
              <template v-else>
                <td>{{ u.username }}</td>
                <td>{{ [u.first_name, u.last_name].filter(Boolean).join(' ') || '—' }}</td>
                <td>
                  <span :class="['badge', u.is_active ? 'badge--active' : 'badge--inactive']">
                    {{ u.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="roleBadgeClass(u)">{{ roleLabel(u) }}</span>
                </td>
                <td>{{ u.message_limit ?? 'Unlimited' }}</td>
                <td>{{ u.message_count }}</td>
                <td class="actions">
                  <template v-if="canEdit(u)">
                    <button @click="startEdit(u)">Edit</button>
                    <button class="ghost" @click="store.toggleActive(u)">
                      {{ u.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </template>
                  <span v-else class="locked-note">Admin only</span>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '../../components/layout/TopBar.vue'
import { useAuthStore } from '../../stores/auth'
import { useUsersStore } from '../../stores/users'

const router = useRouter()
const auth = useAuthStore()
const store = useUsersStore()

const username = ref(localStorage.getItem('username') || '')

function roleLabel(u) {
  if (u.is_superuser) return 'Admin'
  if (u.is_staff) return 'Staff'
  return 'User'
}

function roleBadgeClass(u) {
  if (u.is_superuser) return 'badge--admin'
  if (u.is_staff) return 'badge--staff'
  return 'badge--user'
}

// Staff can edit regular users; only admins can edit staff/admin accounts
// (matches the backend's ADMIN_ONLY_FIELDS / target-is-privileged check).
function canEdit(u) {
  if (auth.isAdmin) return true
  return auth.isStaff && !u.is_staff && !u.is_superuser
}

function roleToFlags(role) {
  return {
    user: { is_staff: false, is_superuser: false },
    staff: { is_staff: true, is_superuser: false },
    admin: { is_staff: true, is_superuser: true },
  }[role]
}

const emptyNewUser = () => ({
  username: '',
  first_name: '',
  last_name: '',
  password: '',
  message_limit: null,
  role: 'user',
})

const newUser = reactive(emptyNewUser())
const creating = ref(false)
const createError = ref('')

async function handleCreate() {
  createError.value = ''
  creating.value = true
  try {
    const { role, ...rest } = newUser
    await store.addUser({ ...rest, ...roleToFlags(role) })
    Object.assign(newUser, emptyNewUser())
  } catch (e) {
    createError.value = e.response?.data?.username?.[0] || 'Could not create user.'
  } finally {
    creating.value = false
  }
}

const editingId = ref(null)
const editForm = reactive({
  first_name: '',
  last_name: '',
  is_active: true,
  role: 'user',
  message_limit: null,
  password: '',
})

function startEdit(user) {
  editingId.value = user.id
  Object.assign(editForm, {
    first_name: user.first_name,
    last_name: user.last_name,
    is_active: user.is_active,
    role: user.is_superuser ? 'admin' : user.is_staff ? 'staff' : 'user',
    message_limit: user.message_limit,
    password: '',
  })
}

async function saveEdit(user) {
  const { role, password, ...rest } = editForm
  const payload = { ...rest }
  if (auth.isAdmin) {
    Object.assign(payload, roleToFlags(role))
    if (password) {
      payload.password = password
    }
  }
  await store.editUser(user.id, payload)
  editingId.value = null
}

const importFile = ref(null)
const importing = ref(false)
const importResult = ref(null)

function onFileChange(event) {
  importFile.value = event.target.files[0] || null
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    importResult.value = await store.bulkImport(importFile.value)
  } finally {
    importing.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => store.loadUsers())
</script>

<style scoped>
.dashboard-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.dashboard {
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px 64px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.dashboard__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.dashboard__header h1 {
  margin: 0 0 4px;
  font-size: 22px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13.5px;
}

.back-link {
  color: var(--color-accent-strong);
  font-size: 13px;
  text-decoration: none;
  white-space: nowrap;
}

.back-link:hover {
  text-decoration: underline;
}

.staff-note {
  margin: 0;
  padding: 12px 16px;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  border-radius: 8px;
  font-size: 13px;
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

.new-user-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
  margin-top: 14px;
  align-items: center;
}

.new-user-form input,
.new-user-form select {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13.5px;
}

.new-user-form input:focus,
.new-user-form select:focus {
  border-color: var(--color-accent);
  outline: none;
}

.new-user-form button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 13.5px;
}

.new-user-form button:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.new-user-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.import-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 14px;
}

.import-row button {
  padding: 9px 16px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 13.5px;
}

.import-row button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.import-result {
  margin-top: 16px;
  font-size: 13.5px;
}

.mini-table,
.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 13.5px;
}

.mini-table th,
.mini-table td,
.users-table th,
.users-table td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border);
}

.users-table th {
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.skipped {
  color: var(--color-danger);
  margin-top: 8px;
}

.stacked-inputs {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stacked-inputs input,
.users-table input[type='number'],
.users-table select {
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 13px;
  width: 100%;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
  white-space: nowrap;
}

.actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 600;
  font-size: 12.5px;
}

.actions button.ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.locked-note {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 600;
}

.badge--active {
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
}

.badge--inactive {
  background: rgba(220, 38, 38, 0.1);
  color: var(--color-danger);
}

.badge--admin {
  background: rgba(99, 102, 241, 0.12);
  color: #4f46e5;
}

.badge--staff {
  background: rgba(20, 184, 166, 0.12);
  color: var(--color-accent-strong);
}

.badge--user {
  background: rgba(107, 114, 128, 0.12);
  color: var(--color-text-secondary);
}

.error {
  color: var(--color-danger);
  font-size: 12.5px;
  margin-top: 10px;
}
</style>
