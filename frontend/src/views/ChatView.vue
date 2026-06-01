<template>
  <div class="chat-container">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <button @click="newChat" class="new-chat-btn">
          + New Chat
        </button>
      </div>

      <div class="threads-list">
        <div
          v-for="thread in chatStore.threads"
          :key="thread.id"
          class="thread-item"
          :class="{ active: chatStore.currentThread?.id === thread.id }"
          @click="selectThread(thread.id)"
        >
          <p class="thread-title">{{ thread.title }}</p>
          <small class="thread-date">{{ formatDate(thread.created_at) }}</small>
        </div>
      </div>
    </div>

    <div class="chat-main">
      <div class="chat-header">
        <h2>{{ chatStore.currentThread?.title || 'New Chat' }}</h2>
      </div>

      <div class="messages-container">
        <div
          v-for="msg in chatStore.messages"
          :key="msg.id"
          class="message"
          :class="msg.role"
        >
          <div class="message-content">
            <p>{{ msg.content }}</p>
          </div>
          <small class="message-time">{{ formatTime(msg.created_at) }}</small>
        </div>

        <div v-if="chatStore.loading" class="message system">
          <div class="message-content">
            <p>Agent is thinking...</p>
          </div>
        </div>
      </div>

      <div class="chat-input-container">
        <textarea
          v-model="inputMessage"
          placeholder="Type your message..."
          @keyup.enter.ctrl="sendMessage"
          :disabled="chatStore.loading"
          class="chat-input"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || chatStore.loading"
          class="send-btn"
        >
          Send
        </button>
      </div>

      <p v-if="chatStore.error" class="error-message">{{ chatStore.error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { formatDistanceToNow, format } from 'date-fns'

const chatStore = useChatStore()
const inputMessage = ref('')

const formatDate = (dateStr: string) => {
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true })
}

const formatTime = (dateStr: string) => {
  return format(new Date(dateStr), 'HH:mm')
}

const newChat = () => {
  chatStore.currentThread = null
  chatStore.messages = []
  inputMessage.value = ''
}

const selectThread = (threadId: string) => {
  chatStore.fetchMessages(threadId)
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value
  inputMessage.value = ''

  const threadId = chatStore.currentThread?.id
  await chatStore.sendMessage(message, threadId)
}

onMounted(() => {
  chatStore.fetchThreads()
})
</script>

<style scoped lang="scss">
.chat-container {
  display: flex;
  height: calc(100vh - 80px);
  gap: 1rem;
}

.chat-sidebar {
  width: 300px;
  background: #1e293b;
  border-right: 1px solid #334155;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .sidebar-header {
    padding: 1rem;
    border-bottom: 1px solid #334155;

    .new-chat-btn {
      width: 100%;
      padding: 0.75rem;
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
      }
    }
  }

  .threads-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;

    .thread-item {
      padding: 1rem;
      margin-bottom: 0.5rem;
      background: #0f172a;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #1e293b;
      }

      &.active {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      }

      .thread-title {
        margin: 0;
        color: #e2e8f0;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .thread-date {
        color: #94a3b8;
        font-size: 0.85rem;
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #1e293b;
  border-radius: 8px;
  overflow: hidden;

  .chat-header {
    padding: 1.5rem;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-bottom: 1px solid #334155;

    h2 {
      margin: 0;
      color: #e2e8f0;
    }
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;

    .message {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;

      &.user {
        align-items: flex-end;

        .message-content {
          background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
          color: white;
        }
      }

      &.assistant {
        align-items: flex-start;

        .message-content {
          background: #334155;
          color: #e2e8f0;
        }
      }

      &.system {
        align-items: center;

        .message-content {
          background: #475569;
          color: #cbd5e1;
        }
      }

      .message-content {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 8px;

        p {
          margin: 0;
          word-wrap: break-word;
          white-space: pre-wrap;
        }
      }

      .message-time {
        color: #94a3b8;
        font-size: 0.85rem;
      }
    }
  }

  .chat-input-container {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    border-top: 1px solid #334155;

    .chat-input {
      flex: 1;
      padding: 0.75rem;
      border: 1px solid #475569;
      border-radius: 6px;
      background-color: #0f172a;
      color: #e2e8f0;
      resize: vertical;
      max-height: 150px;
      font-family: monospace;
      transition: all 0.3s ease;

      &:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .send-btn {
      padding: 0.75rem 1.5rem;
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .error-message {
    color: #ef4444;
    padding: 1rem;
    text-align: center;
  }
}
</style>
