"""Test script for A2A client graph - demonstrates using LangGraph to call agent via A2A protocol."""
import asyncio
import logging

from app.a2a_client_graph import A2AClientGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Test the A2A client graph."""
    print("=" * 60)
    print("🧪 Testing A2A Client Graph")
    print("=" * 60)
    
    # Initialize the client graph
    client_graph = A2AClientGraph(base_url="http://localhost:10000")
    
    try:
        # Test 1: Simple query
        print("\n📋 Test 1: Simple Query")
        print("-" * 60)
        query1 = "What are the latest developments in AI in 2025?"
        print(f"Query: {query1}\n")
        
        result1 = await client_graph.invoke(query1)
        print(f"Response: {result1['agent_response']}\n")
        
        # Test 2: Academic paper search
        print("\n📋 Test 2: Academic Paper Search")
        print("-" * 60)
        query2 = "Find me recent papers on transformer architectures"
        print(f"Query: {query2}\n")
        
        result2 = await client_graph.invoke(query2)
        print(f"Response: {result2['agent_response']}\n")
        
        # Test 3: Streaming
        print("\n📋 Test 3: Streaming Response")
        print("-" * 60)
        query3 = "What is LangGraph?"
        print(f"Query: {query3}\n")
        print("Streaming response:")
        
        async for state in client_graph.stream(query3):
            for node_name, node_state in state.items():
                if "agent_response" in node_state and node_state["agent_response"]:
                    print(f"  {node_name}: {node_state['agent_response'][:100]}...")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
    
    finally:
        await client_graph.close()


if __name__ == "__main__":
    asyncio.run(main())

