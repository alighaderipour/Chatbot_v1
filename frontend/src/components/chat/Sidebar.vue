<template>
  <aside class="sidebar">
    <button class="sidebar__new" @click="$emit('new-chat')">
      <span class="plus">+</span> New chat
    </button>

    <nav class="sidebar__list">
      <div
        v-for="c in conversations"
        :key="c.id"
        class="sidebar__item"
        :class="{ 'sidebar__item--active': c.id === activeId }"
        @click="$emit('select', c.id)"
      >
        <div class="sidebar__item-text">
          <input
            v-if="editingId === c.id"
            ref="editInputRef"
            v-model="editingTitle"
            class="sidebar__item-input"
            @click.stop
            @blur="commitRename(c)"
            @keydown="handleTitleKeydown"
          />
          <span v-else class="sidebar__item-title">{{ c.title }}</span>
          <span class="sidebar__item-time">{{ formatTime(c.updated_at) }}</span>
        </div>
        <button
          class="sidebar__item-edit"
          title="Rename conversation"
          @click.stop="startEdit(c)"
        >
          ✎
        </button>
        <button
          class="sidebar__item-delete"
          title="Delete conversation"
          @click.stop="handleDelete(c)"
        >
          🗑
        </button>
      </div>

      <p v-if="!conversations.length" class="sidebar__empty">No conversations yet</p>
    </nav>
  </aside>
</template>

<script setup>
import { nextTick, ref } from 'vue'

defineProps({
  conversations: { type: Array, default: () => [] },
  activeId: { type: String, default: null },
})
const emit = defineEmits(['new-chat', 'select', 'delete', 'rename'])

const editingId = ref(null)
const editingTitle = ref('')
const editInputRef = ref(null)

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const sameDay = d.toDateString() === now.toDateString()
  return sameDay
    ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

function handleDelete(conversation) {
  // @click.stop keeps this from also triggering 'select' on the row underneath
  const confirmed = window.confirm(`Delete "${conversation.title}"? This can't be undone.`)
  if (confirmed) {
    emit('delete', conversation.id)
  }
}

async function startEdit(conversation) {
  editingId.value = conversation.id
  editingTitle.value = conversation.title
  await nextTick()
  const el = Array.isArray(editInputRef.value) ? editInputRef.value[0] : editInputRef.value
  el?.focus()
  el?.select()
}

function commitRename(conversation) {
  // If editingId was already cleared (e.g. by Escape below), this is a
  // cancelled edit — the blur event still fires, but we skip saving.
  if (editingId.value !== conversation.id) return

  const newTitle = editingTitle.value.trim()
  editingId.value = null
  if (newTitle && newTitle !== conversation.title) {
    emit('rename', conversation.id, newTitle)
  }
}

function handleTitleKeydown(event) {
  if (event.key === 'Enter') {
    event.target.blur() // triggers commitRename via @blur
  } else if (event.key === 'Escape') {
    editingId.value = null // commitRename will see the mismatch and skip saving
    event.target.blur()
  }
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
  align-items: center;
  gap: 6px;
  text-align: left;
  padding: 9px 8px 9px 10px;
  border-radius: 6px;
  border-left: 3px solid transparent;
  background: transparent;
  color: var(--color-text-inverse);
  font-size: 13px;
  width: 100%;
  cursor: pointer;
}

.sidebar__item:hover {
  background: var(--color-sidebar-bg-hover);
}

.sidebar__item--active {
  background: var(--color-accent-soft);
  border-left-color: var(--color-accent);
}

.sidebar__item-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.sidebar__item-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.sidebar__item-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--color-accent);
  border-radius: 4px;
  color: var(--color-text-inverse);
  font-family: inherit;
  font-size: 13px;
  padding: 2px 5px;
}

.sidebar__item-time {
  font-family: var(--font-mono);
  font-size: 11px;
  opacity: 0.5;
}

.sidebar__item-edit,
.sidebar__item-delete {
  flex-shrink: 0;
  background: none;
  border: none;
  font-size: 13px;
  padding: 4px 6px;
  border-radius: 4px;
  opacity: 0;
  color: var(--color-text-inverse);
}

.sidebar__item:hover .sidebar__item-edit,
.sidebar__item:hover .sidebar__item-delete {
  opacity: 0.55;
}

.sidebar__item-edit:hover {
  opacity: 1 !important;
  background: rgba(20, 184, 166, 0.15);
  color: var(--color-accent);
}

.sidebar__item-delete:hover {
  opacity: 1 !important;
  background: rgba(220, 38, 38, 0.15);
  color: #f87171;
}

.sidebar__empty {
  color: var(--color-text-inverse);
  opacity: 0.4;
  font-size: 12px;
  padding: 10px;
}
</style>