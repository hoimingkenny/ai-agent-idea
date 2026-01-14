from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .state import AgentState, TaskMemory
from ..sandbox.runner import Sandbox
from ..utils.safety import Safety
from ..memory.vector_store import Memory
import os

# Initialize Memory
memory_store = Memory()

# flexible model init
def get_llm():
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    elif os.getenv("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="xiaomi/mimo-v2-flash:free",
            temperature=0
        )
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4-turbo", temperature=0)
    else:
        return None

_llm = None

def ensure_llm():
    global _llm
    if _llm is None:
        _llm = get_llm()
        if _llm is None:
            raise ValueError("No API key found for OpenAI, Anthropic, or OpenRouter. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY.")
    return _llm

def retrieve_memory(state: AgentState):
    print("---RETRIEVING MEMORY---")
    failures = memory_store.retrieve_similar_failures(state.task)
    context = ""
    if failures:
        context = "Past Failures/Lessons:\n" + "\n".join(
            [f"- Error: {f.get('error')}\n  Fix: {f.get('fix')}" for f in failures]
        )
    return {"retrieved_context": context}

def planner(state: AgentState):
    print("---PLANNING---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical lead. Create a step-by-step implementation plan for the following task.\n\nContext from past lessons:\n{context}"),
        ("user", "{task}")
    ])
    chain = prompt | ensure_llm() | StrOutputParser()
    plan_text = chain.invoke({"task": state.task, "context": state.retrieved_context})
    # Simple splitting by newline for now
    plan = [line.strip() for line in plan_text.split('\n') if line.strip()]
    return {"plan": plan, "status": "coding"}

def coder(state: AgentState):
    print("---CODING---")
    
    template = "Task: {task}\nPlan: {plan}\n\nPrevious Code: {code}\n\nReflections/Errors: {reflections}"
    
    messages = [
        ("system", "You are a senior python developer. Write code to solve the task following the plan. Output ONLY the python code, no markdown backticks."),
        ("user", template)
    ]
    
    input_variables = {
        "task": state.task,
        "plan": "\n".join(state.plan),
        "code": state.current_code,
        "reflections": str([m.error for m in state.history if m.error])
    }
    
    # If there is a reflection, add it
    if state.history and state.history[-1].reflection:
        messages.append(("user", "Fix the previous error based on this reflection: {reflection}"))
        input_variables["reflection"] = state.history[-1].reflection

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | ensure_llm() | StrOutputParser()
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
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a debugging expert. Analyze the error and code, and provide a reflection on what went wrong and how to fix it."),
        ("user", "Code:\n{code}\n\nError:\n{error}\n\nOutput:\n{output}")
    ])
    
    chain = prompt | ensure_llm() | StrOutputParser()
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
    # Store success
    memory_store.store_success(state.task, state.current_code)
    
    # Store failures from history if any
    for mem in state.history:
        if mem.error:
            memory_store.store_failure(
                error=mem.error,
                failed_code=mem.code,
                fix=state.current_code,
                task=state.task
            )
    return {"status": "finished"}
