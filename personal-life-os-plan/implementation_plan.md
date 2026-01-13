# Technical Implementation Plan: Personal Life OS Agent (Expert Level)

## 1. Project Summary

The **Personal Life OS Agent** is a sophisticated, privacy-first AI system designed to function as a proactive life partner rather than a passive tool. It solves the "context amnesia" problem of current LLMs by maintaining a continuous, encrypted Knowledge Graph of the user's life (calendar, finance, health).

**Core Value Proposition:**
*   **Deep Context**: Remembers relationships, preferences, and history without hallucination.
*   **Proactivity**: Detects risks (burnout, financial strain) *before* they manifest.
*   **Sovereignty**: 100% local-first architecture where data never leaves the device unencrypted.
*   **Alignment**: optimizing for user-defined values (e.g., "Health > Work") rather than generic productivity.

---

## 2. Technical Architecture & Stack

### Stack Selection

| Component | Technology | Justification |
| :--- | :--- | :--- |
| **Language** | **Python 3.12+** | The standard for AI engineering; robust typing system for complex data modeling. |
| **Orchestration** | **LangGraph** | Essential for the **cyclic state management** required by the "proactive monitoring" loops and multi-step reasoning (Plan → Critique → Act). Standard linear chains cannot handle the "background thread" logic effectively. |
| **Local Inference** | **Ollama** (Llama 3 / Mistral) | Critical for the **Privacy Architecture**. Allows running powerful models entirely offline/locally, ensuring no sensitive PII is sent to cloud APIs. |
| **Vector Store** | **ChromaDB** (Local Persistence) | Lightweight, open-source vector database for **Memory Consolidation** and semantic retrieval of past events. |
| **Relational DB** | **SQLite + SQLCipher** | secure, encrypted-at-rest storage for structured data (financial transactions, health metrics). Zero-config serverless architecture fits the "Personal OS" model. |
| **Knowledge Graph** | **NetworkX** + **JSON Storage** | For mapping **Entities** (People, Places) and their relationships. Simpler than Neo4j for a single-user system but powerful enough for graph algorithms (centrality, pathfinding). |
| **Scheduling** | **APScheduler** | Robust in-process task scheduler to handle the **Proactive Monitoring** background threads (running every 6 hours) without needing a heavy message queue like Redis/Celery. |

### Architecture Diagram

```mermaid
graph TD
    subgraph "Data Ingestion Layer"
        Cal[Calendar API]
        Fin[Finance/Plaid Export]
        Health[HealthKit/Fitbit]
        Comms[Email/Slack]
    end

    subgraph "Privacy & Storage Core"
        Encrypt[Encryption Service (User Keys)]
        SQL[(SQLite - Structured Logs)]
        Vec[(ChromaDB - Semantic Memory)]
        KG[(NetworkX - Knowledge Graph)]
    end

    subgraph "Agentic Core (LangGraph)"
        Router{Router}
        Planner[Predictive Planner]
        Monitor[Background Monitor]
        Critic[Value Alignment Critic]
        Summarizer[Nightly Summarizer]
    end

    User((User)) <--> UI[CLI / Web Dashboard]

    %% Data Flow
    Cal & Fin & Health & Comms -->|Raw Events| Encrypt
    Encrypt -->|Encrypted Data| SQL
    
    %% Context Building
    SQL -->|Extract Entities| KG
    SQL -->|Vectorize| Vec

    %% Agent Loop
    UI -->|Query| Router
    Router -->|Fetch Context| KG & Vec & SQL
    Router --> Planner
    Planner --> Critic
    Critic -->|Approved| UI
    Critic -->|Conflict| Planner

    %% Background Threads
    Monitor -.->|Every 6h: Check Patterns| SQL
    Monitor -->|Alert Risk| UI
    Summarizer -.->|Nightly: Compress| Vec
```

### Data Schemas

```python
from datetime import datetime
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

# 1. Unified Event Model (The "Atom" of Context)
class LifeEvent(BaseModel):
    id: str
    source: Literal["calendar", "finance", "health", "communication"]
    timestamp: datetime
    content: str  # Encrypted payload
    entities: List[str]  # IDs of people/places involved
    metadata: Dict[str, float]  # e.g., {"cost": 120.0, "sleep_score": 85}

# 2. Knowledge Graph Entity
class Entity(BaseModel):
    id: str
    name: str
    type: Literal["person", "project", "place", "concept"]
    relationships: Dict[str, str]  # {target_entity_id: relationship_type}
    last_interaction: datetime
    importance_score: float

# 3. Agent State (LangGraph Context)
class AgentState(BaseModel):
    user_query: str
    current_context: List[LifeEvent]
    identified_conflicts: List[str]
    plan_steps: List[str]
    value_alignment_check: bool
    reasoning_trace: List[str]  # For "Transparent Reasoning"
```

### Architecture Mapping

