"""LangGraph agent integration with production features."""

from typing import Dict, Any, List, Optional
import os

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from .models import get_openai_model
from .rag import ProductionRAGChain


class AgentState(TypedDict):
    """State schema for agent graphs."""
    messages: Annotated[List[BaseMessage], add_messages]


def create_rag_tool(rag_chain: ProductionRAGChain):
    """Create a RAG tool from a ProductionRAGChain."""
    
    @tool
    def retrieve_information(query: str) -> str:
        """Use Retrieval Augmented Generation to retrieve information from the student loan documents."""
        try:
            result = rag_chain.invoke(query)
            return result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    return retrieve_information


def get_default_tools(rag_chain: Optional[ProductionRAGChain] = None) -> List:
    """Get default tools for the agent.
    
    Args:
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        List of tools
    """
    tools = []
    
    # Add Tavily search if API key is available
    if os.getenv("TAVILY_API_KEY"):
        tools.append(TavilySearchResults(max_results=5))
    
    # Add Arxiv tool
    tools.append(ArxivQueryRun())
    
    # Add RAG tool if provided
    if rag_chain:
        tools.append(create_rag_tool(rag_chain))
    
    return tools


def create_langgraph_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None
):
    """Create a simple LangGraph agent.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        Compiled LangGraph agent
    """
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    def call_model(state: AgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return END
    
    # Build graph
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"action": "action", END: END})
    graph.add_edge("action", "agent")
    
    return graph.compile()


def create_helpfulness_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None,
    eval_model_name: Optional[str] = None,
    max_refinements: int = 2
):
    """Create a helpfulness-checking LangGraph agent with evaluation and refinement.
    
    This agent evaluates its own responses and refines them if they're not helpful enough.
    
    Args:
        model_name: OpenAI model name for the main agent
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        eval_model_name: Model name for evaluation (defaults to model_name)
        max_refinements: Maximum number of refinement iterations
        
    Returns:
        Compiled LangGraph agent with evaluation and refinement capabilities
    """
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get main model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    # Get evaluation model (use same model if not specified, but with lower temperature)
    eval_model = get_openai_model(
        model_name=eval_model_name or model_name, 
        temperature=0.0  # Deterministic evaluation
    )
    
    # Helpfulness evaluation prompt
    helpfulness_eval_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert evaluator. Evaluate how helpful and complete the assistant's response is to the user's question.

Consider:
1. Does it directly answer the question?
2. Is it complete and informative?
3. Is it accurate based on the available context?
4. Could it be improved?

Respond with ONLY one word: "SATISFACTORY" or "NEEDS_IMPROVEMENT"
If the response is incomplete, inaccurate, unhelpful, or missing important information, respond "NEEDS_IMPROVEMENT".
Otherwise, respond "SATISFACTORY"."""),
        ("human", """User Question: {question}

Assistant Response: {response}

Context Available: {context}

Evaluation:""")
    ])
    
    def call_model(state: AgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def evaluate_response(state: AgentState) -> Dict[str, Any]:
        """Evaluate the helpfulness of the response."""
        messages = state["messages"]
        
        # Find the original user question
        user_question = None
        for msg in messages:
            if isinstance(msg, HumanMessage) and msg.content:
                user_question = msg.content
                break
        
        # Find the last assistant response (non-evaluation)
        last_response = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and hasattr(msg, 'content') and msg.content:
                # Skip evaluation messages
                if "EVALUATION:" not in str(msg.content) and not hasattr(msg, 'tool_calls'):
                    last_response = msg.content
                    break
        
        if not user_question or not last_response:
            # If we can't find question or response, consider it satisfactory
            eval_message = AIMessage(content="EVALUATION: SATISFACTORY")
            return {"messages": [eval_message]}
        
        # Get context from tool calls if available
        context = "No specific context available"
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                context = "Tools were used to gather information"
                break
        
        # Evaluate
        try:
            eval_prompt = helpfulness_eval_prompt.format_messages(
                question=user_question,
                response=last_response,
                context=context
            )
            
            eval_result = eval_model.invoke(eval_prompt)
            evaluation = eval_result.content.strip().upper()
            
            # Ensure it's one of the expected values
            if "NEEDS_IMPROVEMENT" in evaluation or "IMPROVEMENT" in evaluation:
                evaluation = "NEEDS_IMPROVEMENT"
            else:
                evaluation = "SATISFACTORY"
                
        except Exception as e:
            # On error, default to satisfactory
            evaluation = "SATISFACTORY"
        
        # Add evaluation to messages
        eval_message = AIMessage(content=f"EVALUATION: {evaluation}")
        return {"messages": [eval_message]}
    
    def should_refine(state: AgentState) -> str:
        """Decide if response needs refinement."""
        messages = state["messages"]
        
        # Count how many evaluations we've done (number of refinements)
        iteration_count = sum(1 for msg in messages if "EVALUATION:" in str(msg.content))
        
        # Check last evaluation
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and "EVALUATION:" in str(msg.content):
                evaluation = str(msg.content).split("EVALUATION:")[-1].strip()
                if "NEEDS_IMPROVEMENT" in evaluation and iteration_count <= max_refinements:
                    return "refine"
                return "end"
        
        # Default: if we've done too many iterations, end
        if iteration_count >= max_refinements:
            return "end"
        
        return "end"
    
    def refine_response(state: AgentState) -> Dict[str, Any]:
        """Refine the response based on evaluation."""
        messages = state["messages"]
        
        # Get the original question
        user_question = None
        for msg in messages:
            if isinstance(msg, HumanMessage) and msg.content:
                user_question = msg.content
                break
        
        if not user_question:
            # If no question found, just return a message
            return {"messages": [AIMessage(content="I apologize, but I need a question to provide a helpful response.")]}
        
        # Build refinement prompt with context
        refinement_system = """The previous response was evaluated as needing improvement. 
Please provide a better, more helpful response to the user's question.
Use the conversation history and any tool results available to create a more complete and accurate answer.
Focus on:
1. Directly answering the question
2. Providing complete information
3. Being accurate and helpful
4. Using available context effectively"""
        
        # Get conversation context (exclude evaluation messages)
        conversation_context = []
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage)) and "EVALUATION:" not in str(msg.content):
                conversation_context.append(msg)
                # Keep last few messages for context
                if len(conversation_context) > 5:
                    conversation_context = conversation_context[-5:]
        
        # Build messages for refinement
        refinement_messages = [SystemMessage(content=refinement_system)]
        refinement_messages.extend(conversation_context)
        
        # Add a human message prompting for refinement
        refinement_messages.append(HumanMessage(
            content=f"Please provide an improved response to: {user_question}"
        ))
        
        try:
            refined_response = model_with_tools.invoke(refinement_messages)
            return {"messages": [refined_response]}
        except Exception as e:
            # On error, return a message indicating the error
            return {"messages": [AIMessage(content=f"Error during refinement: {str(e)}")]}
    
    def should_continue(state: AgentState) -> str:
        """Route to tools if the last message has tool calls, otherwise evaluate."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "action"
        return "evaluate"
    
    # Build helpfulness agent graph
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.add_node("evaluate", evaluate_response)
    graph.add_node("refine", refine_response)
    
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"action": "action", "evaluate": "evaluate"})
    graph.add_edge("action", "agent")
    graph.add_conditional_edges("evaluate", should_refine, {"refine": "refine", "end": END})
    graph.add_edge("refine", "agent")  # Loop back to agent after refinement
    
    return graph.compile()
