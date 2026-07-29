<template>
  <form class="chat-input" @submit.prevent="send">
    <input v-model="text" placeholder="Message the assistant…" :disabled="disabled" />
    <button type="submit" :disabled="disabled || !text.trim()">
      {{ disabled ? '…' : 'Send' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['send'])
defineProps({ disabled: Boolean })
const text = ref('')

function send() {
  if (!text.value.trim()) return
  emit('send', text.value)
  text.value = ''
}
</script>

<style scoped>
.chat-input {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-shrink: 0;
}

input {
  flex: 1;
  padding: 11px 14px;
  font-size: 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  color: var(--color-text-primary);
}

input:focus {
  border-color: var(--color-accent);
  outline: none;
}

button {
  padding: 11px 22px;
  border: none;
  border-radius: 8px;
  background: var(--color-accent);
  color: #0b1520;
  font-weight: 700;
  font-size: 13.5px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: var(--color-accent-strong);
}
</style>
