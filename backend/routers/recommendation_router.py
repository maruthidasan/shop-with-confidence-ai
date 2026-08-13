from fastapi import APIRouter, Depends, Request
from schemas.recommendation import OccasionRequest, RecommendationResponse
from services.recommendation_service import RecommendationService, get_recommendation_service

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])

@router.post("", response_model=RecommendationResponse)
async def recommend(
    payload: OccasionRequest,
    request: Request,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    return await service.generate_recommendations(payload, request.state.request_id)
