-- Initial schema migration for AI Agent Platform
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT,
    auth_provider_id TEXT,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ
);

-- Create threads table
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    title TEXT,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool', 'system')),
    content TEXT,
    token_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Create checkpoints table
CREATE TABLE checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    state_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER NOT NULL,
    checksum VARCHAR(255)
);

-- Create memories table
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('episodic', 'semantic', 'correction')),
    key TEXT NOT NULL,
    value_json JSONB,
    confidence REAL,
    source_type VARCHAR(50),
    source_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL
);

-- Create memory_edges table
CREATE TABLE memory_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_memory_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    to_memory_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL,
    weight REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_uri TEXT NOT NULL,
    title TEXT,
    mime_type VARCHAR(255),
    checksum VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create document_chunks table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT,
    token_count INTEGER,
    embedding_id UUID,
    metadata JSONB
);

-- Create retrieval_logs table
CREATE TABLE retrieval_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    query_text TEXT,
    retrieved_ids JSONB,
    scores JSONB,
    method VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create feedback_events table
CREATE TABLE feedback_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    feedback_text TEXT,
    severity VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Create reflection_jobs table
CREATE TABLE reflection_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_event_id UUID NOT NULL REFERENCES feedback_events(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    input_json JSONB,
    output_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create tool_calls table
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    input_json JSONB,
    output_json JSONB,
    status VARCHAR(50) NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create audit_logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_type VARCHAR(50) NOT NULL,
    actor_id UUID NOT NULL,
    action VARCHAR(255) NOT NULL,
    target_type VARCHAR(50),
    target_id UUID,
    request_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Indexes
-- (thread_id, created_at) on messages
CREATE INDEX idx_messages_thread_created ON messages (thread_id, created_at);

-- (user_id, memory_type) on memories
CREATE INDEX idx_memories_user_type ON memories (user_id, memory_type);

-- GIN on JSONB metadata fields
CREATE INDEX idx_messages_metadata ON messages USING GIN (metadata);
CREATE INDEX idx_document_chunks_metadata ON document_chunks USING GIN (metadata);
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING GIN (metadata);

-- (document_id, chunk_index) on document_chunks
CREATE INDEX idx_document_chunks_doc_index ON document_chunks (document_id, chunk_index);

-- Partial index on expires_at
CREATE INDEX idx_memories_expires_at ON memories (expires_at) WHERE expires_at IS NOT NULL;

-- Full-text indexes (if needed)
CREATE INDEX idx_messages_content_fts ON messages USING GIN (to_tsvector('english', content));
CREATE INDEX idx_documents_title_fts ON documents USING GIN (to_tsvector('english', title));
CREATE INDEX idx_memories_key_fts ON memories USING GIN (to_tsvector('english', key));