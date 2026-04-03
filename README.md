![demo\_chat](https://dummyimage.com/1000x400/0f172a/ffffff\&text=Mind-Bus+AI+Agent+Demo)

<div align="center">
  
[![Docker Image CI](https://github.com/Iro96/Mind-Bus/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Iro96/Mind-Bus/actions/workflows/docker-image.yml)

</div>

---

* Meet **Mind-Bus** — a persistent AI agent platform with memory, RAG/CAG, and Adaptive Context Compression (ACC).
* Designed for long-term intelligent systems that remember, retrieve, and self-improve.
* Production-ready architecture with modular agent orchestration and scalable deployment.

---

## Overview

**Mind-Bus** is a persistent AI agent platform designed to operate in long-term contexts, learn continuously, and integrate modern AI technologies in a production-ready environment.

It scales from a local AI assistant to a full enterprise-grade intelligent system.

* Persistent AI agent with long-term and short-term memory
* Hybrid **RAG + CAG** knowledge retrieval system
* **Adaptive Context Compression (ACC)** for long conversations
* Self-correcting learning from user feedback and system failures
* Modular agent orchestration and tool integration
* Supports local and cloud LLMs
* Scalable production deployment
* Fully open-source and self-hostable
* Built for modern AI infrastructure and future integrations

Mind-Bus is designed to function as a **long-term intelligent system rather than a temporary chatbot**.

---

## See it in action

Live demo coming soon.

---

## Full Feature List

* Persistent conversational AI agent
* Long-term semantic memory
* Episodic and correction memory
* Hybrid RAG knowledge retrieval
* CAG cached context system
* Adaptive Context Compression (ACC)
* Autonomous task execution
* Tool integration (web, files, APIs, databases)
* Self-correcting learning system
* Feedback-driven improvements
* Modular architecture
* Production deployment support
* Monitoring and observability
* Security and audit logging

More detailed documentation coming soon.

---

## Self-Host

You can run Mind-Bus locally or on your own infrastructure.

### Requirements

* Python 3.10+
* Docker
* Postgres
* Redis
* Qdrant
### Quick Start

```bash
git clone https://github.com/Iro96/Mind-Bus.git
cd Mind-Bus
docker-compose up --build
```

Then open:

```
http://localhost:8000
```

Full setup guide will be available in the documentation.

---

## Architecture

Mind-Bus is built using a modular AI agent architecture.

Core components:

* API Server (FastAPI)
* Agent Orchestrator (LangGraph)
* Memory System
* Retrieval System (Qdrant)
* Adaptive Context Compression (ACC)
* Worker Pipeline
* Self-learning Reflection Engine
* Deployment Infrastructure

The system is designed for scalability, reliability, and long-term learning.

---

## Enterprise

Mind-Bus can be deployed as:

* Local AI system
* Private cloud agent
* Enterprise knowledge platform
* Autonomous AI infrastructure
* Hybrid cloud AI system

Enterprise features may include:

* team memory
* secure deployments
* private model hosting
* monitoring dashboards
* access control
* multi-agent orchestration

More information coming soon.

---

## Frequently Asked Questions (FAQ)

### Q: Can I run Mind-Bus locally?

Yes. Mind-Bus is fully self-hostable and can run on your local machine or server.

### Q: Does Mind-Bus require a GPU?

No. It can run with API-based LLMs or local CPU models. GPU is optional for local models.

### Q: What models does Mind-Bus support?

Mind-Bus is model-agnostic and supports:

* local LLMs
* cloud LLMs
* open-source models
* custom AI models

### Q: Can Mind-Bus learn from user feedback?

Yes. The system includes a self-correcting memory and reflection pipeline that allows continuous improvement while maintaining safety and auditability.

---

## Contributors

<a href="https://github.com/Iro96/Mind-Bus/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Iro96/Mind-Bus" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

---

### Interested in Contributing?

Mind-Bus is open source and community-driven.

* Build a next-generation AI agent platform
* Work with modern AI technologies
* Gain experience in large-scale AI systems
* Help shape the future of persistent AI

You can help by:

* building new features
* improving architecture
* writing documentation
* fixing bugs
* suggesting ideas

Good first issues and contribution guidelines will be added soon.

---

## Roadmap

* Core agent system
* Memory architecture
* RAG + CAG integration
* ACC context compression
* Self-learning system
* Deployment infrastructure
* Monitoring and evaluation
* Multi-agent support
* Enterprise features
