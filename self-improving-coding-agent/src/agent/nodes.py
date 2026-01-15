from langchain_core.output_parsers import StrOutputParser
from .state import AgentState, TaskMemory
from .prompts import coding_prompt, planning_prompt, reflection_prompt
from .research import run_research
from ..sandbox.runner import Sandbox
from ..utils.safety import Safety
from ..memory.vector_store import Memory
from ..llm.factory import ensure_llm

_memory_store = None


def ensure_memory_store() -> Memory:
    global _memory_store
    if _memory_store is None:
        _memory_store = Memory()
    return _memory_store

def retrieve_memory(state: AgentState):
    print("---RETRIEVING MEMORY---")
    failures = ensure_memory_store().retrieve_similar_failures(state.task)
    context = ""
    if failures:
        context = "Past Failures/Lessons:\n" + "\n".join(
            [f"- Error: {f.get('error')}\n  Fix: {f.get('fix')}" for f in failures]
        )
    return {"retrieved_context": context}

def researcher(state: AgentState):
    print("---RESEARCHING---")
    logs = run_research(
        task=state.task,
        retrieved_context=state.retrieved_context,
        llm=ensure_llm(),
    )
    return {"research_logs": logs, "status": "planning"}

def planner(state: AgentState):
    print("---PLANNING---")
    
    research_context = "\n\nResearch Notes:\n" + "\n".join(state.research_logs) if state.research_logs else ""
    
    chain = planning_prompt() | ensure_llm() | StrOutputParser()
    plan_text = chain.invoke({
        "task": state.task, 
        "context": state.retrieved_context,
        "research_context": research_context
    })
    # Simple splitting by newline for now
    plan = [line.strip() for line in plan_text.split('\n') if line.strip()]
    return {"plan": plan, "status": "coding"}

def coder(state: AgentState):
    print("---CODING---")
    
    research_notes = "\n".join(state.research_logs) if state.research_logs else ""
    reflection_text = state.history[-1].reflection if state.history and state.history[-1].reflection else ""

    input_variables = {
        "task": state.task,
        "plan": "\n".join(state.plan),
        "code": state.current_code,
        "reflections": str([m.error for m in state.history if m.error]),
        "research_notes": research_notes,
        "reflection": reflection_text,
    }

    chain = coding_prompt() | ensure_llm() | StrOutputParser()
    code = chain.invoke(input_variables)
    
    # Clean code (remove markdown if present)
    code = code.replace("```python", "").replace("```", "").strip()
    
    return {"current_code": code, "status": "executing", "iteration": state.iteration + 1}

def executor(state: AgentState):
    print("---EXECUTING---")
    # Safety Check
    is_safe, reason = Safety.check(state.current_code)
    if not is_safe:
        print(f"Safety Violation: {reason}")
        return {
            "history": state.history + [TaskMemory(code=state.current_code, output="", error=f"Safety Violation: {reason}")],
            "status": "reflecting"
        }
    
    # Sandbox Run
    sandbox = Sandbox()
    result = sandbox.run(state.current_code)
    
    print(f"Execution Output: {result['output']}")
    print(f"Execution Error: {result['error']}")

    memory = TaskMemory(
        code=state.current_code,
        output=result["output"],
        error=result["error"]
    )
    
    # Decide next step
    if result["error"]:
        return {"history": state.history + [memory], "status": "reflecting"}
    else:
        # Success!
        return {"history": state.history + [memory], "status": "finished"}

def reflector(state: AgentState):
    print("---REFLECTING---")
    last_memory = state.history[-1]
    
    chain = reflection_prompt() | ensure_llm() | StrOutputParser()
    reflection = chain.invoke({
        "code": last_memory.code,
        "error": last_memory.error,
        "output": last_memory.output
    })
    
    updated_memory = last_memory.model_copy(update={"reflection": reflection})
    new_history = state.history[:-1] + [updated_memory]
    
    return {"history": new_history, "status": "coding"}

def save_memory(state: AgentState):
    print("---SAVING MEMORY---")
    ensure_memory_store().store_success(state.task, state.current_code)
    
    # Store failures from history if any
    for mem in state.history:
        if mem.error:
            ensure_memory_store().store_failure(
                error=mem.error,
                failed_code=mem.code,
                fix=state.current_code,
                task=state.task
            )
    return {"status": "finished"}
