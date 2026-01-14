import asyncio
import uuid
from src.services.queue import queue_service
from src.agent.graph import agent_graph
from src.schemas.events import WorkflowStatus
from src.agent.state import WorkflowState

async def process_event(event):
    """Process a single event through the LangGraph agent"""
    print(f"Processing event: {event}")
    
    workflow_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": workflow_id}}
    
    # Initialize state
    initial_state = WorkflowState(
        workflow_id=workflow_id,
        source=event.source,
        original_request=event.payload.get("text", "No text provided"),
        plan=[],
        current_step_index=0,
        context={},
        status=WorkflowStatus.PENDING,
        errors=[],
        audit_trail=[],
        next_node=None
    )
    
    try:
        # Run the graph
        # This will run until it hits an interrupt or END
        result = await agent_graph.ainvoke(initial_state, config=config)
        
        # Check if we are interrupted
        snapshot = await agent_graph.aget_state(config)
        if snapshot.next:
            print(f"Workflow interrupted at: {snapshot.next}. Waiting for approval...")
            # In a real system, we would notify the approval service here.
            # For demonstration, we could simulate approval:
            # await agent_graph.ainvoke(None, config=config)
        else:
            print(f"Workflow completed: {result['status']}")
            print(f"Audit Trail: {result['audit_trail']}")
            
    except Exception as e:
        print(f"Error processing workflow: {e}")

async def run_worker():
    """Main loop for the background worker"""
    print("Starting worker...")
    while True:
        try:
            event = await queue_service.pop_event()
            if event:
                await process_event(event)
            else:
                # Sleep briefly to avoid tight loop
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_worker())
