# Mind-Bus Skills Documentation

## Overview

This directory contains **reusable development skills** for the Mind-Bus AI Agent platform. These skills encapsulate domain knowledge, design patterns, and best practices to accelerate development across all modules.

## 📚 Skills Directory

```
.agents/skills/
├── mindbus-skill/                 # Master expert skill for Mind-Bus
├── agent-orchestration/           # LangGraph node and graph patterns
├── memory-system/                 # Memory extraction, storage, retrieval
├── rag-retrieval/                 # RAG/CAG retrieval and semantic search
├── backend-api/                   # FastAPI routes, services, schemas
├── frontend-components/           # Vue 3 components, stores, routing
├── SKILLS-INDEX.md               # Central index and workflow guide
└── README.md                      # This file
```

## 🚀 Quick Start

### For Agent Development
Use the **agent-orchestration** skill when:
- Building new LangGraph nodes
- Designing agent control flows
- Implementing tool execution
- Managing conversation state

### For Memory Features
Use the **memory-system** skill when:
- Extracting memories from conversations
- Storing episodic/semantic/correction memories
- Retrieving context for the agent
- Implementing memory scoring

### For Retrieval Systems
Use the **rag-retrieval** skill when:
- Implementing semantic search
- Building hybrid RAG+CAG retrieval
- Chunking and storing documents
- Ranking search results

### For API Development
Use the **backend-api** skill when:
- Creating FastAPI endpoints
- Designing request/response schemas
- Implementing services and business logic
- Adding authentication and authorization

### For Frontend Development
Use the **frontend-components** skill when:
- Building Vue 3 components
- Managing state with Pinia
- Adding routes and navigation
- Creating forms and handling user input

## 📖 How to Use These Skills

### Option 1: In Chat
Type `/mindbus-expert` or any specific skill name in GitHub Copilot Chat to invoke the skill with its full knowledge base.

### Option 2: Direct Reference
Open the relevant `SKILL.md` file in the skill directory for quick pattern lookups.

### Option 3: Guided Navigation
Start with `SKILLS-INDEX.md` to:
- Understand which skill to use
- See the development workflow
- Find related skills
- Check quick references

## 🎯 Typical Development Workflows

### Building a Complete Feature (End-to-End)

```
1. Plan with agent-orchestration
   ↓
2. Implement with backend-api
   ↓
3. Add retrieval with rag-retrieval (if needed)
   ↓
4. Use memory-system (if using memories)
   ↓
5. Build UI with frontend-components
```

### Adding Memory to Agent

```
1. memory-system: Design memory types
   ↓
2. agent-orchestration: Add extraction node
   ↓
3. memory-system: Implement storage
   ↓
4. rag-retrieval: Integrate retrieval
   ↓
5. frontend-components: Build UI
```

### Implementing RAG Search

```
1. rag-retrieval: Plan retrieval strategy
   ↓
2. backend-api: Create search endpoint
   ↓
3. frontend-components: Build search UI
```

## 📝 Skill File Structure

Each skill contains:

```markdown
---
name: skill-name
description: "Use when: specific use cases"
keywords: [list, of, keywords]
---

# Skill Title

## Quick Start
- Basic examples and setup

## Core Patterns
- Implementation patterns
- Common approaches

## Examples
- Concrete code examples
- Copy-paste ready

## Testing
- Testing patterns
- Test examples

## Common Mistakes
- What to avoid
- Best practices

## References
- Links to related code
- Documentation
```

## 🔗 Key Integration Points

### Agent System (`agent/`)
- **agent-orchestration** - Node design and graph flows
- **memory-system** - Memory extraction in nodes
- **rag-retrieval** - Retrieval nodes

### Memory System (`memory/`)
- **memory-system** - All memory operations
- **backend-api** - Memory endpoints
- **frontend-components** - Memory UI

### Retrieval System (`agent/retrieval/`)
- **rag-retrieval** - Core retrieval patterns
- **agent-orchestration** - Retrieval nodes
- **backend-api** - Search endpoints

### API (`apps/api/`)
- **backend-api** - All API patterns
- **agent-orchestration** - Agent endpoints
- **memory-system** - Memory endpoints
- **rag-retrieval** - Search endpoints

