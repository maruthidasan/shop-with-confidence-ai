"""Gemini-powered senior fashion stylist service."""

from services.gemini_service import GeminiService, SYSTEM_PROMPT


class GeminiStylistService(GeminiService):
    """Provides product ranking and stylist communication through Gemini."""

    def build_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def recommend_products(
        self,
        context,
        photo_url,
        candidates,
    ):
        """
        Send the original customer photo, style context, and catalog candidates
        to Gemini for visual/appearance-aware fashion recommendations.
        """
        return await self.generate_stylist_edit(
            context,
            photo_url,
            candidates,
        )
