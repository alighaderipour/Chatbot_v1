import client from './client'

export function fetchUsers() {
  return client.get('/users/')
}

export function createUser(payload) {
  return client.post('/users/', payload)
}

export function updateUser(id, payload) {
  return client.patch(`/users/${id}/`, payload)
}

export function importUsers(file) {
  const formData = new FormData()
  formData.append('file', file)
  return client.post('/users/import/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
