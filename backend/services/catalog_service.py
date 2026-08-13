"""Catalog intelligence with original local garment references for the VTO demo."""
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)
ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "vto"

@dataclass(frozen=True)
class CatalogCandidate:
    id: str
    name: str
    category: str
    occasion: str
    color: str
    material: str
    price: int
    available: bool = True
    gender: str = "unisex"
    garment_image_url: str | None = None

class CatalogService:
    _catalog = (
        CatalogCandidate(
            "modern-tailoring", "The Modern Tailoring Edit", "Business Wear",
            "Interview", "Midnight Navy", "Italian wool blend", 268,
            gender="Men", garment_image_url=str(ASSET_ROOT / "modern-tailoring.jpg"),
        ),
        CatalogCandidate(
            "soft-power", "The Soft Power Look", "Business Wear",
            "Interview", "Cream", "Wool crepe", 248,
            gender="Women", garment_image_url=str(ASSET_ROOT / "soft-power.jpg"),
        ),
        CatalogCandidate(
            "understated-statement", "The Understated Statement", "Casual",
            "Business Meeting", "Olive", "Cotton canvas", 212,
            gender="Men", garment_image_url=str(ASSET_ROOT / "understated-statement.jpg"),
        ),
        CatalogCandidate("summer-suit", "Summer Weight Suit", "Business Wear", "Wedding", "Sand", "Linen wool", 392),
        CatalogCandidate("silk-column-dress", "Silk Column Dress", "Women", "Evening", "Soft Fig", "Silk twill", 224),
        CatalogCandidate("polo-knit", "Fine Gauge Polo", "Men", "Date Night", "Forest", "Merino wool", 126),
        CatalogCandidate("leather-loafer", "Black Leather Loafer", "Accessories", "Complete the Look", "Black", "Leather", 184, True, "unisex", str(ASSET_ROOT / "leather-loafer.png")),
    )

    def get_candidates(self, occasion: str, category: str | None = None, gender: str | None = None):
        candidates = [
            item for item in self._catalog
            if item.available and item.occasion.casefold() == occasion.casefold()
        ]
        if category:
            candidates = [item for item in candidates if item.category.casefold() == category.casefold()]
        if gender and gender.casefold() != "unisex":
            candidates = [item for item in candidates if item.gender.casefold() in {"unisex", gender.casefold()}]

        # Keep three recommendations available for the demo.
        if len(candidates) < 3:
            candidates.extend(item for item in self._catalog if item.available and item not in candidates)
        return candidates[:12]

    def filter_products(self, occasion: str, category: str | None = None, gender: str | None = None):
        return self.get_candidates(occasion, category, gender)
