import chromadb
from chromadb.utils import embedding_functions
import uuid
from typing import List, Dict, Any

class Memory:
    def __init__(self, db_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Uses default all-MiniLM-L6-v2
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.failures = self.client.get_or_create_collection(
            name="failure_patterns",
            embedding_function=self.embedding_fn
        )
        self.successes = self.client.get_or_create_collection(
            name="success_patterns",
            embedding_function=self.embedding_fn
        )

    def store_failure(self, error: str, failed_code: str, fix: str, task: str):
        """Stores a failure pattern (error + task) and its fix."""
        self.failures.add(
            documents=[f"Task: {task}\nError: {error}"],
            metadatas=[{"failed_code": failed_code, "fix": fix, "error": error, "task": task}],
            ids=[str(uuid.uuid4())]
        )

    def retrieve_similar_failures(self, task: str, error: str = "") -> List[Dict[str, Any]]:
        """Retrieves similar past failures to avoid repeating them."""
        query = f"Task: {task}\nError: {error}"
        results = self.failures.query(
            query_texts=[query],
            n_results=3
        )
        
        # Flatten results
        output = []
        if results['metadatas'] and results['metadatas'][0]:
            for meta in results['metadatas'][0]:
                output.append(meta)
        return output

    def store_success(self, task: str, code: str):
        """Stores a successful solution."""
        self.successes.add(
            documents=[task],
            metadatas=[{"code": code, "task": task}],
            ids=[str(uuid.uuid4())]
        )
