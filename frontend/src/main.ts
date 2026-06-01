import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Initialize auth store from localStorage
const authStore = useAuthStore()
authStore.initializeFromToken()

app.mount('#app')
