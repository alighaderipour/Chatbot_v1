import { defineStore } from 'pinia'
import { createUser, fetchUsers, importUsers, updateUser } from '../api/users'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
  }),

  actions: {
    async loadUsers() {
      this.loading = true
      try {
        const { data } = await fetchUsers()
        this.users = data
      } finally {
        this.loading = false
      }
    },

    async addUser(payload) {
      const { data } = await createUser(payload)
      this.users.unshift(data)
    },

    async editUser(id, payload) {
      const { data } = await updateUser(id, payload)
      const index = this.users.findIndex((u) => u.id === id)
      if (index !== -1) {
        this.users[index] = data
      }
    },

    async toggleActive(user) {
      await this.editUser(user.id, { is_active: !user.is_active })
    },

    async bulkImport(file) {
      const { data } = await importUsers(file)
      await this.loadUsers()
      return data
    },
  },
})
