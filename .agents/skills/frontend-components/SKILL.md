---
name: frontend-components
description: "Use when: building Vue 3 components, implementing state management with Pinia, adding routes, creating form handling, integrating API calls, or styling with SCSS"
keywords: ["vue3", "typescript", "component", "pinia", "router", "state management", "form", "api", "scss", "vite"]
---

# Frontend Components Skills

Patterns for building Vue 3 TypeScript components in Mind-Bus.

## Quick Start: Creating a Component

### 1. Basic Component Structure
```vue
<!-- src/views/MyView.vue -->
<template>
  <div class="my-view">
    <h1>{{ title }}</h1>
    
    <div v-if="isLoading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="content">
      <!-- Content here -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMyStore } from '@/stores/myStore'

const myStore = useMyStore()

const title = ref('My View')
const isLoading = ref(false)
const error = ref<string | null>(null)

const items = computed(() => myStore.items)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  isLoading.value = true
  try {
    await myStore.fetchItems()
  } catch (err) {
    error.value = (err as Error).message
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.my-view {
  padding: 2rem;
  
  h1 {
    color: #0f172a;
    margin-bottom: 1.5rem;
  }
  
  .loading,
  .error {
    text-align: center;
    padding: 2rem;
  }
  
  .error {
    color: #ef4444;
    background: #fee2e2;
    border-radius: 0.5rem;
  }
}
</style>
```

### 2. Create Pinia Store
```typescript
// src/stores/myStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/services/api'

export interface Item {
  id: string
  name: string
  description: string
  created_at: string
}

export const useMyStore = defineStore('my', () => {
  // State
  const items = ref<Item[]>([])
  const isLoading = ref(false)
  const selectedItem = ref<Item | null>(null)
  
  // Computed
  const itemCount = computed(() => items.value.length)
  const hasItems = computed(() => items.value.length > 0)
  
  // Actions
  async function fetchItems() {
    isLoading.value = true
    try {
      items.value = await api.getItems()
    } finally {
      isLoading.value = false
    }
  }
  
  async function createItem(name: string, description: string) {
    const response = await api.createItem({ name, description })
    items.value.push(response)
    return response
  }
  
  async function deleteItem(id: string) {
    await api.deleteItem(id)
    items.value = items.value.filter(item => item.id !== id)
  }
  
  function selectItem(item: Item) {
    selectedItem.value = item
  }
  
  // Return public API
  return {
    // State
    items,
    isLoading,
    selectedItem,
    
    // Computed
    itemCount,
    hasItems,
    
    // Actions
    fetchItems,
    createItem,
    deleteItem,
    selectItem
  }
})
```

### 3. Add Route
```typescript
// src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MyView from '@/views/MyView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/my-view',
    name: 'MyView',
    component: MyView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

## Component Patterns

### Reusable Component with Props
```vue
<!-- src/components/ItemCard.vue -->
<template>
  <div class="item-card" :class="{ selected }">
    <h3>{{ item.name }}</h3>
    <p>{{ item.description }}</p>
    
    <div class="actions">
      <button @click="emit('select')">Select</button>
      <button @click="emit('delete')" class="delete-btn">Delete</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Item {
  id: string
  name: string
  description: string
}

defineProps<{
  item: Item
  selected?: boolean
}>()

const emit = defineEmits<{
  select: []
  delete: []
}>()
</script>

