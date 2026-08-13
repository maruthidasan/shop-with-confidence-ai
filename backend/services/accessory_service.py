from schemas.recommendation import Accessory


class AccessoryService:
    def recommend(self, occasion: str) -> list[Accessory]:
        return [
            Accessory(category="Shoes", name="Black leather loafers", reason="I’d pair these with the look to keep the finish clean and grounded."),
            Accessory(category="Watch", name="Minimal silver watch", reason="A slim silver watch adds polish without asking for attention."),
            Accessory(category="Bag", name="Structured leather tote", reason="This keeps the silhouette practical and quietly put together."),
        ]