### Frontend (`frontend/`)
- **frontend-components** - All UI patterns
- **backend-api** - API service integration

## 💡 When to Create New Skills

Create a new skill when:
- ✅ A significant module or feature area needs documentation
- ✅ Multiple developers work on the same area
- ✅ Complex patterns emerge across multiple files
- ✅ The knowledge is reusable across projects

Don't create new skills when:
- ❌ It's a one-time or very specific implementation
- ❌ It's already well-documented in code comments
- ❌ It belongs in an existing skill

## 🔍 Finding the Right Skill

Use this decision tree:

```
I'm working on...

├─ Agent nodes or flows? → agent-orchestration
├─ Memory extraction/storage? → memory-system
├─ Semantic search or RAG? → rag-retrieval
├─ API endpoints/services? → backend-api
├─ Vue components/stores? → frontend-components
├─ General architecture? → mindbus-expert
└─ Not sure? → Start with SKILLS-INDEX.md
```

## 📚 Cross-Skill References

### agent-orchestration
- Uses: **memory-system** (in retriever nodes)
- Uses: **rag-retrieval** (in retriever nodes)
- Used by: **backend-api** (agent endpoints)
- Used by: **frontend-components** (chat UI)

### memory-system
- Uses: **rag-retrieval** (vector storage)
- Used by: **agent-orchestration** (memory nodes)
- Used by: **backend-api** (memory endpoints)
- Used by: **frontend-components** (memory UI)

### rag-retrieval
- Uses: **memory-system** (memory vector storage)
- Used by: **agent-orchestration** (retriever nodes)
- Used by: **backend-api** (search endpoints)
- Used by: **frontend-components** (search UI)

### backend-api
- Uses: **agent-orchestration** (agent endpoints)
- Uses: **memory-system** (memory endpoints)
- Uses: **rag-retrieval** (search endpoints)
- Used by: **frontend-components** (API calls)

### frontend-components
- Uses: **backend-api** (API integration)
- Used by: **mindbus-expert** (overview)

## 🛠️ Maintaining These Skills

When updating Mind-Bus code:

1. **If you change patterns**: Update the relevant skill
2. **If you add a new module**: Consider creating a skill
3. **If you find a bug in a pattern**: Fix it in the skill
4. **If patterns change**: Update all cross-references

### Updating a Skill

1. Edit the `SKILL.md` file
2. Update patterns, examples, and references
3. Test examples are still valid
4. Update cross-references in other skills
5. Update `SKILLS-INDEX.md` if needed

## 📖 Learning Path for New Developers

### Week 1: Foundations
1. Read `mindbus-expert` for overview
2. Read `SKILLS-INDEX.md` for architecture
3. Run `docker-compose up` locally

### Week 2: Core Modules
1. **agent-orchestration** - Understand agent flows
2. **memory-system** - Understand memory architecture
3. **rag-retrieval** - Understand retrieval patterns

### Week 3: Implementation
1. **backend-api** - Build simple endpoint
2. **frontend-components** - Build simple component
3. Work on a small task using multiple skills

### Week 4+: Deep Work
- Pick a module and become expert
- Contribute to improvements
- Update skills with learnings

## 🤝 Contributing Improvements

Found better patterns? Want to document edge cases?

1. Create a PR with skill improvements
2. Reference the relevant code
3. Include concrete examples
4. Test examples before submitting
5. Update related skills if needed

## 📞 Getting Help

- **Stuck on agent logic?** Check `agent-orchestration`
- **Memory questions?** Check `memory-system`
- **Search problems?** Check `rag-retrieval`
- **API issues?** Check `backend-api`
- **UI problems?** Check `frontend-components`
- **Architecture questions?** Check `mindbus-expert` or `SKILLS-INDEX.md`

## 🎓 Related Documentation

- **Code**: See inline comments in relevant modules
- **Tests**: See `tests/` directory for patterns
- **Docs**: See `docs/` directory for detailed guides
- **Examples**: See example files and patterns in each module

## Version Info

- **Last Updated**: June 2026
- **Mind-Bus Version**: Main branch
- **Python**: 3.10+
- **Vue**: 3.x
- **FastAPI**: Latest

## License

These skills are part of the Mind-Bus project and follow the same license (check LICENSE file in repo root).
