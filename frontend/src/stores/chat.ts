import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/services/api'

interface Thread {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface Message {
  id: string
  thread_id: string
  role: string
  content: string
  created_at: string
}

export const useChatStore = defineStore('chat', () => {
  const threads = ref<Thread[]>([])
  const currentThread = ref<Thread | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchThreads = async () => {
    error.value = null
    loading.value = true
    try {
      const response = await axios.get('/chat/threads')
      threads.value = response.data.threads || []
    } catch (err) {
      error.value = 'Failed to fetch threads'
    } finally {
      loading.value = false
    }
  }

  const fetchMessages = async (threadId: string) => {
    error.value = null
    loading.value = true
    try {
      const response = await axios.get(`/chat/threads/${threadId}`)
      currentThread.value = response.data.thread
      messages.value = response.data.messages || []
    } catch (err) {
      error.value = 'Failed to fetch messages'
    } finally {
      loading.value = false
    }
  }

  const sendMessage = async (message: string, threadId?: string) => {
    error.value = null
    loading.value = true
    try {
      const response = await axios.post('/chat', {
        message,
        thread_id: threadId
      })
      
      currentThread.value = response.data.thread
      messages.value = response.data.messages || []
      await fetchThreads()
    } catch (err) {
      error.value = 'Failed to send message'
    } finally {
      loading.value = false
    }
  }

  return {
    threads,
    currentThread,
    messages,
    loading,
    error,
    fetchThreads,
    fetchMessages,
    sendMessage
  }
})
