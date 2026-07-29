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
        :conversations="conversations"
        :active-id="activeId"
        @new-chat="startNewConversation"
        @select="loadConversation"
      />

      <main class="chat">
        <div class="messages" ref="messagesEl">
          <div v-if="!messages.length" class="empty-state">
            <p>Start a new conversation to begin.</p>
          </div>
          <ChatMessage v-for="m in messages" :key="m.id" :message="m" />
        </div>
        <ChatInput :disabled="sending" @send="handleSend" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import ChatInput from '../components/ChatInput.vue'
import ChatMessage from '../components/ChatMessage.vue'
import Sidebar from '../components/Sidebar.vue'
import TopBar from '../components/TopBar.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const conversations = ref([])
const activeId = ref(null)
const messages = ref([])
const sending = ref(false)
const messagesEl = ref(null)
const username = ref(localStorage.getItem('username') || '')

async function loadConversations() {
  const { data } = await api.get('/conversations/')
  conversations.value = data
}

async function startNewConversation() {
  const { data } = await api.post('/conversations/', { title: 'New conversation' })
  conversations.value.unshift(data)
  activeId.value = data.id
  messages.value = []
}

async function loadConversation(id) {
  activeId.value = id
  const { data } = await api.get(`/conversations/${id}/`)
  messages.value = data.messages
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function handleSend(text) {
  if (!activeId.value) {
    await startNewConversation()
  }

  messages.value.push({ id: crypto.randomUUID(), role: 'user', content: text })
  messages.value.push({ id: crypto.randomUUID(), role: 'assistant', content: '' })
  const assistantIndex = messages.value.length - 1
  await scrollToBottom()

  sending.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${api.defaults.baseURL}/conversations/${activeId.value}/messages/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content: text }),
    })
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      // Mutate through the reactive array (messages.value[i]), not a captured
      // plain-object reference, so Vue actually detects the change and re-renders.
      messages.value[assistantIndex].content += decoder.decode(value, { stream: true })
      await scrollToBottom()
    }
  } finally {
    sending.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(loadConversations)
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