# AGENT.md - Mind-Bus AI Agent System

This document describes the Mind-Bus AI Agent - its architecture, capabilities, learning mechanisms, and deployment patterns.

## Agent Overview

The Mind-Bus Agent is a **persistent, multi-modal AI system** designed to:

- Maintain continuous memory across conversations
- Learn and improve from experience
- Execute complex tasks through tool integration
- Adapt its behavior based on user feedback
- Compress context for long-term conversations

## Core Architecture

### Agent Execution Graph (LangGraph)

The agent uses a state machine-based execution model:

```bash
Entry
  ↓
[Retrieve] → Fetch relevant memories and documents
  ↓
[Plan] → Decide which actions to take
  ↓
[Execute] → Run tools and gather results
  ↓
[Respond] → Generate response based on results
  ↓
[Reflect] → Extract memories and learn
  ↓
[Compress] → Apply Adaptive Context Compression
  ↓
[Return] → Send response to user
```

### State Structure

```typescript
AgentState {
  messages: List[Dict]        // Conversation history
  thread_id: UUID            // Conversation ID
  user_id: UUID              // User context
  memory: List[Memory]       // Retrieved memories
  context: str               // Current context window
  planning: Dict             // Action plan
  execution_results: Dict    // Tool execution results
  compressed: bool           // ACC applied flag
  metadata: Dict             // Additional state
}
```

## Memory System

### Three-Tier Memory Architecture

#### 1. Short-Term (Conversation Buffer)

- Current conversation history
- Recent context (5-10 messages)
- Immediate task state
- Lives in memory during session

#### 2. Mid-Term (Episodic Memory)

- Specific events and conversations
- Important interactions
- User preferences learned
- Stored in PostgreSQL

- Retrieved via vector similarity

#### 3. Long-Term (Semantic Memory)

- General facts and knowledge
- Extracted patterns
- Persistent insights
- Indexed in Qdrant vectors
- Used for knowledge-based reasoning

### Memory Extraction

After each interaction, the agent extracts memories:

```python
extracted_memories = memory_extractor.extract(
    conversation=conversation_context,
    extraction_type=['episodic', 'semantic', 'correction']
)
```

#### Memory Types

1. **Episodic**
   - What happened and when
   - Specific to this conversation
   - Time-bound and contextual
   - Example: "User asked about Python debugging"

2. **Semantic**
   - General knowledge from conversation
   - Extracted facts and relationships
   - Context-independent
   - Example: "User is a software engineer"

3. **Correction**
   - Errors the agent made
   - User corrections
   - Improvement feedback
   - Example: "Agent was wrong about X, correct answer is Y"

## Learning System

### Self-Correction Mechanism

1. **Error Detection**
   - User feedback marked as negative
   - Explicit corrections provided
   - System-detected inconsistencies

2. **Memory Recording**
   - Store correction as memory
   - Mark original memory as deprecated
   - Increase confidence in correction

3. **Behavior Update**
   - Future retrieval prioritizes corrections
   - Weights adjusted for relevant domains
   - Prevents repeated mistakes

### Feedback Loop

```bash
User Interaction
      ↓
Agent Response
      ↓
User Feedback (Good/Bad)
      ↓
Extract Learning
      ↓
Update Memory
      ↓
Future Interactions Improved
```

## Tool System

### Available Tools

1. **Web Search**
   - Query the internet for information
   - Parse and summarize results
   - Multiple source support

2. **Calculator**
   - Mathematical computations
   - Complex expressions
   - Symbolic math

3. **File Operations**
   - Read/write local files
   - Directory navigation
   - Batch processing

4. **Database Query**
   - Execute SQL queries
   - Access structured data
   - Transaction support

5. **API Integration**
   - Call external APIs
   - Parse responses
   - Authentication support

### Tool Execution Pattern

```python
class ToolRunner:
    async def execute(self, tool_name: str, **params):
        tool = self.get_tool(tool_name)
        
        # Validate parameters
        validated = tool.validate(**params)
        
        # Execute with timeout
        result = await asyncio.wait_for(
            tool.execute(**validated),
            timeout=30.0
        )
        
        return {
            'tool': tool_name,
            'result': result,
            'timestamp': now(),
            'metadata': {...}
        }
```

