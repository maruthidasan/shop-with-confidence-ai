from fastapi.testclient import TestClient
import base64

from main import app


def test_health_check() -> None:
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP", "service": "shop-with-confidence-api"}


def test_recommendation_route_returns_a_demo_edit_without_provider_credentials(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "mock")
    from config import get_settings
    get_settings.cache_clear()
    photo = "data:image/png;base64," + base64.b64encode(b"demo-image").decode()
    response = TestClient(app).post(
        "/api/recommend",
        json={"occasion": "Interview", "photoUrl": photo, "gender": "Men"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendations"]) == 3
    assert all(item["tryOnPreviewUrl"] for item in body["recommendations"])


def test_complete_the_look_route_returns_a_demo_vto(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "mock")
    from config import get_settings
    get_settings.cache_clear()
    response = TestClient(app).post(
        "/api/tryon",
        json={"recommendationId": "leather-loafer", "photoUrl": "https://example.test/look.jpg"},
    )

    assert response.status_code == 200
    assert "leather-loafer" in response.json()["imageUrl"]
