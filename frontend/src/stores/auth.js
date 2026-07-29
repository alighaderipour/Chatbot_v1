import { defineStore } from 'pinia'
import { login as loginRequest } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
  }),
  actions: {
    async login(username, password) {
      const { data } = await loginRequest(username, password)
      this.accessToken = data.access
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('username', username)
    },
    logout() {
      this.accessToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')
    },
  },
})
