import pandas as pd

from src.market_intelligence import (
    MarketIntelligencePipeline,
    classify_category,
    urgency_from_score,
)


def test_regulatory_item_classification():
    category, score = classify_category(
        "regulator launches consultation on wind tender and network development plan",
        "regulator",
    )
    assert category == "Regulation & Policy"
    assert score > 20


def test_urgency_thresholds():
    assert urgency_from_score(74) == "High"
    assert urgency_from_score(50) == "Medium"
    assert urgency_from_score(49) == "Low"


def test_enrichment_produces_valid_scores():
    df = pd.DataFrame([{
        "published_at": pd.Timestamp("2026-07-01"),
        "source": "Example regulator",
        "source_type": "regulator",
        "market": "Germany",
        "title": "Consultation opens for offshore wind tender",
        "summary": "The regulator is reviewing auction design and grid access.",
        "url": "https://example.com",
    }])
    result = MarketIntelligencePipeline("2026-07-02").enrich(df).signals
    assert 0 <= int(result.iloc[0]["strategic_relevance_score"]) <= 100
    assert result.iloc[0]["urgency"] in {"High", "Medium", "Low"}
