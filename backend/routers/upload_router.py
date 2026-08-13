from fastapi import APIRouter, Request

from schemas.common import APIResponse
from schemas.recommendation import UserPhotoRequest
from security.validation import validate_image_metadata

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("", response_model=APIResponse, status_code=201)
async def upload_photo(payload: UserPhotoRequest, request: Request) -> APIResponse:
    """Mock upload endpoint; binary object storage is intentionally not enabled yet."""
    validate_image_metadata(payload.mime_type)
    return APIResponse(message="Photo accepted for style analysis.", requestId=request.state.request_id)
