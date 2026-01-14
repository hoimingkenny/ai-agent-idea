import json
import redis.asyncio as redis
from src.core.config import settings
from src.schemas.events import IngestEvent

class QueueService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def push_event(self, event: IngestEvent):
        """Push an event to the Redis list (queue)."""
        # Serialize the Pydantic model to JSON
        event_json = event.model_dump_json()
        await self.redis.rpush(settings.REDIS_QUEUE_NAME, event_json)

    async def pop_event(self) -> IngestEvent | None:
        """Pop an event from the Redis list (queue)."""
        # blpop returns a tuple (key, value) or None if timeout
        # We use a non-blocking lpop for now, or could use blpop in a worker
        data = await self.redis.lpop(settings.REDIS_QUEUE_NAME)
        if data:
            return IngestEvent.model_validate_json(data)
        return None

queue_service = QueueService()
