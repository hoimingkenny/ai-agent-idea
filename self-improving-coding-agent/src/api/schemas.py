from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    task: str
    max_iterations: int = Field(default=10, ge=1, le=50)


class TaskMemoryDTO(BaseModel):
    code: str
    output: str
    error: Optional[str] = None
    reflection: Optional[str] = None


class RunResponse(BaseModel):
    status: str
    iteration: int
    plan: List[str]
    current_code: str
    retrieved_context: str = ""
    research_logs: List[str] = Field(default_factory=list)
    history: List[TaskMemoryDTO] = Field(default_factory=list)
    raw: Any = None

