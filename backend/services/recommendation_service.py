"""AI Stylist orchestration: upload -> YouCam -> Gemini -> VTO."""
import logging
from config import get_settings
from schemas.recommendation import OccasionRequest, Recommendation, RecommendationResponse, TryOnRequest, TryOnResponse
from services.accessory_service import AccessoryService
from services.catalog_service import CatalogService
from services.confidence_service import ConfidenceService
from services.customer_context_service import CustomerContextService
from services.gemini_stylist_service import GeminiStylistService
from services.youcam_client import YouCamClient

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, catalog, context, youcam, stylist, confidence, accessories):
        self._catalog = catalog
        self._context = context
        self._youcam = youcam
        self._stylist = stylist
        self._confidence = confidence
        self._accessories = accessories

    async def generate_recommendations(self, request: OccasionRequest, request_id: str | None = None):
        context = self._context.build(request)
        candidates = self._catalog.filter_products(context.occasion, context.category, context.gender)
        if not candidates:
            raise ValueError("No suitable products were found.")

        original_photo_url = str(request.photo_url or "")
        # This is the one, unchanged customer image used by Clothes VTO.
        photo_reference = await self._youcam.upload_file(original_photo_url)
        logger.info("full_body_photo_reference_ready request_id=%s", request_id)

        # Gemini understands the original customer image directly; Perfect Corp
        # Skin Analysis is deliberately not part of this fashion flow.
        edit = await self._stylist.recommend_products(context, original_photo_url, candidates)
        candidate_by_id = {candidate.id: candidate for candidate in candidates}
        accessories = self._accessories.recommend(context.occasion)

        recommendations = []
        for item in edit["recommendations"][:3]:
            candidate = candidate_by_id.get(str(item["id"]))
            if not candidate or not candidate.garment_image_url:
                continue

            preview = await self._youcam.start_virtual_try_on(
                photo_reference,
                candidate.id,
                candidate.garment_image_url,
            )

            recommendations.append(
                Recommendation(
                    id=candidate.id,
                    brand="Vela Original",
                    outfitName=candidate.name,
                    confidence=self._confidence.normalize_confidence(int(item["confidence"])),
                    reason=str(item["reason"]),
                    stylistNote=str(item.get("stylistNote", "")),
                    whyThisSuitsYou=str(item["reason"]),
                    alternativeOption="For a softer alternative, consider the Soft Power Look.",
                    tryOnPreviewUrl=preview,
                    imagePlaceholder=candidate.id,
                    accessories=accessories,
                )
            )

        if not recommendations:
            raise ValueError("No VTO-ready recommendations were returned.")

        report = self._confidence.generate_report(
            int(edit["confidenceScore"]),
            [str(value) for value in edit["selectionReasons"]],
        )

        return RecommendationResponse(
            recommendations=recommendations,
            confidenceReport=report,
            requestId=request_id,
        )

    async def create_tryon(self, request: TryOnRequest, request_id: str | None = None):
        candidate = next(
            (item for item in self._catalog.filter_products("", None, None)
             if item.id == request.recommendation_id),
            None,
        )
        image_url = await self._youcam.start_virtual_try_on(
            str(request.photo_url),
            request.recommendation_id,
            candidate.garment_image_url if candidate else None,
        )
        return TryOnResponse(
            recommendationId=request.recommendation_id,
            imageUrl=image_url,
            requestId=request_id,
        )

def get_recommendation_service():
    settings = get_settings()
    return RecommendationService(
        CatalogService(),
        CustomerContextService(),
        YouCamClient(settings),
        GeminiStylistService(settings),
        ConfidenceService(),
        AccessoryService(),
    )
