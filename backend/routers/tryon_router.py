from fastapi import APIRouter, Depends, Request

from schemas.recommendation import TryOnRequest, TryOnResponse
from services.recommendation_service import RecommendationService, get_recommendation_service

router = APIRouter(prefix="/api/tryon", tags=["Virtual Try-On"])


@router.post("", response_model=TryOnResponse)
async def try_on(payload: TryOnRequest, request: Request, service: RecommendationService = Depends(get_recommendation_service)) -> TryOnResponse:
    return await service.create_tryon(payload, request.state.request_id)
