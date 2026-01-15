# API

## Run Server

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

## Endpoints

### GET /health

Returns a basic health response.

### POST /run

Body:

```json
{
  "task": "Write a python script to calculate the 10th Fibonacci number",
  "max_iterations": 10
}
```

Response includes the final plan, code, and execution history.

