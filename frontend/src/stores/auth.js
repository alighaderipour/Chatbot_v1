import { defineStore } from 'pinia'
import { fetchMe, login as loginRequest } from '../api/auth'
import { useConversationsStore } from './conversations'
import { useUsersStore } from './users'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    me: null, // { id, username, first_name, last_name, is_staff, message_limit, message_count }
  }),

  getters: {
    // Matches backend IsStaffOrAdmin — true for both staff and admin tiers.
    isStaff: (state) => state.me?.is_staff ?? false,
    // Matches backend IsAdmin — true only for the top tier.
    isAdmin: (state) => state.me?.is_superuser ?? false,
  },

  actions: {
    async login(username, password) {
      // Clear any previous user's cached data before loading the new
      // user's — same reasoning as the reset in logout() below, but this
      // also covers sessions that ended without a clean logout (e.g. the
      // token simply expired and someone logged back in as someone else).
      useConversationsStore().$reset()
      useUsersStore().$reset()

      const { data } = await loginRequest(username, password)
      this.accessToken = data.access
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('username', username)
      await this.loadMe()
    },

    async loadMe() {
      const { data } = await fetchMe()
      this.me = data
    },

    logout() {
      this.accessToken = null
      this.me = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')

      // Without this, switching users in the same tab (logout, then log in
      // as someone else) left the previous user's open conversation and
      // message list sitting in memory until a hard page reload — because
      // these stores are singletons that persist across login sessions
      // unless explicitly cleared.
      useConversationsStore().$reset()
      useUsersStore().$reset()
    },
  },
})
