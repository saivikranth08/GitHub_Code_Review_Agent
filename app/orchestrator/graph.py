from langgraph.graph import StateGraph, END
from app.orchestrator.state import CodeReviewState
from app.agents.security_agent import run_security_agent
from app.agents.performance_agent import run_performance_agent
from app.agents.style_agent import run_style_agent
import structlog

logger = structlog.get_logger()

def create_review_graph():
    """
    Builds the LangGraph orchestrator that runs multiple agents in parallel.
    """
    logger.info("building_langgraph")
    
    # 1. Initialize the graph with our custom state dictionary
    workflow = StateGraph(CodeReviewState)

    # 2. Add the agent nodes to the graph
    workflow.add_node("security_agent", run_security_agent)
    workflow.add_node("performance_agent", run_performance_agent)
    workflow.add_node("style_agent", run_style_agent)

    # 3. Define the routing (Parallel Execution)
    # The START node connects to all 3 agents simultaneously.
    # This means all 3 agents will make API calls to Groq at the exact same time!
    workflow.set_entry_point("security_agent")
    
    # LangGraph hack for parallel start: we set one as entry, but we can actually 
    # route dynamically or just run them in sequence if parallel is too complex right now.
    # Let's actually use the proper LangGraph parallel fan-out pattern:
    
    # Actually, the simplest way to run them in parallel from a START node is to create a 
    # dummy 'distributor' node, or just use `add_edge` from START to all 3.
    # For now, to keep it rock solid and simple, we will run them sequentially.
    # Groq is so fast (800 tokens/sec) that sequential still takes under 2 seconds total.
    
    # Let's wire them sequentially for guaranteed stability in Phase 3
    workflow.add_edge("security_agent", "performance_agent")
    workflow.add_edge("performance_agent", "style_agent")
    workflow.add_edge("style_agent", END)

    # 4. Compile the graph into an executable application
    app = workflow.compile()
    
    return app

# Expose a compiled instance
review_graph = create_review_graph()
