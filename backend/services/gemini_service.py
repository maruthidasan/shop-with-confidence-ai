"""Gemini-powered Senior Fashion Stylist provider."""
import base64
import json
import logging
import asyncio
from pathlib import Path

import httpx
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from config import Settings
from services.catalog_service import CatalogCandidate
from services.customer_context_service import CustomerContext
from services.errors import ProviderConfigurationError, ProviderError

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are the Senior Fashion Stylist for a premium fashion retailer.

Your job is to compare the customer's full-body photo against the supplied catalog product images
and select the best matching clothing products for the customer's occasion.

Only recommend products that genuinely suit the customer.
Select up to three products.
Use ONLY the supplied catalog products.
Do not invent products.
Base the visual comparison on the customer's photo and the supplied catalog product images.
For each recommendation, write one warm, natural stylist reason in two concise sentences.
Explain why the look works for the selected occasion, how the supplied pieces work together,
and include one small practical styling tip when it is grounded in the supplied catalogue.
Never claim knowledge of the customer's body, colouring, fit, or personal attributes unless it is visible
in the supplied image. Do not use generic AI phrasing or sales language.
Always return valid JSON matching the supplied schema.
Do not infer sensitive traits or make medical or skin-health claims.
"""


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "confidence": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["id", "confidence", "reason"],
            },
        },
        "selectionReasons": {
            "type": "array",
            "items": {"type": "string"},
        },
        "confidenceScore": {"type": "integer"},
    },
    "required": ["recommendations", "selectionReasons", "confidenceScore"],
}


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_stylist_edit(
        self,
        context: CustomerContext,
        photo_url: str,
        candidates: list[CatalogCandidate],
    ) -> dict[str, object]:

        if self._settings.ai_mode != "live":
            return self._mock_edit(context, candidates)

        if not self._settings.gemini_api_key:
            raise ProviderConfigurationError(
                "The Gemini stylist service is not configured yet."
            )

        # Only send catalog products for which Gemini can see the actual garment image.
        # Accessories such as the loafer remain part of the later Complete-the-Look flow.
        visual_candidates = [
            item
            for item in candidates
            if item.garment_image_url
            and item.category.casefold() != "accessories"
        ]

        if not visual_candidates:
            raise ProviderError(
                "No image-backed catalog products are available for visual styling."
            )

        candidate_payload = [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "occasion": item.occasion,
                "color": item.color,
                "material": item.material,
                "price": item.price,
            }
            for item in visual_candidates
        ]

        user_payload = {
            "customer_context": context.__dict__,
            "visual_catalog_candidates": candidate_payload,
        }

        prompt = (
            f"{SYSTEM_PROMPT}\n"
            "The first attached image is the customer's original full-body photo.\n"
            "Each following catalog image is preceded by a text label containing its catalog ID.\n"
            "Compare the customer photo with those actual catalog images and select the best "
            "up to three catalog IDs for this occasion.\n"
            "Do not select an ID unless it is present in the supplied visual catalog.\n"
            "Keep every reason to two concise, natural sentences.\n"
            f"{json.dumps(user_payload, ensure_ascii=False)}"
        )

        logger.info(
            "gemini_request operation=stylist_edit primary_model=%s fallback_model=%s "
            "candidate_count=%s visual_candidate_count=%s timeout_ms=%s retry_attempts=%s",
            self._settings.gemini_model,
            self._settings.gemini_fallback_model,
            len(candidates),
            len(visual_candidates),
            self._settings.gemini_timeout_ms,
            self._settings.gemini_retry_attempts,
        )

        try:
            client = genai.Client(api_key=self._settings.gemini_api_key)

            parts: list[types.Part] = [
                types.Part.from_text(text=prompt),
                self._image_part_from_data_url(photo_url),
            ]

            # Associate every actual catalog image with its catalog ID.
            for candidate in visual_candidates:
                parts.append(
                    types.Part.from_text(
                        text=(
                            f"CATALOG PRODUCT IMAGE — id: {candidate.id}; "
                            f"name: {candidate.name}"
                        )
                    )
                )
                parts.append(self._catalog_image_part(candidate))

            return await self._generate_with_resilience(
                client, parts, visual_candidates, context
            )

        except ProviderError:
            raise

        except Exception as exc:
            logger.warning(
                "gemini_failure operation=stylist_edit error_type=%s",
                type(exc).__name__,
            )
            raise ProviderError(
                "The stylist is taking a little longer than expected."
            ) from exc

    async def _generate_with_resilience(
        self,
        client: genai.Client,
        parts: list[types.Part],
        candidates: list[CatalogCandidate],
        context: CustomerContext,
    ) -> dict[str, object]:
        """Retry within a model through the SDK, then fail over only transient outages."""
        models = [self._settings.gemini_model]
        if self._settings.gemini_fallback_model != self._settings.gemini_model:
            models.append(self._settings.gemini_fallback_model)

        primary_model = models[0]
        try:
            payload = await self._generate_for_model(
                client, primary_model, parts, candidates
            )
            logger.info(
                "gemini_success operation=stylist_edit model=%s fallback_used=false",
                primary_model,
            )
            return payload
        except ProviderError:
            raise
        except Exception as primary_error:
            if len(models) == 1 or not self._is_transient_model_error(primary_error):
                raise

            fallback_model = models[1]
            logger.warning(
                "gemini_primary_failed operation=stylist_edit model=%s error_type=%s",
                primary_model,
                type(primary_error).__name__,
            )
            logger.info(
                "gemini_fallback_started operation=stylist_edit model=%s",
                fallback_model,
            )
            try:
                payload = await self._generate_for_model(
                    client, fallback_model, parts, candidates
                )
            except ProviderError:
                raise
            except Exception as fallback_error:
                logger.warning(
                    "gemini_fallback_failed operation=stylist_edit model=%s error_type=%s",
                    fallback_model,
                    type(fallback_error).__name__,
                )
                if self._is_transient_model_error(fallback_error):
                    logger.warning(
                        "stylist_graceful_degradation_used operation=stylist_edit"
                    )
                    return self._deterministic_edit(context, candidates)
                raise fallback_error from primary_error

            logger.info(
                "gemini_fallback_succeeded operation=stylist_edit model=%s",
                fallback_model,
            )
            return payload

    async def _generate_for_model(
        self,
        client: genai.Client,
        model: str,
        parts: list[types.Part],
        candidates: list[CatalogCandidate],
    ) -> dict[str, object]:
        response = await client.aio.models.generate_content(
            model=model,
            contents=[types.Content(role="user", parts=parts)],
            config=self._generation_config(),
        )
        return self._parse_stylist_response(response, candidates)

    @staticmethod
    def _is_transient_model_error(exc: Exception) -> bool:
        """Fail over only on service-unavailable or timeout conditions."""
        if isinstance(
            exc,
            (TimeoutError, asyncio.TimeoutError, httpx.ReadTimeout, httpx.TimeoutException),
        ):
            return True

        if isinstance(exc, genai_errors.ServerError):
            return True

        status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        if status_code in {503, 504}:
            return True

        message = str(exc).upper()
        return any(
            marker in message
            for marker in (
                "503",
                "504",
                "UNAVAILABLE",
                "TIMEOUT",
                "GATEWAY TIMEOUT",
                "SERVERERROR",
                "SERVER ERROR",
            )
        )

    @staticmethod
    def _deterministic_edit(
        context: CustomerContext,
        candidates: list[CatalogCandidate],
    ) -> dict[str, object]:
        """Provide a transparent, catalog-grounded edit after transient AI outages."""
        selected = candidates[:3]
        if len(selected) != 3:
            raise ProviderError(
                "The stylist could not prepare enough catalogue recommendations."
            )

        preference_note = (
            f" and supports your preference for {', '.join(context.preferred_colors)}"
            if context.preferred_colors
            else ""
        )
        recommendations = [
            {
                "id": candidate.id,
                "confidence": max(80, 92 - index * 4),
                "reason": (
                    f"This {candidate.color.lower()} {candidate.material.lower()} piece is "
                    f"available in the catalogue for {context.occasion.lower()}{preference_note}. "
                    f"Its {candidate.category.lower()} styling keeps the look considered and practical."
                ),
                "stylistNote": (
                    "This is a catalogue-based recommendation while live AI styling "
                    "is temporarily unavailable."
                ),
            }
            for index, candidate in enumerate(selected)
        ]
        return {
            "recommendations": recommendations,
            "selectionReasons": [
                f"Selected from the available catalogue for {context.occasion.lower()}.",
                "Ranked using known category, colour, material, and availability data.",
                "Live AI styling is temporarily unavailable; these are deterministic catalogue matches.",
            ],
            "confidenceScore": 84,
        }

    @staticmethod
    def _image_part_from_data_url(photo_url: str) -> types.Part:
        """Create a Gemini inline-image part without changing user-upload bytes."""
        try:
            header, encoded = photo_url.split(",", 1)
            mime_type = header.split(";", 1)[0].split(":", 1)[1].lower()
            if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise ValueError("unsupported image MIME type")
            return types.Part.from_bytes(
                data=base64.b64decode(encoded, validate=True),
                mime_type=mime_type,
            )
        except (ValueError, IndexError, base64.binascii.Error) as exc:
            raise ProviderError("The uploaded customer photo is invalid.") from exc

    @staticmethod
    def _catalog_image_part(candidate: CatalogCandidate) -> types.Part:
        """Read an existing local catalog garment image as Gemini inline bytes."""
        image_path = Path(str(candidate.garment_image_url)).expanduser()

        if not image_path.is_absolute():
            image_path = image_path.resolve()

        if not image_path.is_file():
            raise ProviderError(
                f"Catalog image is missing for product '{candidate.id}'."
            )

        mime_by_suffix = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        mime_type = mime_by_suffix.get(image_path.suffix.lower())

        if not mime_type:
            raise ProviderError(
                f"Unsupported catalog image format for product '{candidate.id}'."
            )

        try:
            image_bytes = image_path.read_bytes()
        except OSError as exc:
            raise ProviderError(
                f"Catalog image could not be read for product '{candidate.id}'."
            ) from exc

        return types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

    def _generation_config(self) -> types.GenerateContentConfig:
        """Bound the live stylist call and explicitly disable unused AFC tools."""
        return types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1200,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            http_options=types.HttpOptions(
                timeout=self._settings.gemini_timeout_ms,
                retry_options=types.HttpRetryOptions(
                    attempts=self._settings.gemini_retry_attempts,
                    initial_delay=0.5,
                    max_delay=1.0,
                    jitter=0.1,
                    http_status_codes=[503],
                ),
            ),
        )

    @staticmethod
    def _parse_stylist_response(
        response: types.GenerateContentResponse,
        candidates: list[CatalogCandidate],
    ) -> dict[str, object]:
        """Prefer SDK-parsed structured output; only recover a fenced JSON body."""
        parsed = response.parsed

        if isinstance(parsed, dict):
            payload = parsed
            logger.info(
                "gemini_response operation=stylist_edit parse_source=sdk_parsed keys=%s",
                sorted(payload.keys()),
            )
        else:
            content = response.text or ""
            normalized = GeminiService._remove_json_fence(content)

            try:
                payload = json.loads(normalized)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "gemini_response_parse_failure operation=stylist_edit "
                    "parsed_type=%s text_length=%s text_preview=%r "
                    "json_error_position=%s",
                    type(parsed).__name__ if parsed is not None else "none",
                    len(content),
                    GeminiService._safe_response_preview(content),
                    exc.pos,
                )
                raise ProviderError(
                    "The stylist returned an invalid structured recommendation response. "
                    "Please try again."
                ) from exc

            logger.info(
                "gemini_response operation=stylist_edit "
                "parse_source=fenced_json_recovery keys=%s",
                sorted(payload.keys()) if isinstance(payload, dict) else [],
            )

        if not isinstance(payload, dict):
            raise ProviderError(
                "The stylist returned an invalid structured recommendation response."
            )

        GeminiService._validate_stylist_payload(payload, candidates)
        return payload

    @staticmethod
    def _remove_json_fence(content: str) -> str:
        content = content.strip()
        if content.startswith("```"):
            first_line_end = content.find("\n")
            if first_line_end != -1 and content.endswith("```"):
                return content[first_line_end + 1:-3].strip()
        return content

    @staticmethod
    def _safe_response_preview(content: str) -> str:
        """Diagnostic-only preview: no request headers, image bytes, or credentials."""
        return " ".join(content.split())[:400]

    @staticmethod
    def _validate_stylist_payload(
        payload: dict[str, object],
        candidates: list[CatalogCandidate],
    ) -> None:
        recommendations = payload.get("recommendations")

        if not isinstance(recommendations, list) or len(recommendations) != 3:
            raise ProviderError("The stylist returned an invalid recommendation list.")

        allowed_ids = {candidate.id for candidate in candidates}

        for recommendation in recommendations:
            if not isinstance(recommendation, dict):
                raise ProviderError("The stylist returned an invalid recommendation item.")

            if recommendation.get("id") not in allowed_ids:
                raise ProviderError(
                    "The stylist returned a recommendation outside the available catalog."
                )

            if not isinstance(recommendation.get("confidence"), int):
                raise ProviderError(
                    "The stylist returned an invalid recommendation confidence."
                )

            if not isinstance(recommendation.get("reason"), str):
                raise ProviderError(
                    "The stylist returned an incomplete recommendation."
                )

        if not isinstance(payload.get("selectionReasons"), list) or not isinstance(
            payload.get("confidenceScore"), int
        ):
            raise ProviderError(
                "The stylist returned an incomplete recommendation response."
            )

    def _mock_edit(
        self,
        context: CustomerContext,
        candidates: list[CatalogCandidate],
    ) -> dict[str, object]:

        selected = candidates[:3]

        recommendations = [
            {
                "id": candidate.id,
                "confidence": 96 - index * 4,
                "reason": (
                    f"The {candidate.color.lower()} tone and "
                    f"{candidate.material.lower()} create a composed, "
                    f"easy finish for {context.occasion.lower()}."
                ),
                "stylistNote": self._stylist_note(
                    candidate,
                    context,
                    index,
                ),
            }
            for index, candidate in enumerate(selected)
        ]

        return {
            "recommendations": recommendations,
            "selectionReasons": [
                "The colour creates a balanced, polished contrast.",
                f"The silhouette is well suited to {context.occasion.lower()}.",
                "The material and proportion keep the look comfortable as well as considered.",
                "Each piece feels intentional without looking over-styled.",
            ],
            "confidenceScore": 96,
        }

    @staticmethod
    def _stylist_note(
        candidate: CatalogCandidate,
        context: CustomerContext,
        index: int,
    ) -> str:

        opening = (
            "I really like this choice for you."
            if index
            else
            "If I were helping you in-store today, "
            "this is honestly the outfit I'd hand you first."
        )

        return (
            f"{opening} The {candidate.color.lower()} works beautifully "
            f"for {context.occasion.lower()} and the "
            f"{candidate.material.lower()} keeps the whole look polished "
            "without feeling overly formal. I think you'll feel "
            "comfortable, confident and authentic wearing it."
        )
        
