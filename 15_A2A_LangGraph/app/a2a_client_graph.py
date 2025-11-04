"""LangGraph client that uses A2A protocol to communicate with agent server.

This creates a simple LangGraph orchestrator that wraps A2A client calls,
allowing you to use the agent server as a node in a LangGraph workflow.
"""
from __future__ import annotations

import logging
from typing import Annotated, Any, Dict, List, TypedDict
from uuid import uuid4

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph, add_messages
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AClientState(TypedDict):
    """State for A2A client graph."""
    messages: Annotated[List, add_messages]
    agent_response: str
    task_id: str | None
    context_id: str | None
    agent_card: AgentCard | None


class A2AClientGraph:
    """LangGraph client that uses A2A protocol to communicate with agent server."""
    
    def __init__(self, base_url: str = "http://localhost:10000"):
        """Initialize A2A client graph.
        
        Args:
            base_url: Base URL of the agent server
        """
        self.base_url = base_url
        self.httpx_client: httpx.AsyncClient | None = None
        self.client: A2AClient | None = None
        self.agent_card: AgentCard | None = None
        self.graph = self._build_graph()
    
    async def _initialize_client(self):
        """Initialize A2A client and fetch agent card."""
        if self.client is None:
            self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url,
            )
            self.agent_card = await resolver.get_agent_card()
            self.client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=self.agent_card
            )
            logger.info(f"Initialized A2A client for agent: {self.agent_card.name}")
    
    async def _send_to_agent(
        self, state: A2AClientState
    ) -> Dict[str, Any]:
        """Send user query to agent server via A2A protocol."""
        await self._initialize_client()
        
        # Get the latest user message
        messages = state["messages"]
        user_query = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_query = msg.content
                break
        
        if not user_query:
            return {
                "agent_response": "No user query found in messages.",
                "messages": [AIMessage(content="No user query found.")]
            }
        
        # Prepare message payload
        message_payload: Dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': user_query}],
                'message_id': uuid4().hex,
            },
        }
        
        # Use existing context if available
        if state.get("task_id") and state.get("context_id"):
            message_payload['message']['task_id'] = state["task_id"]
            message_payload['message']['context_id'] = state["context_id"]
        
        # Send request to agent server
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )
        
        try:
            response = await self.client.send_message(request)
            
            # Extract response content
            result = response.root.result
            artifacts = result.artifacts or []
            
            # Get the response text from artifacts
            response_text = ""
            if artifacts:
                artifact = artifacts[0]
                parts = artifact.parts or []
                if parts:
                    response_text = parts[0].root.text if hasattr(parts[0].root, 'text') else ""
            
            # Extract task_id and context_id for multi-turn conversations
            task_id = result.id if hasattr(result, 'id') else None
            context_id = result.context_id if hasattr(result, 'context_id') else None
            
            logger.info(f"Received response from agent: {response_text[:100]}...")
            
            return {
                "agent_response": response_text,
                "task_id": task_id,
                "context_id": context_id,
                "agent_card": self.agent_card,
                "messages": [AIMessage(content=response_text)]
            }
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            error_msg = f"Error communicating with agent: {str(e)}"
            return {
                "agent_response": error_msg,
                "messages": [AIMessage(content=error_msg)]
            }
    
    def _format_response(self, state: A2AClientState) -> Dict[str, Any]:
        """Format the final response for the user."""
        response = state.get("agent_response", "No response received.")
        return {
            "messages": [AIMessage(content=response)]
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(A2AClientState)
        
        # Add nodes
        graph.add_node("send_to_agent", self._send_to_agent)
        graph.add_node("format_response", self._format_response)
        
        # Set entry point
        graph.set_entry_point("send_to_agent")
        
        # Add edges
        graph.add_edge("send_to_agent", "format_response")
        graph.add_edge("format_response", END)
        
        return graph.compile()
    
    async def invoke(self, query: str, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Invoke the graph with a user query.
        
        Args:
            query: User query string
            config: Optional graph configuration
            
        Returns:
            Final state with agent response
        """
        if config is None:
            config = {"configurable": {"thread_id": str(uuid4())}}
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "agent_response": "",
            "task_id": None,
            "context_id": None,
            "agent_card": None,
        }
        
        result = await self.graph.ainvoke(initial_state, config)
        return result
    
    async def stream(self, query: str, config: Dict[str, Any] | None = None):
        """Stream the graph execution with a user query.
        
        Args:
            query: User query string
            config: Optional graph configuration
            
        Yields:
            State updates during execution
        """
        if config is None:
            config = {"configurable": {"thread_id": str(uuid4())}}
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "agent_response": "",
            "task_id": None,
            "context_id": None,
            "agent_card": None,
        }
        
        async for state in self.graph.astream(initial_state, config):
            yield state
    
    async def close(self):
        """Close the HTTP client."""
        if self.httpx_client:
            await self.httpx_client.aclose()


async def main():
    """Example usage of A2A client graph."""
    client_graph = A2AClientGraph()
    
    try:
        # Test query
        query = "What are the latest developments in artificial intelligence in 2025?"
        print(f"\n📤 Sending query: {query}\n")
        
        # Invoke the graph
        result = await client_graph.invoke(query)
        
        print(f"\n📥 Agent Response:\n{result['agent_response']}\n")
        
        # Test multi-turn conversation
        if result.get("task_id") and result.get("context_id"):
            print("\n🔄 Testing multi-turn conversation...\n")
            
            follow_up_query = "Can you provide more details about the most important development?"
            print(f"📤 Follow-up query: {follow_up_query}\n")
            
            # Use existing context for follow-up
            follow_up_state = {
                "messages": [HumanMessage(content=follow_up_query)],
                "agent_response": "",
                "task_id": result["task_id"],
                "context_id": result["context_id"],
                "agent_card": result.get("agent_card"),
            }
            
            config = {"configurable": {"thread_id": str(uuid4())}}
            follow_up_result = await client_graph.graph.ainvoke(follow_up_state, config)
            
            print(f"\n📥 Follow-up Response:\n{follow_up_result['agent_response']}\n")
    
    finally:
        await client_graph.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


