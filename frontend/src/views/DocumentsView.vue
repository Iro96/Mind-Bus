<template>
  <div class="documents-view">
    <div class="documents-header">
      <h1>Document Management</h1>
      <p>Upload and manage documents for RAG</p>
    </div>

    <div class="upload-section">
      <div class="upload-box" @drop="handleDrop" @dragover.prevent @dragleave="isDragging = false">
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".txt,.pdf,.md,.docx"
          @change="handleFileSelect"
          style="display: none"
        />
        <button @click="$refs.fileInput.click()" class="upload-btn">
          📤 Select Files
        </button>
        <p>or drag and drop files here</p>
        <small>Supported: txt, pdf, md, docx</small>
      </div>

      <div v-if="uploadProgress > 0 && uploadProgress < 100" class="progress-bar">
        <div class="progress" :style="{ width: uploadProgress + '%' }"></div>
        <span>{{ uploadProgress }}%</span>
      </div>
    </div>

    <div class="documents-list">
      <h2>Documents</h2>

      <div v-if="loading" class="loading-state">
        <p>Loading documents...</p>
      </div>

      <div v-else-if="documents.length === 0" class="empty-state">
        <p>No documents uploaded yet</p>
      </div>

      <div v-else class="documents-grid">
        <div v-for="doc in documents" :key="doc.id" class="document-card">
          <div class="document-icon">📄</div>
          <div class="document-info">
            <h3>{{ doc.filename }}</h3>
            <small>{{ formatFileSize(doc.size) }}</small>
            <small class="doc-date">{{ formatDate(doc.created_at) }}</small>
          </div>

          <div class="document-actions">
            <button @click="downloadDocument(doc.id)" class="action-btn">⬇️</button>
            <button @click="deleteDocument(doc.id)" class="action-btn delete">🗑️</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/services/api'
import { formatDistanceToNow } from 'date-fns'

interface Document {
  id: string
  filename: string
  size: number
  created_at: string
  content_type: string
}

const documents = ref<Document[]>([])
const loading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement>()

const formatDate = (dateStr: string) => {
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true })
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files) return

  await uploadFiles(target.files)
  target.value = ''
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false

  if (!event.dataTransfer?.files) return
  await uploadFiles(event.dataTransfer.files)
}

const uploadFiles = async (files: FileList) => {
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)

    try {
      uploadProgress.value = 0
      const response = await axios.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total && typeof e.total === 'number') {
            uploadProgress.value = Math.round((e.loaded / e.total) * 100)
          }
        }
      })

      documents.value.push(response.data.document)
      uploadProgress.value = 0
    } catch (err) {
      console.error('Upload failed', err)
    }
  }
}

const downloadDocument = async (docId: string) => {
  try {
    const response = await axios.get(`/documents/${docId}/download`, {
      responseType: 'blob'
    })

    let filename = docId
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)|filename=([^;]+)/)
      if (filenameMatch) {
        filename = filenameMatch[1] ? decodeURIComponent(filenameMatch[1]) : (filenameMatch[2] || docId).trim('"')
      }
    } else {
      const doc = documents.value.find(d => d.id === docId)
      filename = doc?.filename || docId
    }

    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Download failed', err)
  }
}

const deleteDocument = async (docId: string) => {
  if (!confirm('Delete this document?')) return

  try {
    await axios.delete(`/documents/${docId}`)
    documents.value = documents.value.filter(d => d.id !== docId)
  } catch (err) {
    console.error('Delete failed', err)
  }
}

const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await axios.get('/documents')
    documents.value = response.data.documents || []
  } catch (err) {
    console.error('Failed to load documents', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped lang="scss">
.documents-view {
  max-width: 1000px;
  margin: 0 auto;
}

.documents-header {
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

.upload-section {
  margin-bottom: 3rem;

  .upload-box {
    border: 2px dashed #475569;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
    background: #1e293b;
    transition: all 0.3s ease;

    &:hover {
      border-color: #64748b;
      background: #0f172a;
    }

    .upload-btn {
      padding: 0.75rem 1.5rem;
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;
      margin-bottom: 1rem;

      &:hover {
        transform: translateY(-2px);
      }
    }

    p {
      margin: 0.5rem 0;
      color: #cbd5e1;
    }

    small {
      display: block;
      color: #94a3b8;
      font-size: 0.85rem;
    }
  }

  .progress-bar {
    margin-top: 1rem;
    height: 8px;
    background: #1e293b;
    border-radius: 4px;
    overflow: hidden;
    position: relative;

    .progress {
      height: 100%;
      background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
      transition: width 0.3s ease;
    }

    span {
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 0.8rem;
      color: #94a3b8;
    }
  }
}

.documents-list {
  h2 {
    color: #e2e8f0;
    margin-bottom: 1rem;
  }

  .loading-state,
  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
  }

  .documents-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;

    .document-card {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      transition: all 0.3s ease;

      &:hover {
        border-color: #475569;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      }

      .document-icon {
        font-size: 2rem;
      }

      .document-info {
        flex: 1;

        h3 {
          margin: 0 0 0.25rem;
          color: #e2e8f0;
          font-size: 1rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        small {
          display: block;
          color: #94a3b8;
          font-size: 0.85rem;
        }

        .doc-date {
          margin-top: 0.25rem;
        }
      }

      .document-actions {
        display: flex;
        gap: 0.5rem;

        .action-btn {
          padding: 0.5rem;
          background: #475569;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.3s ease;

          &:hover {
            background: #64748b;
          }

          &.delete:hover {
            background: #991b1b;
          }
        }
      }
    }
  }
}
</style>
