from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agent.state import WorkflowState
from src.agent.nodes.supervisor import supervisor_node, router
from src.agent.nodes.workers import (
    communication_node,
    data_node,
    analysis_node,
    documentation_node
)

# Define the graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("communication_node", communication_node)
workflow.add_node("data_node", data_node)
workflow.add_node("analysis_node", analysis_node)
workflow.add_node("documentation_node", documentation_node)

# Add edges
workflow.set_entry_point("supervisor")

# Conditional edges from supervisor to workers
workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "communication_node": "communication_node",
        "data_node": "data_node",
        "analysis_node": "analysis_node",
        "documentation_node": "documentation_node",
        "end": END
    }
)

# Edges from workers back to supervisor
workflow.add_edge("communication_node", "supervisor")
workflow.add_edge("data_node", "supervisor")
workflow.add_edge("analysis_node", "supervisor")
workflow.add_edge("documentation_node", "supervisor")

# Initialize checkpointer
checkpointer = MemorySaver()

# Compile the graph with checkpointer and interrupt
agent_graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["communication_node"] # Human approval required before sending messages
)
