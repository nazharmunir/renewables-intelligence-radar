from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


REQUIRED_COLUMNS = {
    "published_at", "source", "source_type", "market", "title", "summary", "url"
}

CATEGORY_KEYWORDS = {
    "Regulation & Policy": {
        "regulation": 16, "regulatory": 16, "consultation": 18, "tender": 16,
        "auction": 15, "approval": 13, "planning permission": 16, "state aid": 16,
        "policy": 12, "pact": 12, "network development plan": 18
    },
    "Competitor & Portfolio": {
        "construction": 10, "installed": 11, "commissioning": 9, "divestment": 15,
        "acquisition": 15, "project": 6, "portfolio": 10, "investment": 10,
        "results": 8, "milestone": 9
    },
    "Supply Chain": {
        "supplier": 13, "order": 14, "turbine": 10, "steel": 10, "blade": 10,
        "service agreement": 12, "delivery": 8, "manufacturing": 12,
        "supply chain": 16
    },
    "Power Market & Grid": {
        "electricity market": 15, "market integration": 14, "grid": 14,
        "price": 10, "generation": 10, "curtailment": 16, "transmission": 13,
        "smard": 12, "security of supply": 15, "market data": 12
    },
    "Technology & Innovation": {
        "recyclable": 15, "lower-carbon": 14, "hydrogen": 12, "battery": 12,
        "innovation": 10, "technology": 8, "digital": 8, "ai": 10,
        "15 mw": 10, "stability": 10
    },
}

SOURCE_PRIORITY = {
    "regulator": 24,
    "system_operator": 21,
    "competitor": 17,
    "supplier": 15,
    "portfolio": 12,
    "research": 14,
    "media": 8,
}

IMPLICATION_TEMPLATES = {
    "Regulation & Policy": (
        "May change permitting, auction design, infrastructure access or project "
        "economics; assumptions and market-entry timing should be reviewed."
    ),
    "Competitor & Portfolio": (
        "Provides a benchmark for competitor execution, capital allocation, project "
        "timelines and strategic focus."
    ),
    "Supply Chain": (
        "May affect turbine availability, supplier concentration, delivery schedules, "
        "technology choices and lifecycle cost."
    ),
    "Power Market & Grid": (
        "Can influence capture prices, congestion, curtailment exposure, connection "
        "timing and long-term power-market assumptions."
    ),
    "Technology & Innovation": (
        "Could improve competitiveness or sustainability, but requires assessment of "
        "maturity, scalability, cost and supplier dependency."
    ),
}


def _normalise_text(parts: Iterable[object]) -> str:
    return " ".join(str(part or "") for part in parts).lower().strip()


def classify_category(text: str, source_type: str) -> tuple[str, int]:
    scores = {category: 0 for category in CATEGORY_KEYWORDS}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword, weight in keywords.items():
            if keyword in text:
                scores[category] += weight

    # Source type gives a transparent prior while content can still override it.
    if source_type == "regulator":
        scores["Regulation & Policy"] += 22
    elif source_type == "system_operator":
        scores["Power Market & Grid"] += 20
    elif source_type in {"competitor", "portfolio"}:
        scores["Competitor & Portfolio"] += 18
    elif source_type == "supplier":
        scores["Supply Chain"] += 20

    category = max(scores, key=scores.get)
    return category, scores[category]


def urgency_from_score(score: int) -> str:
    if score >= 74:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def recommended_action(category: str, urgency: str) -> str:
    prefix = {
        "High": "Escalate for a strategy-team deep dive",
        "Medium": "Track in the next market-intelligence review",
        "Low": "Retain in the knowledge base",
    }[urgency]
    suffix = {
        "Regulation & Policy": "and validate regulatory and project-model assumptions.",
        "Competitor & Portfolio": "and compare implications against the internal pipeline.",
        "Supply Chain": "and assess supplier, technology and schedule exposure.",
        "Power Market & Grid": "and test effects on power-price and grid assumptions.",
        "Technology & Innovation": "and evaluate maturity, economics and scalability.",
    }[category]
    return f"{prefix} {suffix}"


@dataclass
class PipelineResult:
    signals: pd.DataFrame
    cluster_terms: dict[int, str]


class MarketIntelligencePipeline:
    def __init__(self, reference_date: str | pd.Timestamp | None = None):
        self.reference_date = pd.Timestamp(reference_date) if reference_date else None

    def load(self, csv_path: str | Path) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
        if df["published_at"].isna().any():
            bad_rows = df.index[df["published_at"].isna()].tolist()
            raise ValueError(f"Invalid published_at values in rows: {bad_rows}")

        df = (
            df.drop_duplicates(subset=["title", "source"])
              .sort_values("published_at", ascending=False)
              .reset_index(drop=True)
        )
        return df

    def enrich(self, df: pd.DataFrame) -> PipelineResult:
        result = df.copy()
        ref_date = self.reference_date or result["published_at"].max()

        category_values = []
        keyword_scores = []
        strategic_scores = []
        urgencies = []
        implications = []
        actions = []

        for row in result.itertuples(index=False):
            text = _normalise_text([row.title, row.summary, row.source, row.market])
            category, keyword_score = classify_category(text, row.source_type)

            age_days = max((ref_date - row.published_at).days, 0)
            recency_score = max(0, 22 - int(age_days / 12))
            source_score = SOURCE_PRIORITY.get(str(row.source_type), 8)
            market_bonus = 7 if str(row.market) in {
                "Germany", "Europe", "European Union", "North Sea"
            } else 3
            score = min(100, source_score + keyword_score + recency_score + market_bonus)
            urgency = urgency_from_score(score)

            category_values.append(category)
            keyword_scores.append(keyword_score)
            strategic_scores.append(score)
            urgencies.append(urgency)
            implications.append(IMPLICATION_TEMPLATES[category])
            actions.append(recommended_action(category, urgency))

        result["category"] = category_values
        result["keyword_signal_strength"] = keyword_scores
        result["strategic_relevance_score"] = strategic_scores
        result["urgency"] = urgencies
        result["strategic_implication"] = implications
        result["recommended_action"] = actions

        clusters, cluster_terms = self._cluster_topics(result)
        result["topic_cluster"] = clusters
        result["cluster_theme"] = result["topic_cluster"].map(cluster_terms)

        result = result.sort_values(
            ["strategic_relevance_score", "published_at"],
            ascending=[False, False]
        ).reset_index(drop=True)

        return PipelineResult(signals=result, cluster_terms=cluster_terms)

    @staticmethod
    def _cluster_topics(df: pd.DataFrame) -> tuple[list[int], dict[int, str]]:
        documents = (df["title"].fillna("") + ". " + df["summary"].fillna("")).tolist()
        if len(documents) < 4:
            return [0] * len(documents), {0: "general renewables"}

        n_clusters = min(5, max(2, len(documents) // 4))
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=500
        )
        matrix = vectorizer.fit_transform(documents)
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
        labels = model.fit_predict(matrix)

        terms = vectorizer.get_feature_names_out()
        themes: dict[int, str] = {}
        for cluster_id, center in enumerate(model.cluster_centers_):
            top_indices = center.argsort()[-4:][::-1]
            themes[cluster_id] = " · ".join(terms[index] for index in top_indices)

        return labels.tolist(), themes
