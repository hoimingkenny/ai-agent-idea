from langchain_core.messages import HumanMessage
from src.agent.state import WorkflowState, WorkflowStatus
from src.schemas.events import AgentAction, AuditLogEntry
from src.agent.tools.slack import slack_tool
from src.agent.tools.db_query import db_query_tool
from datetime import datetime

async def communication_node(state: WorkflowState):
    """Worker node for communication tasks"""
    current_task = state['plan'][state['current_step_index']]
    print(f"Executing Communication Task: {current_task}")
    
    # Mock extracting channel and message from context or task description
    channel = "#general"
    message = f"Executing task: {current_task}. Context: {state.get('context', {})}"
    
    result = await slack_tool.send_message(channel, message)
    
    # Update audit trail
    action = AgentAction(
        agent_name="CommunicationAgent",
        tool_name="send_message",
        tool_input={"channel": channel, "message": message},
        timestamp=datetime.now()
    )
    
    audit_entry = AuditLogEntry(
        workflow_id=state['workflow_id'],
        action=action,
        outcome=result.get("status", "unknown"),
        authorized_by=None
    )
    
    return {
        "audit_trail": [audit_entry],
        "current_step_index": state["current_step_index"] + 1
    }

async def data_node(state: WorkflowState):
    """Worker node for data tasks"""
    current_task = state['plan'][state['current_step_index']]
    print(f"Executing Data Task: {current_task}")
    
    # Mock query execution
    query = "SELECT * FROM users LIMIT 5" # In reality, extracted from task/LLM
    
    # We catch errors here to prevent crashing the worker
    try:
        # data = await db_query_tool.execute_query(query)
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}] # Mock data
        outcome = "success"
    except Exception as e:
        data = {"error": str(e)}
        outcome = "failed"
        
    action = AgentAction(
        agent_name="DataAgent",
        tool_name="execute_query",
        tool_input={"query": query},
        timestamp=datetime.now()
    )
    
    audit_entry = AuditLogEntry(
        workflow_id=state['workflow_id'],
        action=action,
        outcome=outcome,
        authorized_by=None
    )
    
    # Update context with data
    new_context = state.get("context", {}).copy()
    new_context["data_result"] = data
    
    return {
        "context": new_context,
        "audit_trail": [audit_entry],
        "current_step_index": state["current_step_index"] + 1
    }

async def analysis_node(state: WorkflowState):
    """Worker node for analysis tasks"""
    current_task = state['plan'][state['current_step_index']]
    print(f"Executing Analysis Task: {current_task}")
    
    data_to_analyze = state.get("context", {}).get("data_result", [])
    analysis_result = f"Analyzed {len(data_to_analyze)} records. Found patterns X, Y, Z."
    
    action = AgentAction(
        agent_name="AnalysisAgent",
        tool_name="analyze_data",
        tool_input={"data_summary": f"{len(data_to_analyze)} records"},
        timestamp=datetime.now()
    )
    
    audit_entry = AuditLogEntry(
        workflow_id=state['workflow_id'],
        action=action,
        outcome="success",
        authorized_by=None
    )
    
    new_context = state.get("context", {}).copy()
    new_context["analysis_result"] = analysis_result
    
    return {
        "context": new_context,
        "audit_trail": [audit_entry],
        "current_step_index": state["current_step_index"] + 1
    }

async def documentation_node(state: WorkflowState):
    """Worker node for documentation tasks"""
    current_task = state['plan'][state['current_step_index']]
    print(f"Executing Documentation Task: {current_task}")
    
    # Mock documentation
    doc_content = f"Workflow Report:\nAnalysis: {state.get('context', {}).get('analysis_result', 'N/A')}"
    
    action = AgentAction(
        agent_name="DocumentationAgent",
        tool_name="write_document",
        tool_input={"content_length": len(doc_content)},
        timestamp=datetime.now()
    )
    
    audit_entry = AuditLogEntry(
        workflow_id=state['workflow_id'],
        action=action,
        outcome="success",
        authorized_by=None
    )
    
    return {
        "audit_trail": [audit_entry],
        "current_step_index": state["current_step_index"] + 1
    }
