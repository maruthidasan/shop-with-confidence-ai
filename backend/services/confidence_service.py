from schemas.recommendation import ConfidenceReport


class ConfidenceService:
    def normalize_confidence(self, score: int | float) -> int:
        return min(100, max(0, round(float(score))))

    def build_report(self, score: int, selection_reasons: list[str]) -> ConfidenceReport:
        score = self.normalize_confidence(score)
        return ConfidenceReport(
            score=score,
            title="You Look Great!",
            subtitle="This is a thoughtful choice for the occasion and a look I think you can wear with ease.",
            factors={"skinToneMatch": 5, "occasionMatch": 5, "colorHarmony": 5, "professionalAppearance": 5},
            selectionReasons=selection_reasons,
            overallMatch="A polished, balanced match that feels true to the moment.",
            alternativeLook="For a softer alternative, try the Soft Power Look with a light neutral accessory.",
        )

    generate_report = build_report
