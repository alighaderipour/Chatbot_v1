<template>
  <div :class="['message', message.role]">
    <div class="bubble">
      <span v-if="message.role === 'assistant'" class="bubble__label">Assistant</span>
      <p class="bubble__text">{{ message.content }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: { type: Object, required: true },
})
</script>

<style scoped>
.message {
  display: flex;
  margin: 10px 0;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 14px;
}

.bubble__label {
  display: block;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-accent-strong);
  margin-bottom: 4px;
}

.bubble__text {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 14.5px;
}

.message.user .bubble {
  background: var(--color-accent);
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.message.assistant .bubble {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 4px;
}
</style>
