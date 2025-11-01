"""Explore the assistants defined in langgraph.json.

This script demonstrates how to:
1. Use assistant IDs vs graph IDs
2. Compare the two assistants
3. Show their execution flow differences
"""
from langgraph_sdk import get_sync_client


def list_assistants():
    """Print information about available assistants."""
    print("=" * 60)
    print("ASSISTANTS DEFINED IN langgraph.json")
    print("=" * 60)
    print()
    print("1. Assistant ID: 'agent'")
    print("   - Graph ID: 'simple_agent'")
    print("   - Description: Tool-using agent with conditional tool-calling")
    print("   - Flow: Agent → [Tools] → Done")
    print()
    print("2. Assistant ID: 'agent_helpful'")
    print("   - Graph ID: 'agent_with_helpfulness'")
    print("   - Description: Agent with helpfulness check node and loop limit")
    print("   - Flow: Agent → [Tools] → Helpfulness Check → [Loop if needed] → Done")
    print()
    print("=" * 60)
    print()


def test_assistant(assistant_or_graph_id: str, query: str):
    """Test an assistant or graph by ID."""
    print(f"\n{'='*60}")
    print(f"TESTING: {assistant_or_graph_id}")
    print(f"QUERY: {query}")
    print(f"{'='*60}\n")
    
    client = get_sync_client(url="http://localhost:2024")
    
    nodes_visited = []
    for chunk in client.runs.stream(
        None,  # Threadless run
        assistant_or_graph_id,
        input={
            "messages": [
                {
                    "role": "human",
                    "content": query,
                }
            ]
        },
        stream_mode="updates",
    ):
        if chunk.event == "updates" and chunk.data:
            for node_name in chunk.data.keys():
                if node_name not in nodes_visited:
                    nodes_visited.append(node_name)
                    print(f"  → Node executed: {node_name}")
    
    print(f"\n✓ Execution complete. Nodes visited: {', '.join(nodes_visited)}")
    print()


def main():
    """Main function to explore assistants."""
    list_assistants()
    
    print("\nNOTE: You can use either:")
    print("  - Graph IDs directly: 'simple_agent' or 'agent_with_helpfulness'")
    print("  - Assistant IDs: The SDK may require graph IDs for streaming")
    print()
    
    query = "What is Python?"
    
    # Test simple_agent (via graph ID)
    print("\n" + "="*60)
    print("COMPARISON: Testing both assistants with the same query")
    print("="*60)
    
    test_assistant("simple_agent", query)
    
    test_assistant("agent_with_helpfulness", query)
    
    print("\n" + "="*60)
    print("KEY DIFFERENCES OBSERVED:")
    print("="*60)
    print("- simple_agent: Only 'agent' and 'action' nodes")
    print("- agent_with_helpfulness: Includes 'agent', 'action', AND 'helpfulness' nodes")
    print("="*60)


if __name__ == "__main__":
    main()

