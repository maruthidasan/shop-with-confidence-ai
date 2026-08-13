"""Perfect Corp / YouCam provider adapter; exact tenant endpoints live only in environment configuration."""
import logging

import httpx

from config import Settings
from services.errors import ProviderConfigurationError, ProviderError

logger = logging.getLogger(__name__)


class YouCamService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _headers(self) -> dict[str, str]:
        if not self._settings.youcam_api_key:
            raise ProviderConfigurationError("The virtual fitting service is not configured yet.")
        return {self._settings.youcam_auth_header: f"{self._settings.youcam_auth_prefix}{self._settings.youcam_api_key}"}

    async def analyze_skin(self, photo_url: str) -> dict[str, str]:
        logger.info("skin_analysis_started")
        if self._settings.ai_mode != "live":
            result = {"undertone": "neutral", "recommendedPalette": "deep navy and soft neutrals"}
        else:
            if not self._settings.youcam_skin_analysis_url:
                raise ProviderConfigurationError("The skin analysis endpoint is not configured yet.")
            result = await self._post(self._settings.youcam_skin_analysis_url, {"src_file_url": photo_url})
        logger.info("skin_analysis_completed")
        return {"undertone": str(result.get("undertone", "neutral")), "recommendedPalette": str(result.get("recommendedPalette", result.get("recommended_palette", "deep navy and soft neutrals")))}

    async def virtual_tryon(self, photo_url: str, recommendation_id: str, garment_image_url: str | None = None) -> str:
        logger.info("virtual_tryon_started recommendation_id=%s", recommendation_id)
        if self._settings.ai_mode != "live":
            image_url = f"https://placehold.co/1200x1600?text=Your+Look+{recommendation_id}"
        else:
            if not self._settings.youcam_clothes_tryon_url or not garment_image_url:
                raise ProviderConfigurationError("The virtual fitting service needs its configured endpoint and product image.")
            result = await self._post(self._settings.youcam_clothes_tryon_url, {"src_file_url": photo_url, "ref_file_url": garment_image_url, "garment_category": "auto"})
            image_url = str(result.get("result_url") or result.get("image_url") or "")
            if not image_url:
                raise ProviderError("The virtual fitting preview could not be prepared right now.")
        logger.info("virtual_tryon_completed recommendation_id=%s", recommendation_id)
        return image_url

    async def _post(self, url: str, payload: dict[str, str]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("youcam_failure error_type=%s", type(exc).__name__)
            raise ProviderError("The fitting service is temporarily unavailable. Please try again shortly.") from exc