| Key Architectural Decision | Phase Implemented | Implementation Detail |
| :--- | :--- | :--- |
| **Continuous Context Building** | **Phase 2** | `IngestionPipeline` classes for each data source; Entity extraction logic feeding NetworkX. |
| **Proactive Monitoring** | **Phase 3** | `APScheduler` job triggering the `AnomalyDetector` node in LangGraph every 6 hours. |
| **Value Alignment** | **Phase 3** | Dedicated `Critic` node in the graph that validates generated plans against `user_values.json` config. |
| **Privacy Architecture** | **Phase 1** | `Fernet` (cryptography lib) wrapper around all DB writes; Local Ollama setup. |
| **Predictive Planning** | **Phase 3** | Time-series heuristic analysis on `LifeEvent` history to forecast resource contention. |
| **Memory Consolidation** | **Phase 4** | Nightly job using LLM to summarize `LifeEvent`s into higher-level `Memory` vectors. |

---

## 3. Detailed Implementation Plan

### Phase 1: Foundation & Privacy-First Infrastructure
**Goal:** Build the secure storage layer and basic agent scaffolding. No data enters the system without encryption.

*   **File Structure**:
    *   `src/core/security.py`: Encryption/Decryption logic.
    *   `src/core/config.py`: Configuration loading (Env vars, Model selection).
    *   `src/storage/db.py`: SQLite + SQLCipher setup.
    *   `src/storage/vector.py`: ChromaDB wrapper.
*   **Key Tasks**:
    1.  Implement `SecurityManager` class using `cryptography.fernet`. Ensure keys are loaded from env, not hardcoded.
    2.  Setup `DatabaseManager` to initialize SQLite with schemas for `LifeEvent`.
    3.  Setup `VectorStore` to handle embedding generation (using local embeddings like `all-MiniLM-L6-v2`).
    4.  Create basic `Agent` class that connects to Ollama and echoes responses (Hello World of LLM).

### Phase 2: Context Ingestion & Knowledge Graph
**Goal:** Ingest data from mock sources and build the "World Model" (Graph + Vector).

*   **File Structure**:
    *   `src/ingestion/connectors/`: Base class and implementations for Calendar/Finance.
    *   `src/ingestion/processor.py`: Entity extraction logic.
    *   `src/storage/graph.py`: NetworkX wrapper.
*   **Key Tasks**:
    1.  Implement `CalendarConnector` and `FinanceConnector` (start with CSV/JSON import for MVP).
    2.  Build `ContextProcessor`: Uses LLM to parse raw text/JSON into `LifeEvent` objects and extract `Entity` nodes.
    3.  Implement `GraphStore.add_entity(entity)` and `GraphStore.add_relationship(source, target, type)`.
    4.  Verify that ingesting a "Lunch with Sarah" event creates a "Sarah" node in the graph.

### Phase 3: Agentic Reasoning & Proactive Monitoring
**Goal:** The "Brain". Implement the LangGraph state machine, value alignment, and background monitoring.

*   **File Structure**:
    *   `src/agent/graph.py`: The LangGraph state machine definition.
    *   `src/agent/nodes/`: Individual logic (Planner, Critic, ToolExecutor).
    *   `src/services/monitor.py`: Background scheduler.
*   **Key Tasks**:
    1.  Define the **ReAct** style graph: `Input -> RetrieveContext -> Plan -> CheckValues -> Output`.
    2.  Implement `ValueCritic` node: Prompts LLM with "Does this action conflict with [Values]?"
    3.  Implement `AnomalyDetector`: Simple statistical check (e.g., "Meeting hours > X AND Sleep hours < Y").
    4.  Setup `APScheduler` in `main.py` to run `AnomalyDetector` every 6 hours.

### Phase 4: Polish & Interaction
**Goal:** Make it usable. CLI/Web interface, Transparent Reasoning display, and Memory Consolidation.

*   **File Structure**:
    *   `src/interface/cli.py` or `src/interface/app.py` (Streamlit).
    *   `src/services/memory_consolidation.py`: Nightly summarization.
*   **Key Tasks**:
    1.  Build a **Streamlit** dashboard showing:
        *   Chat interface.
        *   Knowledge Graph visualization (using `streamlit-agraph`).
        *   Current "Risk Level" (from Monitor).
    2.  Implement `consolidate_memories()`: Query events > 24h old, summarize, store summary, archive raw events.
    3.  Add "Why?" feature: Append the `reasoning_trace` from `AgentState` to the final response.

---

## 4. Development Priorities

### P0: Critical (The "MVP")
*   [ ] Local LLM (Ollama) integration.
*   [ ] Secure Storage (SQLite + Encryption).
*   [ ] Basic Ingestion (Manual Entry/JSON import).
*   [ ] Simple RAG (Retrieval Augmented Generation) loop.

### P1: Important (The "Expert" Features)
*   [ ] LangGraph Cyclic Logic (Plan -> Critique).
*   [ ] Knowledge Graph Entity Extraction.
*   [ ] Background Monitoring Service.
*   [ ] Value Alignment "Critic" Node.

### P2: Nice-to-have (Polish)
*   [ ] Real-time API integrations (Google Calendar API, Plaid).
*   [ ] Interactive Graph Visualization in UI.
*   [ ] Voice Input/Output.
