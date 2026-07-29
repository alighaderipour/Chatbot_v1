import { defineStore } from 'pinia'
import {
  createConversation,
  deleteConversation as deleteConversationRequest,
  fetchConversation,
  fetchConversations,
  sendMessageStream,
  updateConversation,
} from '../api/conversations'

// crypto.randomUUID() only works in "secure contexts" (HTTPS, or the literal
// hostname "localhost"). This app is served over plain HTTP from a LAN IP
// (e.g. http://192.168.9.35:5173) for coworkers, which is NOT a secure
// context — so crypto.randomUUID() throws there, even though it works fine
// when you test from the server itself via localhost. These IDs are only
// ever used as temporary client-side Vue :key values before a page reload
// re-fetches real IDs from the backend, so they don't need to be "real" UUIDs.
function tempId() {
  return `tmp-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

export const useConversationsStore = defineStore('conversations', {
  state: () => ({
    conversations: [],
    activeId: null,
    messages: [],
    sending: false,
  }),

  actions: {
    async loadConversations() {
      const { data } = await fetchConversations()
      this.conversations = data
    },

    async startNewConversation() {
      const { data } = await createConversation()
      this.conversations.unshift(data)
      this.activeId = data.id
      this.messages = []
    },

    async loadConversation(id) {
      this.activeId = id
      const { data } = await fetchConversation(id)
      this.messages = data.messages
    },

    async deleteConversation(id) {
      await deleteConversationRequest(id)
      this.conversations = this.conversations.filter((c) => c.id !== id)

      if (this.activeId === id) {
        this.activeId = null
        this.messages = []
      }
    },

    async renameConversation(id, title) {
      const { data } = await updateConversation(id, title)
      const conversation = this.conversations.find((c) => c.id === id)
      if (conversation) {
        conversation.title = data.title
      }
    },

    async sendMessage(text) {
      if (!this.activeId) {
        await this.startNewConversation()
      }

      this.messages.push({ id: tempId(), role: 'user', content: text })
      this.messages.push({ id: tempId(), role: 'assistant', content: '' })
      const assistantIndex = this.messages.length - 1

      this.sending = true
      try {
        const token = localStorage.getItem('access_token')
        const res = await sendMessageStream(this.activeId, text, token)
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          // Mutate through the store's own reactive state (this.messages[i]),
          // never through a captured plain-object reference — same reactivity
          // rule as before, just centralized here now instead of in the view.
          this.messages[assistantIndex].content += decoder.decode(value, { stream: true })
        }
      } finally {
        this.sending = false
      }
    },
  },
})