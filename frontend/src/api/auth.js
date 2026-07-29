import client from './client'

export function login(username, password) {
  return client.post('/token/', { username, password })
}

export function refreshToken(refresh) {
  return client.post('/token/refresh/', { refresh })
}
