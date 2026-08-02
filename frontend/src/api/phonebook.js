import client from './client'

export function searchPhonebook(query) {
  return client.get('/phonebook/search/', { params: { q: query } })
}

export function fetchDepartments() {
  return client.get('/phonebook/departments/')
}

export function fetchSections(departmentId) {
  const params = departmentId ? { department: departmentId } : {}
  return client.get('/phonebook/sections/', { params })
}
