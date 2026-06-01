<template>
  <div class="tools-view">
    <div class="tools-header">
      <h1>Tools & Integrations</h1>
      <p>Manage available tools and integrations for the agent</p>
    </div>

    <div class="tools-grid">
      <div v-if="loading" class="loading-state">
        <p>Loading tools...</p>
      </div>

      <div v-else-if="tools.length === 0" class="empty-state">
        <p>No tools available</p>
      </div>

      <div v-else>
        <div v-for="tool in tools" :key="tool.id" class="tool-card">
          <div class="tool-header">
            <h3>{{ tool.name }}</h3>
            <span class="tool-status" :class="{ enabled: tool.enabled }">
              {{ tool.enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>

          <p class="tool-description">{{ tool.description }}</p>

          <div class="tool-meta">
            <small v-if="tool.version">Version: {{ tool.version }}</small>
            <small v-if="tool.category">Category: {{ tool.category }}</small>
          </div>

          <div v-if="tool.parameters" class="tool-parameters">
            <h4>Parameters:</h4>
            <ul>
              <li v-for="param in tool.parameters" :key="param">
                {{ param }}
              </li>
            </ul>
          </div>

          <div class="tool-actions">
            <button
              @click="toggleTool(tool.id, !tool.enabled)"
              :class="{ enabled: tool.enabled }"
              class="toggle-btn"
            >
              {{ tool.enabled ? 'Disable' : 'Enable' }}
            </button>
            <button @click="viewToolDetails(tool.id)" class="details-btn">
              Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="tools-info">
      <h2>Available Tools</h2>
      <ul>
        <li><strong>Web Search:</strong> Search the web for information</li>
        <li><strong>Calculator:</strong> Perform mathematical calculations</li>
        <li><strong>File Operations:</strong> Read, write, and manage files</li>
        <li><strong>Database Query:</strong> Execute database queries</li>
        <li><strong>API Integration:</strong> Call external APIs</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/services/api'

interface Tool {
  id: string
  name: string
  description: string
  enabled: boolean
  version?: string
  category?: string
  parameters?: string[]
}

const tools = ref<Tool[]>([])
const loading = ref(false)

const loadTools = async () => {
  loading.value = true
  try {
    const response = await axios.get('/tools')
    tools.value = response.data.tools || []
  } catch (err) {
    console.error('Failed to load tools', err)
  } finally {
    loading.value = false
  }
}

const toggleTool = async (toolId: string, enabled: boolean) => {
  try {
    await axios.patch(`/tools/${toolId}`, { enabled })
    const tool = tools.value.find(t => t.id === toolId)
    if (tool) {
      tool.enabled = enabled
    }
  } catch (err) {
    console.error('Failed to toggle tool', err)
  }
}

const viewToolDetails = (toolId: string) => {
  const tool = tools.value.find(t => t.id === toolId)
  if (tool) {
    alert(`Tool: ${tool.name}\n\n${tool.description}`)
  }
}

onMounted(() => {
  loadTools()
})
</script>

<style scoped lang="scss">
.tools-view {
  max-width: 1200px;
  margin: 0 auto;
}

.tools-header {
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

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;

  .loading-state,
  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
  }

  .tool-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.3s ease;

    &:hover {
      border-color: #475569;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .tool-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;

      h3 {
        margin: 0;
        color: #e2e8f0;
        font-size: 1.1rem;
      }

      .tool-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #7f1d1d;
        color: #fca5a5;

        &.enabled {
          background: #064e3b;
          color: #86efac;
        }
      }
    }

    .tool-description {
      margin: 0.5rem 0;
      color: #cbd5e1;
      font-size: 0.9rem;
      line-height: 1.4;
    }

    .tool-meta {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      margin: 0.75rem 0;
      font-size: 0.85rem;
      color: #94a3b8;
    }

    .tool-parameters {
      margin: 0.75rem 0;
      padding: 0.5rem;
      background: #0f172a;
      border-radius: 4px;

      h4 {
        margin: 0 0 0.5rem;
        color: #cbd5e1;
        font-size: 0.9rem;
      }

      ul {
        margin: 0;
        padding-left: 1.5rem;
        list-style: disc;
        color: #94a3b8;
        font-size: 0.85rem;

        li {
          margin: 0.25rem 0;
        }
      }
    }

    .tool-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;

      .toggle-btn,
      .details-btn {
        flex: 1;
        padding: 0.5rem;
        border: 1px solid #475569;
        border-radius: 4px;
        background: #0f172a;
        color: #cbd5e1;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          background: #1e293b;
          border-color: #64748b;
        }

        &.toggle-btn.enabled {
          background: #064e3b;
          border-color: #10b981;
          color: #86efac;

          &:hover {
            background: #047857;
          }
        }
      }
    }
  }
}

.tools-info {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1.5rem;

  h2 {
    margin: 0 0 1rem;
    color: #e2e8f0;
  }

  ul {
    margin: 0;
    padding-left: 1.5rem;
    color: #cbd5e1;

    li {
      margin: 0.5rem 0;
      line-height: 1.6;

      strong {
        color: #60a5fa;
      }
    }
  }
}
</style>
