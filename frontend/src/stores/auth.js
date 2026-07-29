import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
  }),
  actions: {
    async login(username, password) {
      const { data } = await api.post('/token/', { username, password })
      this.accessToken = data.access
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
    },
    logout() {
      this.accessToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})