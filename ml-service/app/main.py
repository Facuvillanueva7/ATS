from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ai, training

app = FastAPI(title="ATS ML Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)

app.include_router(ai.router)
app.include_router(training.router)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
