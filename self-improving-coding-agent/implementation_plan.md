# Self-Improving Coding Agent - Technical Implementation Plan

## 1. Project Summary
**Goal**: Build an autonomous coding agent capable of writing, testing, and refining code through an iterative agentic loop (Plan → Execute → Test → Reflect).
**Value Proposition**: Unlike standard chatbots, this agent validates its own output. It uses a feedback loop to correct errors, ensuring functional code delivery. It learns from past mistakes using a memory system, reducing repetitive errors and improving efficiency over time.

## 2. Technical Architecture & Stack

### 2.1 Stack Selection
*   **Language**: Python 3.10+ (Strong typing, rich ecosystem for AI/Agents).
*   **Agent Framework**: **LangGraph** (Stateful, cyclic graph architecture perfect for the Plan-Execute-Reflect loop).
*   **LLM Interface**: **LangChain** (Standard interface for LLMs, tools, and chains).
*   **Sandboxing**: **Docker** (via `docker-py`). Provides complete isolation for executing untrusted code with resource limits (CPU/Memory).
*   **Memory/Vector Store**: **ChromaDB**. Local, efficient vector store for semantic retrieval of past failures and solutions.
*   **Static Analysis**: **AST** (Abstract Syntax Tree) & **Bandit**. Pre-execution safety checks to block dangerous operations.
*   **CLI**: **Typer**. For a clean, robust command-line interface.

### 2.2 Architecture Diagram

```mermaid
graph TD
    Start([User Request]) --> RetrieveMemory[Retrieve Past Lessons]
    RetrieveMemory --> Plan[Planner Node]
    Plan --> Code[Coder Node]
    Code --> SafetyCheck{Static Analysis}
    
    SafetyCheck -- Fail --> Reflect[Reflector Node]
    SafetyCheck -- Pass --> Execute[Executor Node (Docker)]
    
    Execute -- Error --> Reflect
    Execute -- Success --> Verify{Verification}
    
    Verify -- Fail --> Reflect
    Verify -- Pass --> SaveMemory[Save Success Pattern]
    
    Reflect --> Plan
    SaveMemory --> End([Task Completed])
    
    subgraph Memory System
        RetrieveMemory
        SaveMemory
    end
    
    subgraph Sandbox
        Execute
    end
```

### 2.3 Data Schemas

```python
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

class TaskMemory(BaseModel):
    """Stores context for the current execution attempt."""
    code: str
    output: str
    error: Optional[str]
    reflection: Optional[str]

class AgentState(BaseModel):
    """The state object passed through the LangGraph."""
    task: str
    plan: List[str]
    current_code: str
    file_path: str
    iteration: int
    max_iterations: int = 10
    history: List[TaskMemory] = []
    status: Literal["planning", "coding", "executing", "reflecting", "finished", "failed"]

class FailureRecord(BaseModel):
    """Schema for long-term failure memory."""
    error_signature: str  # Vectorized for similarity search
    task_description: str
    failed_code: str
    fix_description: str
    timestamp: float
```

### 2.4 Architecture Mapping
*   **Execution Loop Design**: Implemented via **LangGraph** nodes (Plan, Code, Execute, Reflect) with a cyclic edge structure.
*   **Sandboxing Strategy**: **Docker** containers used in the `Executor Node` with `pids_limit`, `mem_limit`, and network disabled.
*   **Memory Hierarchy**: 
    *   *Short-term*: `AgentState.history` (in-memory list).
    *   *Long-term*: ChromaDB `success_patterns` collection.
    *   *Failure*: ChromaDB `failure_patterns` collection.
*   **Reflection Mechanism**: The `Reflector Node` uses LLM to analyze `TaskMemory.error` and `TaskMemory.code`, generating a `reflection` string.
*   **Learning from Mistakes**: `RetrieveMemory` node queries ChromaDB before planning. `SaveMemory` node stores data after success/failure.
*   **Code Safety**: `SafetyCheck` node runs AST analysis before Docker execution.

## 3. Detailed Implementation Plan

### Phase 1: Foundation & Infrastructure (P0)
**Goal**: Establish the project structure and secure execution environment.
*   **File Structure**:
    *   `src/sandbox/runner.py`
    *   `src/utils/safety.py`
    *   `tests/test_sandbox.py`
*   **Key Tasks**:
    *   Setup `docker-py` client.
    *   Implement `Sandbox.run(code: str) -> Dict[str, str]` which writes code to a temp volume and runs it in a container.
    *   Implement `Safety.check(code: str) -> bool` using `ast` to blacklist `import os`, `subprocess`, etc. (unless necessary and strictly controlled).

### Phase 2: Core Agent Logic (P0)
**Goal**: Implement the basic Plan-Code-Execute-Reflect loop.
*   **File Structure**:
    *   `src/agent/graph.py`
    *   `src/agent/nodes.py`
    *   `src/agent/state.py`
*   **Key Tasks**:
    *   Define `AgentState`.
    *   Implement `planner`, `coder`, `executor` (calls Sandbox), `reflector` functions.
    *   Construct the LangGraph with conditional edges based on execution results.

### Phase 3: Memory & Learning (P1)
**Goal**: Add persistence and "intelligence" via past experiences.
*   **File Structure**:
    *   `src/memory/vector_store.py`
    *   `src/agent/callbacks.py`
*   **Key Tasks**:
    *   Setup ChromaDB client.
    *   Implement `Memory.retrieve_similar_failures(query: str)`.
    *   Implement `Memory.store_failure(error: str, fix: str)`.
    *   Integrate retrieval into the `planner` prompt.

### Phase 4: Polish & CLI (P2)
**Goal**: User interface and robustness.
*   **File Structure**:
    *   `main.py`
    *   `pyproject.toml`
*   **Key Tasks**:
    *   Create Typer CLI: `python main.py run "task"`.
    *   Add streaming output to show agent progress.
    *   Add "Human in the loop" option for dangerous file operations (if we allow them later).

## 4. Development Priorities
1.  **P0**: Docker Sandbox & Safety Checks (Critical for running generated code).
2.  **P0**: LangGraph Control Flow (The core agent loop).
3.  **P1**: Reflection & Error Handling (Crucial for "self-improvement").
4.  **P2**: Vector Memory (Optimization for long-term usage).
5.  **P2**: CLI & Developer Experience.
