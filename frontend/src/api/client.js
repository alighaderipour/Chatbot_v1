import axios from 'axios'

// Your backend machine's LAN IP — coworkers' browsers need this exact address
// (localhost won't work for them; it means "their own machine", not yours).
const BASE_URL = 'http://192.168.9.35:8000/api'

const client = axios.create({
  baseURL: BASE_URL,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/token/refresh/`, { refresh })
          localStorage.setItem('access_token', data.access)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return client(originalRequest)
        } catch (e) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default client