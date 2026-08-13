"""Perfect Corp YouCam client for AI Clothes VTO."""
import asyncio
import base64
import logging
from pathlib import Path
from typing import Any

import httpx

from config import Settings
from services.errors import ProviderConfigurationError, ProviderError

logger = logging.getLogger(__name__)

class YouCamClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._garment_file_ids: dict[str, str] = {}

    def _headers(self) -> dict[str, str]:
        if not self._settings.youcam_api_key:
            raise ProviderConfigurationError("The virtual fitting service is not configured yet.")
        return {
            self._settings.youcam_auth_header:
                f"{self._settings.youcam_auth_prefix}{self._settings.youcam_api_key}"
        }

    def _cloth_file_api_url(self) -> str:
        url = self._settings.youcam_clothes_tryon_url
        if not url or "/task/cloth" not in url:
            raise ProviderConfigurationError(
                "The configured Clothes API URL is invalid. Expected a /task/cloth endpoint."
            )
        return url.replace("/task/cloth", "/file/cloth")

    async def _upload_bytes_to_clothes(self, filename: str, content_type: str, data: bytes) -> str:
        return await self._upload_bytes_to_file_api(
            self._cloth_file_api_url(), filename, content_type, data
        )

    async def _upload_bytes_to_file_api(
        self, file_api_url: str, filename: str, content_type: str, data: bytes
    ) -> str:
        if len(data) > 10 * 1024 * 1024:
            raise ProviderError("Image must be smaller than 10 MB.")

        async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
            response = await client.post(
                file_api_url,
                headers={**self._headers(), "Content-Type": "application/json"},
                json={
                    "files": [{
                        "content_type": content_type,
                        "file_name": filename,
                        "file_size": len(data),
                    }]
                },
            )
            response.raise_for_status()
            payload = response.json()
            try:
                info = payload["data"]["files"][0]
                file_id = str(info["file_id"])
                request = info["requests"][0]
                upload_url = request["url"]
                upload_headers = request.get("headers", {})
            except (KeyError, IndexError, TypeError) as exc:
                raise ProviderError("Perfect Corp returned an unexpected file upload response.") from exc

            upload = await client.put(
                upload_url,
                headers=upload_headers,
                content=data,
            )
            upload.raise_for_status()
            return file_id

    async def upload_file(self, photo_url: str) -> str:
        """Upload an image unchanged and return its Perfect Corp Clothes reference."""
        if not photo_url:
            raise ProviderError("A customer photo is required.")

        # Demo mode must remain usable without Perfect Corp credentials. Live mode
        # always uploads data URLs so Clothes VTO receives the original bytes.
        if self._settings.ai_mode != "live":
            return photo_url

        if photo_url.startswith("data:image/"):
            mime, data = self._decode_data_url(photo_url)
            file_id = await self._upload_bytes_to_clothes(
                f"customer-full-body.{self._extension_for_mime(mime)}", mime, data
            )
            return f"file:{file_id}"

        # Public URLs are also supported.
        return photo_url

    @staticmethod
    def _decode_data_url(data_url: str) -> tuple[str, bytes]:
        try:
            header, encoded = data_url.split(",", 1)
            mime = header.split(";", 1)[0].split(":", 1)[1].lower()
            if mime not in {"image/jpeg", "image/png", "image/webp"}:
                raise ValueError("unsupported image MIME type")
            return mime, base64.b64decode(encoded, validate=True)
        except (ValueError, IndexError, base64.binascii.Error) as exc:
            raise ProviderError("The uploaded customer photo is invalid.") from exc

    @staticmethod
    def _extension_for_mime(mime: str) -> str:
        return {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[mime]

    async def start_virtual_try_on(
        self,
        photo_reference: str,
        recommendation_id: str,
        garment_image_url: str | None,
    ) -> str:
        if self._settings.ai_mode != "live":
            return f"https://placehold.co/1200x1600?text=Your+Look+{recommendation_id}"

        if not photo_reference:
            raise ProviderError("A customer photo is required for virtual try-on.")
        if not garment_image_url:
            raise ProviderError(f"No original garment reference is configured for {recommendation_id}.")
        if not self._settings.youcam_clothes_tryon_url:
            raise ProviderConfigurationError("The virtual try-on endpoint is not configured yet.")

        ref_file_id = await self._garment_file_id(recommendation_id, garment_image_url)

        payload: dict[str, str] = {
            "garment_category": ("shoes" if recommendation_id == "leather-loafer" else "full_body"),
            "ref_file_id": ref_file_id,
        }
        if photo_reference.startswith("file:"):
            payload["src_file_id"] = photo_reference[5:]
        else:
            payload["src_file_url"] = photo_reference

        result = await self._post(self._settings.youcam_clothes_tryon_url, payload)
        data = result.get("data", result)
        task_id = str(data.get("task_id") or data.get("taskId") or "")
        if not task_id:
            raise ProviderError("Perfect Corp did not return a virtual try-on task ID.")

        result = await self._poll_task(self._settings.youcam_clothes_tryon_url, task_id)
        data = result.get("data", result)
        results = data.get("results", {})
        image_url = (
            results.get("url") or results.get("result_url") or results.get("image_url")
            or data.get("url") or data.get("result_url") or data.get("image_url")
        )
        if not image_url:
            raise ProviderError("Perfect Corp completed the virtual try-on but did not return a result image URL.")
        return str(image_url)

    async def _garment_file_id(self, recommendation_id: str, path_string: str) -> str:
        if recommendation_id in self._garment_file_ids:
            return self._garment_file_ids[recommendation_id]

        path = Path(path_string)
        if not path.exists():
            raise ProviderError(f"Garment reference image was not found: {path}")

        data = path.read_bytes()
        content_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        file_id = await self._upload_bytes_to_clothes(path.name, content_type, data)
        self._garment_file_ids[recommendation_id] = file_id
        return file_id

    async def _poll_task(self, endpoint: str, task_id: str) -> dict[str, Any]:
        task_url = f"{endpoint.rstrip('/')}/{task_id}"
        async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
            for _ in range(30):
                await asyncio.sleep(2)
                response = await client.get(task_url, headers=self._headers())
                response.raise_for_status()
                result = response.json()
                status = result.get("data", {}).get("task_status")
                if status == "success":
                    return result
                if status == "error":
                    data = result.get("data", {})
                    raise ProviderError(
                        f"Perfect Corp task failed: {data.get('error', 'unknown_error')} - "
                        f"{data.get('error_message', 'Unknown provider error.')}"
                    )
        raise ProviderError("Perfect Corp task timed out.")

    async def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers={**self._headers(), "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:1000]
            logger.warning("youcam_post_failure status=%s body=%s", exc.response.status_code, body)
            raise ProviderError("The fitting service rejected the request.") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("The fitting service is temporarily unavailable.") from exc
