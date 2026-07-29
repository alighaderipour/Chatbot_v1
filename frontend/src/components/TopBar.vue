<template>
  <header class="topbar">
    <div class="topbar__brand">
      <span class="topbar__mark">◆</span>
      <span class="topbar__title">Internal Assistant</span>
    </div>

    <div class="topbar__status">
      <span class="status-dot" :class="{ 'status-dot--online': online }"></span>
      <span class="status-model">{{ modelName }}</span>
      <span class="status-sub">{{ online ? 'Online' : 'Offline' }}</span>
    </div>

    <div class="topbar__user">
      <span v-if="username" class="topbar__username">{{ username }}</span>
      <button class="topbar__logout" title="Sign out" @click="$emit('logout')">Sign out</button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  modelName: { type: String, default: 'Assistant' },
  online: { type: Boolean, default: true },
  username: { type: String, default: '' },
})
defineEmits(['logout'])
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
}

.topbar__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 200px;
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
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 200px;
  justify-content: flex-end;
}

.topbar__username {
  color: var(--color-text-inverse);
  font-size: 13px;
  opacity: 0.85;
}

.topbar__logout {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: var(--color-text-inverse);
  opacity: 0.8;
  padding: 6px 12px;
  font-size: 12.5px;
}

.topbar__logout:hover {
  opacity: 1;
  border-color: var(--color-accent);
  color: var(--color-accent);
}
</style>