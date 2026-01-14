from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator
from src.schemas.events import EventSource, WorkflowStatus, AgentAction, AuditLogEntry

class WorkflowState(TypedDict):
    """Core state object passed through LangGraph"""
    workflow_id: str
    source: EventSource
    original_request: str
    plan: List[str]
    current_step_index: int
    context: Dict[str, Any]
    status: WorkflowStatus
    errors: List[str]
    audit_trail: Annotated[List[AuditLogEntry], operator.add]
    
    # Internal state for the graph
    next_node: Optional[str]
