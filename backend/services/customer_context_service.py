from dataclasses import dataclass

from schemas.recommendation import OccasionRequest


@dataclass(frozen=True)
class CustomerContext:
    occasion: str
    category: str | None
    gender: str | None
    preferred_colors: tuple[str, ...]


class CustomerContextService:
    def build(self, request: OccasionRequest) -> CustomerContext:
        return CustomerContext(request.occasion, request.category, request.gender, tuple(request.preferred_colors))
