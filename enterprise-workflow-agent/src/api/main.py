from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import ingest

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingest"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
