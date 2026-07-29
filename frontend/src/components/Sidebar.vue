<template>
  <aside class="sidebar">
    <button class="sidebar__new" @click="$emit('new-chat')">
      <span class="plus">+</span> New chat
    </button>

    <nav class="sidebar__list">
      <button
        v-for="c in conversations"
        :key="c.id"
        class="sidebar__item"
        :class="{ 'sidebar__item--active': c.id === activeId }"
        @click="$emit('select', c.id)"
      >
        <span class="sidebar__item-title">{{ c.title }}</span>
        <span class="sidebar__item-time">{{ formatTime(c.updated_at) }}</span>
      </button>

      <p v-if="!conversations.length" class="sidebar__empty">No conversations yet</p>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  conversations: { type: Array, default: () => [] },
  activeId: { type: String, default: null },
})
defineEmits(['new-chat', 'select'])

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const sameDay = d.toDateString() === now.toDateString()
  return sameDay
    ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: var(--color-sidebar-bg);
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar__new {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-accent);
  color: #0b1520;
  border: none;
  border-radius: 8px;
  padding: 10px 12px;
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 16px;
  transition: background 0.15s ease;
}

.sidebar__new:hover {
  background: var(--color-accent-strong);
}

.plus {
  font-size: 15px;
  line-height: 1;
}

.sidebar__list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar__item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  text-align: left;
  padding: 9px 10px;
  border-radius: 6px;
  border: none;
  border-left: 3px solid transparent;
  background: transparent;
  color: var(--color-text-inverse);
  font-size: 13px;
  width: 100%;
}

.sidebar__item:hover {
  background: var(--color-sidebar-bg-hover);
}

.sidebar__item--active {
  background: var(--color-accent-soft);
  border-left-color: var(--color-accent);
}

.sidebar__item-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.sidebar__item-time {
  font-family: var(--font-mono);
  font-size: 11px;
  opacity: 0.5;
}

.sidebar__empty {
  color: var(--color-text-inverse);
  opacity: 0.4;
  font-size: 12px;
  padding: 10px;
}
</style>