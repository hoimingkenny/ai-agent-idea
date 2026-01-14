import typer
from dotenv import load_dotenv
import os
import sys

# Add current directory to path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.graph import create_graph

load_dotenv()

app = typer.Typer()

@app.command()
def run(task: str, max_iterations: int = 10):
    """
    Run the self-improving coding agent on a task.
    """
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY in .env file or environment variables.")
        return

    print(f"🚀 Starting Agent for task: {task}")
    
    graph = create_graph()
    
    initial_state = {
        "task": task,
        "max_iterations": max_iterations,
        "iteration": 0,
        "plan": [],
        "current_code": "",
        "history": [],
        "status": "planning",
        "retrieved_context": ""
    }
    
    try:
        # Stream the execution
        for event in graph.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"\n📍 Node Completed: {node_name}")
                
                if node_name == "planner":
                    print("📋 Plan:")
                    for i, step in enumerate(state_update.get("plan", [])):
                        print(f"  {i+1}. {step}")
                
                elif node_name == "coder":
                    print("💻 Code Generated (length: {} chars)".format(len(state_update.get("current_code", ""))))
                
                elif node_name == "executor":
                    history = state_update.get("history", [])
                    if history:
                        last_mem = history[-1]
                        if last_mem.error:
                            print(f"❌ Execution Failed: {last_mem.error}")
                        else:
                            print(f"✅ Execution Success!")
                            print(f"Output: {last_mem.output}")
                
                elif node_name == "reflector":
                    history = state_update.get("history", [])
                    if history:
                        print(f"🤔 Reflection: {history[-1].reflection}")
                
                elif node_name == "retrieve_memory":
                    context = state_update.get("retrieved_context", "")
                    if context:
                        print(f"🧠 Retrieved Memory: Found past lessons.")
                    else:
                        print(f"🧠 Retrieved Memory: No relevant past lessons found.")

    except Exception as e:
        print(f"\n💥 Error running agent: {e}")

if __name__ == "__main__":
    app()
