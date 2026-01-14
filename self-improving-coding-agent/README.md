# Self-Improving Coding Agent

A coding agent that can iteratively plan, write code, execute it (safely), and fix its own errors using an LLM.

## Prerequisites

- **Python 3.10+**
- **Docker** (Recommended for sandboxed execution)
  - If Docker is not available, the agent will fall back to local execution (with a warning).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd self-improving-coding-agent
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, ensure you have the necessary packages like `langchain`, `langgraph`, `openai`, `chromadb`, `typer`, `docker`, `python-dotenv` installed.)*

## Configuration

1.  Create a `.env` file in the project root:
    ```bash
    touch .env
    ```

2.  Add your API key to `.env`. The agent supports OpenRouter, Anthropic, and OpenAI.
    ```env
    # Example for OpenRouter
    OPENROUTER_API_KEY=your_api_key_here
    
    # Or for Anthropic
    # ANTHROPIC_API_KEY=your_api_key_here
    
    # Or for OpenAI
    # OPENAI_API_KEY=your_api_key_here
    ```

## Usage

### Local Usage

Run the agent with a task description:

```bash
python main.py "Write a python script to calculate the 10th Fibonacci number"
```

### Docker Usage

You can also run the agent entirely within Docker. This is useful for deployment or ensuring a consistent environment.

1.  **Build the image**:
    ```bash
    docker-compose build
    ```

2.  **Run a task**:
    ```bash
    docker-compose run agent "Write a python script to calculate the 10th Fibonacci number"
    ```

    *Note: The `docker-compose.yml` mounts `/var/run/docker.sock`, allowing the agent inside the container to spawn sibling containers for safe code execution.*

## How it Works

The agent will:
1.  **Plan** the implementation.
2.  **Code** the solution.
3.  **Execute** the code in a sandbox (or locally if Docker is missing).
4.  **Reflect** on any errors and fix them automatically.
5.  **Save** successful patterns to memory for future tasks.
