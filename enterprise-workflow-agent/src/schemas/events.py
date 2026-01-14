from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EventSource(str, Enum):
    SLACK = "slack"
    JIRA = "jira"
    EMAIL = "email"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"

class IngestEvent(BaseModel):
    source: EventSource
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
