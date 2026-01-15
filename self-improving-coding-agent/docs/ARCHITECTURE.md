# Architecture

## Overview

This project implements a cyclic coding agent using LangGraph:

1. Retrieve memory (similar past failures)
2. Research (optional web search + summarization)
3. Plan (step-by-step plan)
4. Code (generate Python code)
5. Execute (sandboxed execution)
6. Reflect (debug loop on failure)
7. Save memory (store successes and failure fixes)

## Key Modules

- Agent graph: src/agent/graph.py
- Agent nodes: src/agent/nodes.py
- Prompts: src/agent/prompts.py
- Research: src/agent/research.py
- Web search tool: src/agent/tools.py
- Safety checks: src/utils/safety.py
- Sandbox runner: src/sandbox/runner.py
- Vector memory: src/memory/vector_store.py

## Trust Boundaries

- Untrusted code runs inside Docker when available (network disabled, resource limited).
- Static safety checks run before execution.
- Web search output is summarized before being used for planning/coding.

