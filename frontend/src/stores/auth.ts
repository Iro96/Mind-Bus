import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/services/api'

interface AuthUser {
  username: string
  user_id: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (username: string, password: string) => {
    const response = await axios.post('/auth/token', { username, password })
    token.value = response.data.access_token
    localStorage.setItem('token', response.data.access_token)
    
    // Decode token to get user info (basic JWT parsing)
    const payload = JSON.parse(atob(response.data.access_token.split('.')[1]))
    user.value = {
      username: payload.sub,
      user_id: payload.user_id,
      roles: payload.roles
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout
  }
})
