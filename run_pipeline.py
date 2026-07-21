from pathlib import Path

from src.market_intelligence import MarketIntelligencePipeline
from src.newsletter import build_executive_brief


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "public_updates.csv"
OUTPUT_CSV = ROOT / "outputs" / "prioritised_signals.csv"
OUTPUT_HTML = ROOT / "outputs" / "executive_brief.html"


def main() -> None:
    pipeline = MarketIntelligencePipeline()
    raw = pipeline.load(DATA_PATH)
    result = pipeline.enrich(raw)

    result.signals.to_csv(OUTPUT_CSV, index=False)
    build_executive_brief(result.signals, OUTPUT_HTML)

    print(f"Processed {len(result.signals)} public updates.")
    print(f"Signals: {OUTPUT_CSV}")
    print(f"Executive brief: {OUTPUT_HTML}")
    print("\nTop signals:")
    print(
        result.signals[
            ["strategic_relevance_score", "urgency", "category", "title"]
        ].head(5).to_string(index=False)
    )


if __name__ == "__main__":
    main()
