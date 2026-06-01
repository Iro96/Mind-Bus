---
name: agent-orchestration
description: "Use when: implementing LangGraph agent nodes, building control flows, managing conversation state, routing between nodes, handling tool execution, or designing agent graphs"
keywords: ["langgraph", "agent", "node", "graph", "state", "orchestration", "control flow", "routing", "tools", "execution"]
---

# Agent Orchestration Skills

Advanced patterns for designing and implementing LangGraph-based agent systems.

## Core Concepts

### LangGraph Basics
- **Nodes**: Async functions that process state
- **Edges**: Connections between nodes defining flow
- **State**: Shared data structure passed between nodes
- **Conditional Edges**: Route to different nodes based on state
- **Checkpointing**: Persist state for recovery/threading

### Mind-Bus State Structure
```python
class AgentState:
    messages: List[Dict]           # Conversation history
    thread_id: UUID                # Conversation ID
    user_id: UUID                  # User context
    memory: List[Memory]           # Retrieved memories
    context: str                   # Current context window
    compressed: bool               # ACC applied flag
    tool_calls: List[Dict]        # Pending tool executions
    response: Optional[str]        # LLM response
```

## Node Implementation Patterns

### Retriever Node
Fetch context from memory and knowledge bases.

```python
async def retriever_node(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant context and memories."""
    
    last_msg = next(
        (m for m in reversed(state.messages) if m["role"] == "user"),
        None
    )
    if not last_msg:
        return {"memory": [], "context": ""}
    
    memories = await memory_manager.retrieve(
        query=last_msg["content"],
        user_id=state.user_id,
        limit=5,
        similarity_threshold=0.75
    )
    
    context = "\n".join([m["content"] for m in memories])
    
    return {"memory": memories, "context": context}
```

### Planner Node
Decide what actions to take.

```python
async def planner_node(state: AgentState) -> Dict[str, Any]:
    """Plan next actions based on context."""
    
    plan_prompt = f"""Given: {state.messages[-1]['content']}
    Context: {state.context}
    Decide: tool|retrieve|respond"""
    
    plan = await llm_client.generate(plan_prompt)
    
    return {
        "plan": plan,
        "messages": state.messages + [{"role": "planner", "content": plan}]
    }
```

### Tool Runner Node
Execute tools and collect results.

```python
async def tool_runner_node(state: AgentState) -> Dict[str, Any]:
    """Execute pending tool calls in parallel."""
    
    if not state.tool_calls:
        return {"tool_results": []}
    
    tasks = [
        get_tool(call["name"]).execute(**call["arguments"])
        for call in state.tool_calls
    ]
    
    results = await asyncio.gather(*tasks)
    
    new_messages = state.messages + [
        {"role": "tool", "tool": call["name"], "content": str(r)}
        for r, call in zip(results, state.tool_calls)
    ]
    
    return {"tool_results": results, "messages": new_messages}
```

### Responder Node
Generate final response.

```python
async def responder_node(state: AgentState) -> Dict[str, Any]:
    """Generate response to user."""
    
    response_prompt = f"""
    Context: {state.context}
    Memory: {[m['content'] for m in state.memory]}
    
    User: {state.messages[-1]['content']}
    
    Respond naturally.
    """
    
    response = await llm_client.generate(response_prompt)
    
    return {
        "response": response,
        "messages": state.messages + [{"role": "assistant", "content": response}]
    }
```

## Graph Design Patterns

### Sequential Flow
```python
from langgraph.graph import StateGraph

graph = StateGraph(AgentState)
graph.add_node("retriever", retriever_node)
graph.add_node("planner", planner_node)
graph.add_node("responder", responder_node)

graph.add_edge("retriever", "planner")
graph.add_edge("planner", "responder")
graph.add_edge("responder", "END")

graph.set_entry_point("retriever")
agent = graph.compile()
```

### Conditional Routing
```python
def route_decision(state: AgentState) -> str:
    """Route based on planner decision."""
    return "tool_runner" if "tool" in state.get("plan", "") else "responder"

graph.add_conditional_edges(
    "planner",
    route_decision,
    {"tool_runner": "tool_runner", "responder": "responder"}
)
graph.add_edge("tool_runner", "responder")
```

### Reflection Loop
```python
def should_reflect(state: AgentState) -> str:
    """Check if reflection needed."""
    return "reflect" if state.get("needs_improvement") else "END"

graph.add_node("reflector", reflector_node)
graph.add_conditional_edges(
    "responder",
    should_reflect,
    {"reflect": "reflector", "END": "END"}
)
graph.add_edge("reflector", "responder")  # Loop back
```

## Running the Agent

```python
# Create initial state
initial_state = AgentState(
    messages=[{"role": "user", "content": "Hello!"}],
    thread_id=uuid4(),
    user_id=user_id,
    memory=[],
    context="",
    compressed=False
)

# Run agent
result = agent.invoke(initial_state)

# Stream results
for step in agent.stream(initial_state):
    for node, value in step.items():
        print(f"{node}: {value}")
```

## Testing Patterns

```python
import pytest

@pytest.mark.asyncio
async def test_retriever_node():
    """Test retriever node."""
    state = AgentState(...)
    result = await retriever_node(state)
    assert "memory" in result
    assert "context" in result

@pytest.mark.asyncio
async def test_agent_flow():
    """Test full agent flow."""
    agent = build_test_agent()
    result = agent.invoke(initial_state)
    assert result["response"] is not None
```

## References

- **LangGraph**: https://langgraph.js.org
- **Graph**: `agent/graph.py`
- **Nodes**: `agent/nodes/`
- **State**: `agent/state/state.py`
