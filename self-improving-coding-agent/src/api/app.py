from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .schemas import RunRequest, RunResponse, TaskMemoryDTO
from ..agent.graph import create_graph


app = FastAPI(title="Self-Improving Coding Agent", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/run", response_model=RunResponse)
def run_agent(payload: RunRequest) -> RunResponse:
    graph = create_graph()

    initial_state = {
        "task": payload.task,
        "max_iterations": payload.max_iterations,
        "iteration": 0,
        "plan": [],
        "current_code": "",
        "history": [],
        "status": "planning",
        "retrieved_context": "",
        "research_logs": [],
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    history = []
    for item in result.get("history", []):
        if hasattr(item, "model_dump"):
            history.append(TaskMemoryDTO(**item.model_dump()))
        else:
            history.append(TaskMemoryDTO(**item))

    return RunResponse(
        status=result.get("status", "unknown"),
        iteration=result.get("iteration", 0),
        plan=result.get("plan", []),
        current_code=result.get("current_code", ""),
        retrieved_context=result.get("retrieved_context", ""),
        research_logs=result.get("research_logs", []),
        history=history,
        raw=result,
    )

