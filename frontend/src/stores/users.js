import { defineStore } from 'pinia'
import { createUser, fetchUsers, importUsers, updateUser } from '../api/users'

const PAGE_SIZE = 20 // must match UserPagination.page_size on the backend

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    page: 1,
    count: 0, // total users across all pages
  }),

  getters: {
    totalPages: (state) => Math.max(1, Math.ceil(state.count / PAGE_SIZE)),
  },

  actions: {
    async loadUsers(page = this.page) {
      this.loading = true
      try {
        const { data } = await fetchUsers(page)
        this.users = data.results
        this.count = data.count
        this.page = page
      } finally {
        this.loading = false
      }
    },

    nextPage() {
      if (this.page < this.totalPages) {
        this.loadUsers(this.page + 1)
      }
    },

    previousPage() {
      if (this.page > 1) {
        this.loadUsers(this.page - 1)
      }
    },

    async addUser(payload) {
      await createUser(payload)
      // A new user could land on any page depending on username sort order
      // — simplest correct behavior is just reloading the current page
      // rather than guessing where to splice it into the local array.
      await this.loadUsers(this.page)
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
      await this.loadUsers(this.page)
      return data
    },
  },
})
