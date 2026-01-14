# Learning Outcomes & Portfolio Guide: Self-Improving Coding Agent

## 1. Project Challenges

*   **Secure Execution of Untrusted Code:**
    *   Building a system that executes arbitrary AI-generated code is inherently risky. The challenge was to create a robust sandbox that prevents system compromise (e.g., infinite loops, file system destruction) while still allowing the agent to perform useful tasks. This required a multi-layered approach using **Docker** for containerization and resource limits, combined with **AST (Abstract Syntax Tree)** parsing for static analysis to pre-emptively block dangerous imports like `subprocess` before execution.

*   **Orchestrating Cyclic Agentic State:**
    *   Unlike linear RAG pipelines, this agent requires a cyclic workflow (Plan → Code → Execute → Reflect) where the state needs to persist and mutate across iterations. Managing this stateful behavior and defining clear exit conditions to prevent infinite retry loops was a complex architectural challenge solved using **LangGraph**.

*   **Semantic Error Correction & Memory:**
    *   Implementing a "long-term memory" that actually helps the agent avoid repeating mistakes. The challenge was not just storing data, but retrieving *relevant* past failures based on the current context. This involved designing a schema for `FailureRecord` and using **ChromaDB** to perform vector similarity searches on error signatures, effectively closing the learning loop.

## 2. The "Why" (Problem Solved)

*   **Autonomous Reliability:** Standard LLMs often generate code that looks correct but fails to run. This project bridges the gap between "generation" and "execution" by validating code in a real environment. It ensures that the final output is not just syntactically correct, but functionally verified.
*   **Efficiency through Learning:** By persisting "lessons learned" in a vector store, the agent eliminates the cost of re-discovering solutions to known problems. It simulates a developer growing in experience, making it a more efficient tool for recurring coding tasks.
*   **Safe Automation:** It provides a blueprint for safe AI automation. By solving the sandboxing and safety check problems, it enables the deployment of coding agents in environments where security is paramount, unlocking potential for automated testing and refactoring pipelines.

## 3. CV/Resume Summary

**Self-Improving Autonomous Coding Agent** | *Python, LangGraph, Docker, ChromaDB, LangChain*
Architected an autonomous agent capable of iteratively writing, executing, and refining code using a cyclic **LangGraph** workflow. Engineered a secure **Docker**-based sandbox with **AST** static analysis to safely execute and validate untrusted code in real-time. Implemented a **RAG**-based memory system using **ChromaDB** to index and retrieve past error patterns, enabling the agent to learn from failures and reduce repetitive debugging cycles.

## 4. Key Learning Outcomes (Star Method Prep)

*   **Agentic Workflow Orchestration:**
    *   Demonstrated the ability to move beyond simple LLM prompts by designing a stateful, cyclic graph architecture (LangGraph). Modeled complex behaviors where the agent autonomously plans, executes, and reflects on its work, handling control flow based on dynamic execution results.

*   **Secure System Design & Containerization:**
    *   Showcased expertise in "defense-in-depth" security practices. demonstrated how to isolate high-risk operations using Docker containers and implement static code analysis (AST) to enforce policy compliance, ensuring the safety of the host system.

*   **Vector Database & Contextual Memory:**
    *   Applied vector search technology (ChromaDB) to solve a specific functional problem (error recurrence). Learned how to structure data (embeddings) to enable semantic retrieval, effectively giving the AI "experience" that persists across sessions.

*   **Advanced Docker Patterns (Docker-in-Docker):**
    *   Solved the complex deployment challenge of running a containerized agent that needs to spawn its own sibling containers. Implemented a Docker-in-Docker (DinD) architecture by mounting the host's Docker socket, enabling the agent to maintain its secure sandbox capabilities even when deployed as a container itself.

*   **Cost-Effective LLM Integration:**
    *   Optimized the system for real-world viability by integrating OpenRouter to leverage cost-effective models (`xiaomi/mimo-v2-flash:free`). This demonstrated an understanding of the trade-offs between model capability and operational cost, a critical skill for building sustainable AI applications.
