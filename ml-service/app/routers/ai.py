from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedder import EmbeddingStrategy, OpenAIEmbeddingStrategy, LocalEmbeddingStrategy
from app.services.matcher import cosine_match
from app.services.ner import ner_extract
from app.services.predictor import PredictorService

router = APIRouter(prefix="/", tags=["ai"])


class ParseRequest(BaseModel):
    text: str


class ParseResponse(BaseModel):
    entities: dict
    summary: str | None = None


class EmbedRequest(BaseModel):
    text: str
    type: str = "candidate"


class EmbedResponse(BaseModel):
    vector: list[float]


class MatchRequest(BaseModel):
    candidate_vector: list[float]
    job_vector: list[float]


class MatchResponse(BaseModel):
    score: float
    top_features: list[str]


class PredictRequest(BaseModel):
    features: dict
    model: str = "interview"


class PredictResponse(BaseModel):
    yhat: float
    shap_factors: dict[str, float]


@router.post("parse", response_model=ParseResponse)
async def parse_cv(request: ParseRequest) -> ParseResponse:
    entities = ner_extract(request.text)
    return ParseResponse(entities=entities, summary=entities.get("summary"))


@router.post("embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest) -> EmbedResponse:
    strategy: EmbeddingStrategy
    if request.type == "candidate":
        strategy = OpenAIEmbeddingStrategy()
    else:
        strategy = LocalEmbeddingStrategy()
    vector = await strategy.embed(request.text)
    return EmbedResponse(vector=vector)


@router.post("match", response_model=MatchResponse)
async def match(request: MatchRequest) -> MatchResponse:
    score, factors = cosine_match(request.candidate_vector, request.job_vector)
    return MatchResponse(score=score, top_features=factors)


@router.post("predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    predictor = PredictorService()
    try:
        result = predictor.predict(request.model, request.features)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return PredictResponse(yhat=result.yhat, shap_factors=result.shap)
