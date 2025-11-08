from fastapi import APIRouter
from pydantic import BaseModel
from app.services.trainer import TrainingService

router = APIRouter(prefix="/train", tags=["training"])


class TrainRequest(BaseModel):
    target: str
    job_id: str | None = None
    params: dict | None = None


class TrainResponse(BaseModel):
    run_id: str
    metrics: dict


@router.post("", response_model=TrainResponse)
async def train(request: TrainRequest) -> TrainResponse:
    service = TrainingService()
    result = service.train_model(request.target, request.job_id, request.params or {})
    return TrainResponse(run_id=result.run_id, metrics=result.metrics)
