<template>
  <div class="app-shell">
    <TopBar
      model-name="Qwen3.6-35B"
      :online="true"
      :username="username"
      @logout="handleLogout"
    />

    <div class="app-body">
      <Sidebar
        :conversations="store.conversations"
        :active-id="store.activeId"
        @new-chat="store.startNewConversation"
        @select="store.loadConversation"
        @delete="store.deleteConversation"
        @rename="store.renameConversation"
      />

      <main class="chat">
        <div class="messages" ref="messagesEl">
          <div v-if="!store.messages.length" class="empty-state">
            <p>Start a new conversation to begin.</p>
          </div>
          <ChatMessage v-for="m in store.messages" :key="m.id" :message="m" />
        </div>
        <ChatInput :disabled="store.sending" @send="store.sendMessage" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import ChatInput from '../../components/chat/ChatInput.vue'
import ChatMessage from '../../components/chat/ChatMessage.vue'
import Sidebar from '../../components/chat/Sidebar.vue'
import TopBar from '../../components/layout/TopBar.vue'
import { useAuthStore } from '../../stores/auth'
import { useConversationsStore } from '../../stores/conversations'

const router = useRouter()
const auth = useAuthStore()
const store = useConversationsStore()

const messagesEl = ref(null)
const username = ref(localStorage.getItem('username') || '')

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

// Auto-scroll whenever messages change or stream in new content
watch(() => store.messages, scrollToBottom, { deep: true })

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  store.loadConversations()
  if (!auth.me) {
    auth.loadMe()
  }
})
</script>

<style scoped>
.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  min-width: 0;
  min-height: 0;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.empty-state {
  margin: auto;
  color: var(--color-text-secondary);
  font-size: 14px;
}
</style>
