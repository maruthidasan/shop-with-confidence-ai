import asyncio
import base64
import logging
import os
from types import SimpleNamespace

import httpx
from schemas.recommendation import OccasionRequest
from services.catalog_service import CatalogCandidate
from services.confidence_service import ConfidenceService
from services.customer_context_service import CustomerContext
from services.gemini_service import GeminiService
from services.recommendation_service import RecommendationService


def test_gemini_visual_input_preserves_original_upload_bytes():
    original_bytes = b"original-full-body-bytes"
    photo_url = "data:image/png;base64," + base64.b64encode(original_bytes).decode("ascii")

    image_part = GeminiService._image_part_from_data_url(photo_url)

    assert image_part.inline_data.mime_type == "image/png"
    assert image_part.inline_data.data == original_bytes


def test_gemini_stylist_config_disables_afc_and_bounds_failures():
    from config import Settings

    config = GeminiService(Settings(GEMINI_TIMEOUT_MS=20_000, GEMINI_RETRY_ATTEMPTS=2))._generation_config()

    assert config.automatic_function_calling.disable is True
    assert config.http_options.timeout == 20_000
    assert config.http_options.retry_options.attempts == 2
    assert config.http_options.retry_options.http_status_codes == [503]
    assert config.http_options.retry_options.jitter == 0.1
    assert config.max_output_tokens == 1200


def test_gemini_prefers_sdk_parsed_structured_response_and_rejects_unknown_catalog_ids():
    from config import Settings

    candidates = [CatalogCandidate(f"look-{i}", "Look", "Business", "Interview", "Navy", "Wool", 100) for i in range(1, 4)]
    response = SimpleNamespace(
        parsed={
            "recommendations": [{"id": f"look-{i}", "confidence": 90, "reason": "Fits", "stylistNote": "Polished"} for i in range(1, 4)],
            "selectionReasons": ["Occasion fit"],
            "confidenceScore": 90,
        },
        text="not valid JSON and intentionally ignored",
    )

    payload = GeminiService(Settings())._parse_stylist_response(response, candidates)

    assert payload["recommendations"][0]["id"] == "look-1"


def test_gemini_recovers_only_fenced_json_when_sdk_parsed_is_unavailable():
    from config import Settings

    candidates = [CatalogCandidate(f"look-{i}", "Look", "Business", "Interview", "Navy", "Wool", 100) for i in range(1, 4)]
    response = SimpleNamespace(
        parsed=None,
        text='```json\n{"recommendations":[{"id":"look-1","confidence":90,"reason":"Fits","stylistNote":"Polished"},{"id":"look-2","confidence":90,"reason":"Fits","stylistNote":"Polished"},{"id":"look-3","confidence":90,"reason":"Fits","stylistNote":"Polished"}],"selectionReasons":["Occasion fit"],"confidenceScore":90}\n```',
    )

    payload = GeminiService(Settings())._parse_stylist_response(response, candidates)

    assert payload["confidenceScore"] == 90


def test_gemini_falls_back_after_primary_read_timeout(caplog):
    from config import Settings

    caplog.set_level(logging.INFO)

    candidates = [
        CatalogCandidate(f"look-{i}", "Look", "Business", "Interview", "Navy", "Wool", 100)
        for i in range(1, 4)
    ]
    response = SimpleNamespace(
        parsed={
            "recommendations": [
                {"id": f"look-{i}", "confidence": 90, "reason": "Fits"}
                for i in range(1, 4)
            ],
            "selectionReasons": ["Occasion fit"],
            "confidenceScore": 90,
        },
        text="",
    )

    class Models:
        def __init__(self):
            self.models = []

        async def generate_content(self, *, model, **kwargs):
            self.models.append(model)
            if model == "primary-model":
                raise httpx.ReadTimeout("read timed out")
            return response

    class Client:
        def __init__(self):
            self.models = Models()
            self.aio = SimpleNamespace(models=self.models)

    service = GeminiService(
        Settings(
            GEMINI_MODEL="primary-model",
            GEMINI_FALLBACK_MODEL="gemini-2.5-flash",
        )
    )
    client = Client()

    payload = asyncio.run(
        service._generate_with_resilience(
            client, [], candidates, CustomerContext("Interview", None, "Men", ())
        )
    )

    assert payload["confidenceScore"] == 90
    assert client.models.models == ["primary-model", "gemini-2.5-flash"]
    assert "gemini_primary_failed" in caplog.text
    assert "gemini_fallback_started" in caplog.text
    assert "gemini_fallback_succeeded" in caplog.text


