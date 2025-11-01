# Exploring Assistants in LangGraph Platform

## Overview

Your `langgraph.json` defines **2 assistants** that map to **2 graphs**:

### Mapping

| Assistant ID | Graph ID | Description |
|--------------|----------|-------------|
| `agent` | `simple_agent` | Tool-using agent with conditional tool-calling |
| `agent_helpful` | `agent_with_helpfulness` | Agent with helpfulness check node and loop limit |

## How to Explore Assistants

### Method 1: Direct Graph IDs (Recommended)

You can call graphs directly using their graph IDs:

```python
from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")

# Use graph ID directly
for chunk in client.runs.stream(
    None,
    "simple_agent",  # Graph ID
    input={"messages": [{"role": "human", "content": "Hello!"}]},
    stream_mode="updates",
):
    print(chunk.data)
```

### Method 2: Assistant IDs

Assistant IDs (`agent`, `agent_helpful`) are configured in `langgraph.json` for the LangGraph Platform UI, but for direct SDK calls, you typically use the graph IDs.

## Execution Flow Differences

### `simple_agent` Flow:
```
Entry → agent → [has tool calls?] → action (tools) → agent → Done
```

**Nodes:** `agent`, `action`

### `agent_with_helpfulness` Flow:
```
Entry → agent → [has tool calls?] → action (tools) → agent → helpfulness → [helpful?] → Done or Loop back
```

**Nodes:** `agent`, `action`, `helpfulness`

## Test Scripts

1. **`test_served_graph.py`** - Tests `simple_agent`
2. **`test_agent_helpful.py`** - Tests `agent_with_helpfulness`
3. **`explore_assistants.py`** - Compares both assistants side-by-side

## Running Examples

```bash
# Test simple agent
uv run python test_served_graph.py

# Test agent with helpfulness check
uv run python test_agent_helpful.py

# Compare both assistants
uv run python explore_assistants.py
```

## Key Differences

1. **simple_agent**: Simple tool-calling loop - agent calls tools until satisfied, then ends.

2. **agent_with_helpfulness**: Adds a quality control loop - after the agent responds, a helpfulness evaluator checks if the response is helpful:
   - If helpful (`HELPFULNESS:Y`) → Ends
   - If not helpful (`HELPFULNESS:N`) → Loops back to agent
   - Has a safety limit (10 messages) to prevent infinite loops

## Visual Exploration

You can also explore assistants visually using **LangGraph Studio**:
1. Make sure the server is running: `uv run langgraph dev`
2. Open: https://smith.langchain.com/studio?baseUrl=http://localhost:2024
3. Select an assistant and watch the execution flow in real-time

