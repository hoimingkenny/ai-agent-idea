from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from typing import List, Dict, Any

class DBQueryTool:
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a read-only SQL query.
        """
        # Security check: simplistic prevention of write operations
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")
            
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(text(query), params or {})
                # Convert rows to dicts
                return [dict(row._mapping) for row in result]
            except Exception as e:
                return [{"error": str(e)}]

db_query_tool = DBQueryTool()