## Adaptive Context Compression (ACC)

### Problem

- Token limits in LLMs
- Performance degradation with long contexts
- Memory constraints

### Solution: ACC

```bash
Original Conversation (5000 tokens)
      ↓
[Compression Algorithm]
      ↓
Compressed Summary (500 tokens)
      + Essential Markers
      + Semantic Anchors
      ↓
Augmented Context (2000 tokens)
```

### Compression Strategy

1. **Summarization**
   - Extract key points from messages
   - Preserve semantic meaning
   - Reduce redundancy

2. **Selective Keeping**
   - Keep recent messages in full
   - Compress older messages
   - Mark important boundaries

3. **Semantic Anchors**
   - Preserve references to important topics
   - Maintain conversation flow
   - Enable later expansion if needed

## Retrieval System

### Hybrid RAG+CAG Approach

#### RAG (Retrieval Augmented Generation)

```python
# Vector similarity search
memories = vector_db.search(
    query_embedding=embed(user_message),
    top_k=5,
    filter={'user_id': current_user}
)

# Rerank by relevance
ranked = rerank(memories, user_message)

# Format for LLM
context = format_memories(ranked)
```

#### CAG (Cached Augmented Generation)

```python
cache_key = hash(user_message, conversation_context)

if cache_key in redis_cache:
    return cached_response  # Fast path
else:
    response = generate_response()
    cache.set(cache_key, response, ttl=3600)
    return response
```

### Retrieval Decision Tree

```bash
User Message Received
      ↓
Check Cache (CAG)
      ├─ Cache Hit → Return cached response
      └─ Cache Miss ↓
         Query Vector DB (RAG)
         Get Top 5 Similar Memories
         Check Relevance Threshold
         ├─ High Relevance → Use full context
         ├─ Medium Relevance → Use selective context
         └─ Low Relevance → Use base prompt only
         Generate Response
         Cache for Future Use
```

## Conversation Management

### Thread Lifecycle

1. **Creation**
   - First message creates thread
   - Title inferred from first message
   - User associated with thread

2. **Active**
   - Messages accumulate
   - Memories extracted
   - Context managed

3. **Archive**
   - Marked as completed
   - Data persisted
   - Still retrievable

### Message Handling

```python
def process_message(thread_id, user_id, content):
    # Create message entry
    message = Message(
        thread_id=thread_id,
        user_id=user_id,
        role='user',
        content=content
    )
    
    # Build agent state
    state = build_state(thread_id, user_id)
    
    # Execute agent graph
    result = agent_graph.invoke(state)
    
    # Store response
    response_msg = Message(
        thread_id=thread_id,
        role='assistant',
        content=result['response']
    )
    
    # Extract and store memories
    memories = memory_extractor.extract(result)
    memory_manager.save(memories)
    
    return response_msg
```

## Observability & Monitoring

### Logging

Every agent action is logged with:

- Request ID for tracing
- Timestamp
- User ID
- Action name
- Duration
- Results/Errors

```python
logger.info(
    "Agent action",
    extra={
        'request_id': request_id,
        'action': 'tool_execution',
        'tool': 'web_search',
        'duration_ms': elapsed_ms,
        'success': True
    }
)
```

### Metrics

- **Latency**: Time per agent step
- **Cache Hit Rate**: CAG effectiveness
- **Tool Success Rate**: Tool reliability
- **Memory Quality**: Relevance of retrieved memories
- **User Satisfaction**: From feedback signals

### Tracing

```bash
request_id: abc-123
  ├─ retrieve (150ms)
  │   ├─ vector_search (80ms)
  │   └─ rerank (70ms)
  ├─ plan (200ms)
  ├─ execute (500ms)
  │   ├─ web_search (350ms)
  │   └─ parse_results (150ms)
  ├─ respond (300ms)
  ├─ reflect (100ms)
  └─ compress (50ms)
  
Total: 1300ms
```

## Performance Optimization

### Speed

1. **Early Exit** - Return cached responses immediately
2. **Parallel Execution** - Run independent tools concurrently
3. **Lazy Loading** - Load memories only when needed
4. **Index Optimization** - Vector DB tuning for speed

### Quality

