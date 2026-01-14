from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import retrieve_memory, planner, coder, executor, reflector, save_memory

def check_execution_status(state: AgentState):
    """
    Determines the next step based on the execution result.
    """
    if state.status == "finished":
        return "success"
    
    if state.iteration >= state.max_iterations:
        print("Max iterations reached. Task failed.")
        return "failed"
    
    return "continue"

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("retrieve_memory", retrieve_memory)
    workflow.add_node("planner", planner)
    workflow.add_node("coder", coder)
    workflow.add_node("executor", executor)
    workflow.add_node("reflector", reflector)
    workflow.add_node("save_memory", save_memory)

    # Define flow
    workflow.set_entry_point("retrieve_memory")
    
    workflow.add_edge("retrieve_memory", "planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "executor")
    
    # Conditional edge after execution
    workflow.add_conditional_edges(
        "executor",
        check_execution_status,
        {
            "success": "save_memory",
            "failed": END,
            "continue": "reflector"
        }
    )
    
    workflow.add_edge("reflector", "coder")
    workflow.add_edge("save_memory", END)

    return workflow.compile()
