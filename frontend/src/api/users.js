import client from './client'

export function fetchUsers(page = 1) {
  return client.get('/users/', { params: { page } })
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
