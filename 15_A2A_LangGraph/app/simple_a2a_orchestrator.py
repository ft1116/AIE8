"""Simple LangGraph orchestrator that uses A2A protocol to call agent server.

This is Activity #1: A simple LangGraph graph that uses the A2A protocol
to communicate with the agent server running on localhost:10000.
"""
import asyncio
import logging

from app.a2a_client_graph import A2AClientGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Simple example of using LangGraph to orchestrate A2A protocol calls."""
    print("=" * 70)
    print("🚀 Simple LangGraph A2A Orchestrator")
    print("=" * 70)
    print("\nThis demonstrates Activity #1:")
    print("A LangGraph graph that uses A2A protocol to call the agent server.\n")
    
    # Initialize the client graph
    client_graph = A2AClientGraph(base_url="http://localhost:10000")
    
    try:
        # Example query
        user_query = input("\nEnter your query (or press Enter for default): ").strip()
        if not user_query:
            user_query = "What are the latest AI developments in 2025?"
            print(f"Using default query: {user_query}")
        
        print(f"\n📤 Sending query to agent via A2A protocol...")
        print("-" * 70)
        
        # Invoke the graph
        result = await client_graph.invoke(user_query)
        
        print(f"\n📥 Response from agent:\n")
        print(result['agent_response'])
        print("\n" + "=" * 70)
        print("✅ Query completed successfully!")
        print("=" * 70)
        
        # Show agent card info
        if result.get('agent_card'):
            card = result['agent_card']
            print(f"\n🤖 Agent Information:")
            print(f"   Name: {card.name}")
            print(f"   Description: {card.description}")
            print(f"   Skills: {len(card.skills)} available")
            for skill in card.skills:
                print(f"     - {skill.name}: {skill.description}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await client_graph.close()


if __name__ == "__main__":
    asyncio.run(main())


