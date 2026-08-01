import client from './client'

export function fetchAppSettings() {
  return client.get('/settings/')
}

export function updateAppSettings(payload) {
  return client.patch('/settings/', payload)
}
