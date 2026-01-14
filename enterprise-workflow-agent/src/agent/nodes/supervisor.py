from src.agent.state import WorkflowState, WorkflowStatus
from typing import Literal

async def supervisor_node(state: WorkflowState):
    """
    Supervisor node that plans the workflow or decides the next step.
    In a real implementation, this would use an LLM to generate a plan.
    """
    
    # If no plan exists, generate one
    if not state.get("plan"):
        request = state["original_request"].lower()
        plan = []
        
        if "slack" in request or "message" in request:
            plan.append("communication_node")
        if "data" in request or "query" in request:
            plan.append("data_node")
        if "analyze" in request:
            plan.append("analysis_node")
        
        # Default fallback
        if not plan:
            plan.append("documentation_node")
            
        return {
            "plan": plan,
            "status": WorkflowStatus.PLANNING,
            "current_step_index": 0
        }
    
    # Check if workflow is complete
    if state["current_step_index"] >= len(state["plan"]):
        return {
            "status": WorkflowStatus.COMPLETED,
            "next_node": "end"
        }
    
    # Determine next node from plan
    next_step = state["plan"][state["current_step_index"]]
    return {
        "status": WorkflowStatus.RUNNING,
        "next_node": next_step
    }

def router(state: WorkflowState) -> Literal["communication_node", "data_node", "analysis_node", "documentation_node", "end"]:
    """Conditional edge router"""
    if state["status"] == WorkflowStatus.COMPLETED:
        return "end"
        
    return state["next_node"]
