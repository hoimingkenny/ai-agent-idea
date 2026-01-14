from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.schemas.events import IngestEvent, EventSource
from src.services.queue import queue_service
from typing import Dict, Any

router = APIRouter()

@router.post("/slack")
async def ingest_slack_event(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Webhook endpoint for Slack events.
    Verifies the request and pushes it to the event queue.
    """
    # TODO: Verify Slack signature
    
    # Handle URL verification challenge from Slack
    if "type" in payload and payload["type"] == "url_verification":
        return {"challenge": payload["challenge"]}

    # Create a standardized event
    event = IngestEvent(
        source=EventSource.SLACK,
        event_type=payload.get("type", "unknown"),
        payload=payload
    )
    
    # Push to queue in background to keep response fast
    background_tasks.add_task(queue_service.push_event, event)
    
    return {"status": "accepted", "message": "Event queued for processing"}
