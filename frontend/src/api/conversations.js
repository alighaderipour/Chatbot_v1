import client from './client'

export function fetchConversations() {
  return client.get('/conversations/')
}

export function createConversation(title = 'New conversation') {
  return client.post('/conversations/', { title })
}

export function fetchConversation(id) {
  return client.get(`/conversations/${id}/`)
}

export function updateConversation(id, title) {
  return client.patch(`/conversations/${id}/`, { title })
}

export function deleteConversation(id) {
  return client.delete(`/conversations/${id}/`)
}

// Streaming responses need raw fetch (axios doesn't stream well in the browser),
// but the URL/auth logic still lives here so views never build requests by hand.
export function sendMessageStream(conversationId, content, token) {
  return fetch(`${client.defaults.baseURL}/conversations/${conversationId}/messages/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
  })
}