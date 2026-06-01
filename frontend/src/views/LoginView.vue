<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>🧠 Mind-Bus</h1>
        <p>AI Agent Platform</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter username"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter password"
            required
          />
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <p v-if="error" class="error-message">{{ error }}</p>

        <div class="demo-creds">
          <p>Demo Credentials:</p>
          <ul>
            <li><strong>Admin:</strong> username: admin, password: password</li>
            <li><strong>User:</strong> username: user, password: password</li>
          </ul>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: #1e293b;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  border: 1px solid #334155;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;

  h1 {
    margin: 0;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  p {
    margin: 0.5rem 0 0;
    color: #94a3b8;
    font-size: 1rem;
  }
}

.form-group {
  margin-bottom: 1.5rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #cbd5e1;
    font-weight: 500;
  }

  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #475569;
    border-radius: 6px;
    background-color: #0f172a;
    color: #e2e8f0;
    font-size: 1rem;
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(59, 130, 246, 0.4);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.error-message {
  color: #ef4444;
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.demo-creds {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #475569;
  color: #94a3b8;
  font-size: 0.9rem;

  p {
    margin: 0 0 0.5rem;
    color: #cbd5e1;
    font-weight: 500;
  }

  ul {
    margin: 0;
    padding-left: 1rem;
    list-style: none;

    li {
      margin: 0.5rem 0;
      font-size: 0.85rem;
    }
  }
}
</style>
