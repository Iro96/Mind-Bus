<template>
  <div class="memory-view">
    <div class="memory-header">
      <h1>Memory Management</h1>
      <p>Manage your agent's long-term and episodic memories</p>
    </div>

    <div class="memory-controls">
      <div class="filter-group">
        <label for="memory-type">Memory Type:</label>
        <select v-model="selectedMemoryType" id="memory-type">
          <option value="">All</option>
          <option value="episodic">Episodic</option>
          <option value="semantic">Semantic</option>
          <option value="correction">Correction</option>
        </select>
      </div>
      <button @click="refreshMemories" class="refresh-btn">
        🔄 Refresh Memories
      </button>
    </div>

    <div class="memories-container">
      <div v-if="loading" class="loading-state">
        <p>Loading memories...</p>
      </div>

      <div v-else-if="memories.length === 0" class="empty-state">
        <p>No memories found</p>
      </div>

      <div v-else>
        <div v-for="memory in filteredMemories" :key="memory.id" class="memory-card">
          <div class="memory-header-card">
            <span class="memory-type" :class="memory.memory_type">
              {{ memory.memory_type }}
            </span>
            <small class="memory-date">{{ formatDate(memory.created_at) }}</small>
          </div>

          <div class="memory-content">
            <h3>{{ memory.title }}</h3>
            <p>{{ memory.content }}</p>
          </div>

          <div class="memory-meta">
            <small v-if="memory.source">Source: {{ memory.source }}</small>
            <small v-if="memory.relevance_score">Relevance: {{ memory.relevance_score.toFixed(2) }}</small>
          </div>

          <div class="memory-actions">
            <button @click="deleteMemory(memory.id)" class="delete-btn">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from '@/services/api'
import { formatDistanceToNow } from 'date-fns'

interface Memory {
  id: string
  title: string
  content: string
  memory_type: string
  created_at: string
  source?: string
  relevance_score?: number
}

const memories = ref<Memory[]>([])
const selectedMemoryType = ref('')
const loading = ref(false)

const filteredMemories = computed(() => {
  if (!selectedMemoryType.value) return memories.value
  return memories.value.filter(m => m.memory_type === selectedMemoryType.value)
})

const formatDate = (dateStr: string) => {
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true })
}

const refreshMemories = async () => {
  loading.value = true
  try {
    const response = await axios.get('/memory', {
      params: { memory_type: selectedMemoryType.value || undefined }
    })
    memories.value = response.data.memories || []
  } catch (err) {
    console.error('Failed to load memories', err)
  } finally {
    loading.value = false
  }
}

const deleteMemory = async (memoryId: string) => {
  if (!confirm('Delete this memory?')) return

  try {
    await axios.delete(`/memory/${memoryId}`)
    memories.value = memories.value.filter(m => m.id !== memoryId)
  } catch (err) {
    console.error('Failed to delete memory', err)
  }
}

onMounted(() => {
  refreshMemories()
})
</script>

<style scoped lang="scss">
.memory-view {
  max-width: 1200px;
  margin: 0 auto;
}

.memory-header {
  margin-bottom: 2rem;

  h1 {
    margin: 0 0 0.5rem;
    color: #e2e8f0;
    font-size: 2rem;
  }

  p {
    margin: 0;
    color: #94a3b8;
  }
}

.memory-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #1e293b;
  border-radius: 8px;

  .filter-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;

    label {
      color: #cbd5e1;
      font-weight: 500;
    }

    select {
      padding: 0.5rem;
      border: 1px solid #475569;
      border-radius: 4px;
      background-color: #0f172a;
      color: #e2e8f0;

      &:focus {
        outline: none;
        border-color: #3b82f6;
      }
    }
  }

  .refresh-btn {
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
    }
  }
}

.memories-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;

  .loading-state,
  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
  }

  .memory-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;

    &:hover {
      border-color: #475569;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .memory-header-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;

      .memory-type {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;

        &.episodic {
          background: rgba(59, 130, 246, 0.2);
          color: #60a5fa;
        }

        &.semantic {
          background: rgba(139, 92, 246, 0.2);
          color: #a78bfa;
        }

        &.correction {
          background: rgba(239, 68, 68, 0.2);
          color: #fca5a5;
        }
      }

      .memory-date {
        color: #94a3b8;
        font-size: 0.8rem;
      }
    }

    .memory-content {
      margin-bottom: 1rem;

      h3 {
        margin: 0 0 0.5rem;
        color: #e2e8f0;
        font-size: 1rem;
      }

      p {
        margin: 0;
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.4;
        max-height: 100px;
        overflow: hidden;
      }
    }

    .memory-meta {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      margin-bottom: 1rem;
      font-size: 0.85rem;
      color: #94a3b8;
    }

    .memory-actions {
      display: flex;
      gap: 0.5rem;

      .delete-btn {
        flex: 1;
        padding: 0.5rem;
        background: #7f1d1d;
        color: #fca5a5;
        border: 1px solid #991b1b;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          background: #991b1b;
        }
      }
    }
  }
}
</style>
