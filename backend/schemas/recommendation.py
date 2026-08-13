from pydantic import BaseModel, Field, HttpUrl, field_validator


class UserPhotoRequest(BaseModel):
    photo_url: HttpUrl = Field(alias="photoUrl", description="Public or browser-generated URL for the user photo")
    mime_type: str = Field(default="image/jpeg", alias="mimeType")

    model_config = {"populate_by_name": True}

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, value: str) -> str:
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if value not in allowed:
            raise ValueError(f"Unsupported MIME type. Allowed types: {', '.join(sorted(allowed))}")
        return value


class OccasionRequest(BaseModel):
    occasion: str = Field(min_length=2, max_length=80, examples=["Interview"])
    photo_url: str | None = Field(default=None, alias="photoUrl")
    category: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=40)
    preferred_colors: list[str] = Field(default_factory=list, alias="preferredColors")

    model_config = {"populate_by_name": True}


class Accessory(BaseModel):
    category: str
    name: str
    reason: str


class Recommendation(BaseModel):
    id: str
    brand: str
    outfit_name: str = Field(alias="outfitName")
    confidence: int = Field(ge=0, le=100)
    reason: str
    image_placeholder: str = Field(alias="imagePlaceholder")
    accessories: list[Accessory]
    stylist_note: str = Field(default="", alias="stylistNote")
    why_this_suits_you: str = Field(default="", alias="whyThisSuitsYou")
    alternative_option: str = Field(default="", alias="alternativeOption")
    try_on_preview_url: str | None = Field(default=None, alias="tryOnPreviewUrl")

    model_config = {"populate_by_name": True}


class ConfidenceReport(BaseModel):
    score: int = Field(ge=0, le=100)
    title: str
    subtitle: str
    factors: dict[str, int]
    selection_reasons: list[str] = Field(alias="selectionReasons")
    overall_match: str = Field(default="A thoughtful fit for this moment.", alias="overallMatch")
    alternative_look: str = Field(default="", alias="alternativeLook")

    model_config = {"populate_by_name": True}


class RecommendationResponse(BaseModel):
    success: bool = True
    message: str = "Recommendations generated successfully."
    recommendations: list[Recommendation]
    confidence_report: ConfidenceReport = Field(alias="confidenceReport")
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = {"populate_by_name": True}


class TryOnRequest(BaseModel):
    recommendation_id: str = Field(alias="recommendationId", min_length=1)
    photo_url: HttpUrl = Field(alias="photoUrl")

    model_config = {"populate_by_name": True}


class TryOnResponse(BaseModel):
    success: bool = True
    message: str = "Virtual try-on prepared successfully."
    recommendation_id: str = Field(alias="recommendationId")
    image_url: str = Field(alias="imageUrl")
    request_id: str | None = Field(default=None, alias="requestId")

    model_config = {"populate_by_name": True}
