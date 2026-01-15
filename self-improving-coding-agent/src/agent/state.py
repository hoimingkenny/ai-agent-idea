from typing import List, Optional, Literal, Annotated
from pydantic import BaseModel, Field
import operator

class TaskMemory(BaseModel):
    """Stores context for the current execution attempt."""
    code: str
    output: str
    error: Optional[str] = None
    reflection: Optional[str] = None

class AgentState(BaseModel):
    """The state object passed through the LangGraph."""
    task: str
    plan: List[str] = Field(default_factory=list)
    current_code: str = ""
    file_path: str = "solution.py"
    iteration: int = 0
    max_iterations: int = 5
    retrieved_context: str = ""
    research_logs: List[str] = Field(default_factory=list)
    # history: Annotated[List[TaskMemory], operator.add] # If we want to append. 
    # But standard Pydantic usage in LangGraph replaces state unless Annotated is used.
    # For now, let's just use List and manually append in nodes.
    history: List[TaskMemory] = Field(default_factory=list)
    status: Literal["planning", "researching", "coding", "executing", "reflecting", "finished", "failed"] = "planning"