<style scoped lang="scss">
.item-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
  transition: all 0.2s;
  
  &:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  &.selected {
    border-color: #3b82f6;
    background: #eff6ff;
  }
  
  h3 {
    margin: 0 0 0.5rem 0;
    color: #0f172a;
  }
  
  p {
    margin: 0 0 1rem 0;
    color: #64748b;
  }
  
  .actions {
    display: flex;
    gap: 0.5rem;
    
    button {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 0.25rem;
      background: #3b82f6;
      color: white;
      cursor: pointer;
      
      &:hover {
        background: #2563eb;
      }
      
      &.delete-btn {
        background: #ef4444;
        
        &:hover {
          background: #dc2626;
        }
      }
    }
  }
}
</style>
```

### Form Component
```vue
<!-- src/components/ItemForm.vue -->
<template>
  <form @submit.prevent="onSubmit" class="item-form">
    <div class="form-group">
      <label for="name">Name</label>
      <input
        v-model="formData.name"
        type="text"
        id="name"
        required
        placeholder="Enter name"
      />
      <span v-if="errors.name" class="error">{{ errors.name }}</span>
    </div>
    
    <div class="form-group">
      <label for="description">Description</label>
      <textarea
        v-model="formData.description"
        id="description"
        rows="4"
        placeholder="Enter description"
      />
      <span v-if="errors.description" class="error">{{ errors.description }}</span>
    </div>
    
    <button
      type="submit"
      :disabled="isSubmitting"
      class="submit-btn"
    >
      {{ isSubmitting ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const emit = defineEmits<{
  submit: [data: { name: string; description: string }]
}>()

const formData = reactive({
  name: '',
  description: ''
})

const errors = reactive({
  name: '',
  description: ''
})

const isSubmitting = ref(false)

async function onSubmit() {
  // Reset errors
  errors.name = ''
  errors.description = ''
  
  // Validate
  if (!formData.name) {
    errors.name = 'Name is required'
    return
  }
  
  isSubmitting.value = true
  try {
    emit('submit', { ...formData })
    formData.name = ''
    formData.description = ''
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped lang="scss">
.item-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  
  .form-group {
    display: flex;
    flex-direction: column;
    
    label {
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #0f172a;
    }
    
    input,
    textarea {
      padding: 0.75rem;
      border: 1px solid #e2e8f0;
      border-radius: 0.25rem;
      font-size: 1rem;
      
      &:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
    }
    
    .error {
      color: #ef4444;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  }
  
  .submit-btn {
    padding: 0.75rem 1.5rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover:not(:disabled) {
      background: #2563eb;
    }
    
    &:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }
  }
}
</style>
```

### API Service Integration
```typescript
// src/services/api.ts
import axios, { AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

const api: AxiosInstance = axios.create({
  baseURL: '/api'
})

// Request interceptor
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// Item endpoints
export async function getItems() {
  const response = await api.get('/items')
  return response.data
}

export async function createItem(data: { name: string; description: string }) {
  const response = await api.post('/items', data)
  return response.data
}

export async function deleteItem(id: string) {
  await api.delete(`/items/${id}`)
}

export async function updateItem(id: string, data: Partial<Item>) {
  const response = await api.put(`/items/${id}`, data)
  return response.data
}
```

## Styling Patterns

### Dark Theme with Tailwind Colors
```scss
// src/style.scss
$primary: #0f172a;       // slate-950
$primary-light: #1e293b; // slate-800
$accent: #3b82f6;        // blue-500
$success: #10b981;       // emerald-500
$error: #ef4444;         // red-500
$border: #e2e8f0;        // slate-200
$text: #0f172a;
$text-light: #64748b;    // slate-500
$bg: #ffffff;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: $bg;
  color: $text;
  line-height: 1.6;
}

a {
  color: $accent;
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}

button {
  font-family: inherit;
  font-size: 1rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  cursor: pointer;
  
  &:active {
    transform: scale(0.98);
  }
}

input,
textarea,
select {
  font-family: inherit;
  font-size: 1rem;
}
```

## Testing Patterns

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MyView from '@/views/MyView.vue'

describe('MyView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('renders component', () => {
    const wrapper = mount(MyView)
    expect(wrapper.find('h1').text()).toContain('My View')
  })
  
  it('loads data on mount', async () => {
    const wrapper = mount(MyView)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.content').exists()).toBe(true)
  })
  
  it('handles errors', async () => {
    // Mock store error
    // Verify error message is displayed
  })
})
```

## Common Mistakes

1. **Not Validating Props**: Always use TypeScript types
   ```typescript
   // ✅ CORRECT
   defineProps<{ item: Item }>()
   ```

2. **Not Unsubscribing**: Clean up subscriptions in `onUnmounted`
   ```typescript
   onUnmounted(() => {
     subscription.unsubscribe()
   })
   ```

3. **Blocking Renders**: Use `nextTick()` for DOM-dependent logic
   ```typescript
   // ✅ CORRECT
   await nextTick()
   ```

## Performance Tips

1. **Lazy Load Routes**: Code split by route
2. **Use Computed**: Cache expensive calculations
3. **Memoize Components**: Use `defineAsyncComponent` for large components
4. **Debounce Input**: Debounce form input handlers
5. **Virtualize Lists**: For large lists, use virtualization

## References

- **Vue 3 Docs**: https://vuejs.org
- **Pinia Docs**: https://pinia.vuejs.org
- **Components**: `frontend/src/components/`
- **Stores**: `frontend/src/stores/`
- **Views**: `frontend/src/views/`
- **Vite Config**: `frontend/vite.config.ts`
