<template>
  <header class="topbar">
    <router-link to="/entry" class="topbar__brand">
      <span class="topbar__mark">◆</span>
      <span class="topbar__title">Internal Assistant</span>
    </router-link>

    <div class="topbar__status">
      <span class="status-dot" :class="{ 'status-dot--online': online }"></span>
      <span class="status-model">{{ modelName }}</span>
      <span class="status-sub">{{ online ? 'Online' : 'Offline' }}</span>
    </div>

    <div class="topbar__user" ref="menuRoot">
      <span v-if="messageUsage" class="usage-badge">{{ messageUsage }}</span>

      <button class="topbar__trigger" @click="menuOpen = !menuOpen">
        <span class="avatar">{{ initial }}</span>
        <span class="topbar__username">{{ displayName }}</span>
        <svg class="chevron" :class="{ 'chevron--open': menuOpen }" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </button>

      <div v-if="menuOpen" class="menu">
        <div class="menu__header">
          <span class="badge" :class="roleBadgeClass">{{ roleLabel }}</span>
        </div>

        <router-link v-if="auth.isStaff" to="/admin" class="menu__item" @click="menuOpen = false">
          Admin dashboard
        </router-link>

        <button class="menu__item menu__item--danger" @click="$emit('logout')">Sign out</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  modelName: { type: String, default: 'Assistant' },
  online: { type: Boolean, default: true },
  username: { type: String, default: '' },
})
defineEmits(['logout'])

const auth = useAuthStore()
const menuOpen = ref(false)
const menuRoot = ref(null)

// "username name family" — falls back to just the username prop until
// /me/ has loaded (e.g. the instant right after login, before loadMe()
// resolves).
const displayName = computed(() => {
  const uname = auth.me?.username || props.username
  const fullName = [auth.me?.first_name, auth.me?.last_name].filter(Boolean).join(' ')
  return fullName ? `${uname} ${fullName}` : uname
})

const initial = computed(() => (displayName.value ? displayName.value[0].toUpperCase() : '?'))

const roleLabel = computed(() => {
  if (auth.me?.is_superuser) return 'Admin'
  if (auth.me?.is_staff) return 'Staff'
  return 'User'
})

const roleBadgeClass = computed(() => {
  if (auth.me?.is_superuser) return 'badge--admin'
  if (auth.me?.is_staff) return 'badge--staff'
  return 'badge--user'
})

const messageUsage = computed(() => {
  if (!auth.me) return ''
  const { message_limit, message_count } = auth.me
  return message_limit != null ? `${message_count} / ${message_limit} messages` : 'Unlimited messages'
})

function handleClickOutside(event) {
  if (menuRoot.value && !menuRoot.value.contains(event.target)) {
    menuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--color-topbar-bg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
  position: relative;
  z-index: 20;
}

.topbar__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 200px;
  text-decoration: none;
}

.topbar__mark {
  color: var(--color-accent);
  font-size: 16px;
}

.topbar__title {
  color: var(--color-text-inverse);
  font-weight: 700;
  letter-spacing: 0.01em;
  font-size: 14.5px;
}

.topbar__status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-text-inverse);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #6b7280;
  flex-shrink: 0;
}

.status-dot--online {
  background: var(--color-accent);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.55);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(20, 184, 166, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0);
  }
}

.status-model {
  opacity: 0.85;
}

.status-sub {
  color: var(--color-accent);
}

.topbar__user {
  position: relative;
  min-width: 200px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.usage-badge {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-text-inverse);
  opacity: 0.75;
  white-space: nowrap;
}

.topbar__trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 4px 10px 4px 4px;
}

.topbar__trigger:hover {
  border-color: var(--color-accent);
}

.avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.topbar__username {
  color: var(--color-text-inverse);
  font-size: 13px;
}

.chevron {
  width: 14px;
  height: 14px;
  color: var(--color-text-inverse);
  opacity: 0.6;
  transition: transform 0.15s ease;
}

.chevron--open {
  transform: rotate(180deg);
}

.menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: var(--color-surface);
  border-radius: 10px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.menu__header {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-bottom: 1px solid var(--color-border);
}

.menu__item {
  padding: 10px 14px;
  text-align: left;
  background: none;
  border: none;
  font-size: 13.5px;
  color: var(--color-text-primary);
  text-decoration: none;
  display: block;
}

.menu__item:hover {
  background: var(--color-accent-soft);
}

.menu__item--danger {
  color: var(--color-danger);
}

.badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  width: fit-content;
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
</style>
