<template>
  <div id="app" class="app-container">
    <nav class="navbar">
      <div class="nav-brand">
        <h1>🧠 Mind-Bus</h1>
        <p class="nav-subtitle">AI Agent Platform</p>
      </div>
      <div class="nav-menu">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          Chat
        </router-link>
        <router-link to="/memory" class="nav-link" :class="{ active: $route.path === '/memory' }">
          Memory
        </router-link>
        <router-link to="/documents" class="nav-link" :class="{ active: $route.path === '/documents' }">
          Documents
        </router-link>
        <router-link to="/tools" class="nav-link" :class="{ active: $route.path === '/tools' }">
          Tools
        </router-link>
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #0f172a;
  color: #e2e8f0;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-bottom: 2px solid #64748b;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.nav-brand {
  h1 {
    margin: 0;
    font-size: 1.8rem;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .nav-subtitle {
    margin: 0;
    font-size: 0.9rem;
    color: #94a3b8;
  }
}

.nav-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;

  .nav-link {
    color: #cbd5e1;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;

    &:hover {
      background-color: #475569;
      color: #f1f5f9;
    }

    &.active {
      background-color: #3b82f6;
      color: #fff;
      font-weight: 600;
    }
  }

  .logout-btn {
    padding: 0.5rem 1rem;
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background-color: #dc2626;
      transform: translateY(-2px);
    }
  }
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