1. **Memory Relevance** - Better retrieval = better answers
2. **Tool Accuracy** - Validate tool outputs
3. **Feedback Loop** - Learn from corrections
4. **Context Management** - Compress wisely

### Resource Usage

1. **Token Optimization** - Use compression
2. **Storage** - Archive old conversations

3. **Caching** - Reduce redundant computation
4. **Batching** - Process multiple requests together

## Security & Safety

### User Isolation

- All queries scoped by user_id
- Memories kept separate
- Cross-user contamination prevented

### Tool Safety

- Timeout limits on tool execution
- Sandboxed execution environment
- Rate limiting on API calls
- Input validation for all parameters

### Content Safety

- Filter potentially harmful requests
- Log sensitive operations
- Audit trail for compliance
- Rollback capability for errors

## Configuration

### Environment Variables

```env
# Agent
AGENT_MODEL=gpt-4
AGENT_TEMPERATURE=0.7
CONTEXT_WINDOW_SIZE=8000
MAX_TOOL_TIMEOUT=30

# Memory
MEMORY_BATCH_SIZE=5
MEMORY_EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_DIMENSION=384

# Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=10000

# Compression
COMPRESSION_THRESHOLD=0.8
COMPRESSION_RATIO_TARGET=0.1
```

### Model Configuration

```python
agent_config = {
    'model': 'gpt-4',
    'temperature': 0.7,
    'max_tokens': 2000,
    'top_p': 0.95,

    'frequency_penalty': 0.1,
    'presence_penalty': 0.0,
    'system_prompt': SYSTEM_PROMPT
}
```

## Deployment Patterns

### Local Development

```bash
docker-compose up --build
# Agent runs in-process with API
```

### Single Server

```js
┌─────────────────────────────────┐
│     Single Server               │
│  ┌─────────────────────────┐   │

│  │  API + Agent (FastAPI)  │   │
│  │  + Memory (Agent Graph) │   │
│  └──────────────┬──────────┘   │
│  ┌──────────────┼──────────┐   │
│  │ PostgreSQL   │  Redis   │   │
│  │ Qdrant       │  RQ      │   │
│  └──────────────┴──────────┘   │
└─────────────────────────────────┘
```

### Scaled Architecture

```js
┌──────────────────────────────────────────┐
│           Load Balancer                  │
└────────────────┬─────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ↓            ↓            ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│ API 1   │  │ API 2   │  │ API 3   │
│ Agent 1 │  │ Agent 2 │  │ Agent 3 │
└────┬────┘  └────┬────┘  └────┬────┘

     │            │            │
     └────────────┼────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ↓            ↓            ↓

  PostgreSQL    Redis       Qdrant
```

## Troubleshooting

### Agent Not Responding

1. Check logs for errors
2. Verify model API credentials
3. Check context window size
4. Verify thread exists

### Memory Issues

1. Check vector DB connection
2. Verify embeddings are being stored
3. Check retrieval relevance
4. Clear old memories if needed

### Tool Failures

1. Check tool configuration
2. Verify tool dependencies
3. Check timeout settings
4. Review error logs

### Performance Degradation

1. Monitor memory retrieval latency
2. Check cache hit rates

3. Review compression ratios
4. Profile tool execution times

## Future Enhancements

1. **Multi-Modal Input** - Images, audio, video
2. **Advanced Planning** - STRIPS, HTN planning

3. **Collaborative Agents** - Multi-agent coordination
4. **Custom Models** - Fine-tuning on user data
5. **Advanced Safety** - Constitutional AI principles
6. **Skill Learning** - Learn new tool combinations
7. **Personalization** - User-specific models

## Best Practices

### For Developers

1. Always log with request_id for tracing
2. Use dependency injection for services
3. Write tests for new tools
4. Monitor agent latency
5. Document tool parameters

### For Users

1. Provide feedback to improve agent
2. Use threads for context
3. Manage document uploads for better RAG
4. Review and correct memories
5. Monitor tool usage

## Conclusion

The Mind-Bus Agent is a sophisticated system combining:

- **Persistent Memory** - Never forgets important information
- **Continuous Learning** - Improves from feedback
- **Tool Integration** - Extends capabilities
- **Context Awareness** - Understands conversation history
- **Optimized Execution** - Fast and efficient

This architecture enables building truly intelligent, long-term AI systems that learn and improve over time.
