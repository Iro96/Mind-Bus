# Mind-Bus Overview

## What is Mind-Bus?

Mind-Bus is a persistent AI agent platform built for long-term conversational intelligence, memory, and autonomous task execution. It combines a modular agent orchestration layer with memory storage, retrieval, tool integration, and a FastAPI-based API server.

## Core goals

- Persistent AI conversations with long-term memory
- Hybrid retrieval using knowledge graphs and vector search
- Adaptive context compression for long-running dialogues
- Modular architecture for tools, agents, and workflows
- Self-learning feedback and reflection pipelines
- Production-ready deployment using Docker and standard services

## Key components

- `apps/api` — FastAPI backend and HTTP interface
- `agent` — agent orchestration graph and node definitions
- `memory` — long-term and short-term memory storage logic
- `retrieval` — document ingestion, chunking, and vector search support
- `worker` — background jobs and reflection pipelines
- `storage` — Postgres database access layer
- `deploy` — Docker Compose deployment definition

## Why this project exists

The platform is intended to act as more than a simple chatbot. It is a persistent, self-aware agent environment that can remember, reason, execute tasks, and improve over time.

## What makes it special

- Modular agent graph using `langgraph`
- Persistence through Postgres and Qdrant
- Background workers for reflection and analytics
- Interface-ready backend with FastAPI
- Designed for extensibility across frontend and backend
