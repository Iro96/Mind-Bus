import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/services/api'

interface AuthUser {
  username: string
  user_id: string
  roles: string[]
}

function decodeJWTPayload(token: string): any | null {
  try {
    let payload = token.split('.')[1]
    // Add padding if needed (Base64URL -> Base64)
    const padding = 4 - (payload.length % 4)
    if (padding !== 4) {
      payload += '='.repeat(padding)
    }
    payload = payload.replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(payload))
  } catch (e) {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => !!user.value)

  const initializeFromToken = () => {
    const stored = localStorage.getItem('auth_user')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch (e) {
        user.value = null
      }
    }
  }

  const login = async (username: string, password: string) => {
    const response = await axios.post('/auth/token', { username, password })
    const jwt = response.data.access_token
    
    // Decode JWT to get user info (for display purposes only)
    const payload = decodeJWTPayload(jwt)
    if (payload) {
      user.value = {
        username: payload.sub || username,
        user_id: payload.user_id,
        roles: payload.roles || []
      }
      localStorage.setItem('auth_user', JSON.stringify(user.value))
    }
    
    // Token is now set as HttpOnly cookie by backend
    token.value = jwt
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_user')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    initializeFromToken
  }
})