def test_gemini_uses_catalogue_degradation_after_both_models_fail_transiently(caplog):
    from config import Settings

    caplog.set_level(logging.INFO)
    candidates = [
        CatalogCandidate(f"look-{i}", f"Look {i}", "Business", "Interview", "Navy", "Wool", 100)
        for i in range(1, 4)
    ]

    class Models:
        def __init__(self):
            self.models = []

        async def generate_content(self, *, model, **kwargs):
            self.models.append(model)
            raise httpx.ReadTimeout("read timed out")

    class Client:
        def __init__(self):
            self.models = Models()
            self.aio = SimpleNamespace(models=self.models)

    service = GeminiService(
        Settings(
            GEMINI_MODEL="primary-model",
            GEMINI_FALLBACK_MODEL="fallback-model",
        )
    )
    client = Client()
    payload = asyncio.run(
        service._generate_with_resilience(
            client, [], candidates, CustomerContext("Interview", None, "Men", ())
        )
    )

    assert client.models.models == ["primary-model", "fallback-model"]
    assert [item["id"] for item in payload["recommendations"]] == [
        "look-1", "look-2", "look-3"
    ]
    assert payload["confidenceScore"] == 84
    assert "stylist_graceful_degradation_used" in caplog.text


def test_recommendation_flow_sends_original_to_gemini_and_vto_without_skin_analysis():
    candidate = CatalogCandidate(
        "look-1", "Look One", "Business Wear", "Interview", "Navy", "Wool", 100,
        garment_image_url="garment.jpg",
    )

    class Context:
        def build(self, request):
            return CustomerContext(request.occasion, request.category, request.gender, ())

    class Catalog:
        def filter_products(self, *args):
            return [candidate]

    class YouCam:
        def __init__(self):
            self.uploaded_photos = []
            self.vto_references = []

        async def upload_file(self, photo_url):
            self.uploaded_photos.append(photo_url)
            return "file:original"

        async def start_virtual_try_on(self, reference, recommendation_id, garment_image_url):
            self.vto_references.append(reference)
            return "https://example.test/vto-result.jpg"

    class Stylist:
        def __init__(self):
            self.photo_urls = []

        async def recommend_products(self, context, photo_url, candidates):
            self.photo_urls.append(photo_url)
            return {"recommendations": [{"id": "look-1", "confidence": 88, "reason": "Great fit"}], "confidenceScore": 88, "selectionReasons": ["fit"]}

    class Accessories:
        def recommend(self, occasion):
            return []

    youcam = YouCam()
    stylist = Stylist()
    original_photo = "data:image/png;base64," + base64.b64encode(b"original-full-body-bytes").decode("ascii")
    service = RecommendationService(Catalog(), Context(), youcam, stylist, ConfidenceService(), Accessories())
    asyncio.run(service.generate_recommendations(OccasionRequest(occasion="Interview", photoUrl=original_photo)))

    assert youcam.uploaded_photos == [original_photo]
    assert stylist.photo_urls == [original_photo]
    assert youcam.vto_references == ["file:original"]


def test_leather_loafer_uses_shoes_and_the_original_vto_file_reference():
    from config import Settings
    from services.youcam_client import YouCamClient

    class TryOnClient(YouCamClient):
        def __init__(self):
            super().__init__(Settings(
                AI_MODE="live", YOUCAM_API_KEY="test-key",
                YOUCAM_CLOTHES_TRYON_URL="https://example.test/s2s/v2.1/task/cloth",
            ))
            self.payload = None

        async def _garment_file_id(self, recommendation_id, path_string):
            return "loafer-garment-file"

        async def _post(self, url, payload):
            self.payload = payload
            return {"data": {"task_id": "tryon-task"}}

        async def _poll_task(self, endpoint, task_id):
            return {"data": {"results": {"url": "https://example.test/look.jpg"}}}

    client = TryOnClient()
    asyncio.run(client.start_virtual_try_on("file:original-full-body", "leather-loafer", "loafer.jpg"))

    assert client.payload == {
        "garment_category": "shoes",
        "ref_file_id": "loafer-garment-file",
        "src_file_id": "original-full-body",
    }


def test_cross_vto_loafer_reference_is_backend_local_in_production_style_cwd(tmp_path):
    from services.catalog_service import CatalogService

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        loafer = next(
            item for item in CatalogService().filter_products("", None, None)
            if item.id == "leather-loafer"
        )
        assert loafer.garment_image_url is not None
        assert not loafer.garment_image_url.startswith("../frontend/")
        assert os.path.isfile(loafer.garment_image_url)
    finally:
        os.chdir(original_cwd)
