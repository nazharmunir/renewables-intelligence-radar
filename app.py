from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.market_intelligence import MarketIntelligencePipeline


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "public_updates.csv"

st.set_page_config(
    page_title="Renewables Intelligence Radar",
    page_icon="⚡",
    layout="wide",
)

@st.cache_data
def load_signals() -> pd.DataFrame:
    pipeline = MarketIntelligencePipeline()
    raw = pipeline.load(DATA_PATH)
    return pipeline.enrich(raw).signals

signals = load_signals()

st.title("Renewables Intelligence Radar")
st.caption(
    "An independent market-intelligence prototype that transforms public regulatory, "
    "competitor, supplier and electricity-market updates into prioritised strategic signals."
)

st.info(
    "Portfolio demonstration based solely on public information. "
    
)

with st.sidebar:
    st.header("Filters")
    selected_markets = st.multiselect(
    "Market",
    sorted(signals["market"].unique()),
    default=["Germany", "Europe", "North Sea"]
)
    selected_categories = st.multiselect(
    "Category",
    sorted(signals["category"].unique()),
    default=[
        "Regulation & Policy",
        "Power Market & Grid",
        "Competitor & Portfolio"
    ]
)
    selected_urgencies = st.multiselect(
    "Urgency",
    ["High", "Medium", "Low"],
    default=["High", "Medium"]
)
    minimum_score = st.slider("Minimum strategic score", 0, 100, 40)

filtered = signals[
    signals["market"].isin(selected_markets)
    & signals["category"].isin(selected_categories)
    & signals["urgency"].isin(selected_urgencies)
    & (signals["strategic_relevance_score"] >= minimum_score)
].copy()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Signals", len(filtered))
metric_2.metric("High urgency", int((filtered["urgency"] == "High").sum()))
metric_3.metric(
    "Average score",
    f"{filtered['strategic_relevance_score'].mean():.0f}" if len(filtered) else "–"
)
metric_4.metric("Markets covered", filtered["market"].nunique())

left, right = st.columns(2)

with left:
    category_counts = (
        filtered.groupby("category", as_index=False)
        .size()
        .sort_values("size", ascending=False)
    )
    fig_category = px.bar(
        category_counts,
        x="size",
        y="category",
        orientation="h",
        title="Signals by strategic category",
        labels={"size": "Signals", "category": ""},
    )
    st.plotly_chart(fig_category, use_container_width=True)

with right:
    timeline = filtered.copy()
    timeline["month"] = timeline["published_at"].dt.to_period("M").astype(str)
    timeline_counts = timeline.groupby(["month", "category"], as_index=False).size()
    fig_timeline = px.line(
        timeline_counts,
        x="month",
        y="size",
        color="category",
        markers=True,
        title="Signal development over time",
        labels={"size": "Signals", "month": "Month", "category": "Category"},
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

st.subheader("Priority signals")
for row in filtered.sort_values(
    ["strategic_relevance_score", "published_at"],
    ascending=[False, False]
).itertuples(index=False):
    with st.expander(
        f"{row.strategic_relevance_score}/100 · {row.urgency} · {row.title}"
    ):
        st.write(f"**Source:** {row.source} · {row.published_at:%d %B %Y}")
        st.write(f"**Market:** {row.market}")
        st.write(f"**Category:** {row.category}")
        st.write(row.summary)
        st.write(f"**Strategic implication:** {row.strategic_implication}")
        st.write(f"**Suggested action:** {row.recommended_action}")
        st.write(f"**NLP theme:** {row.cluster_theme}")
        st.link_button("Open public source", row.url)

st.subheader("Analysis table")
st.dataframe(
    filtered[
        [
            "published_at", "source", "market", "category", "urgency",
            "strategic_relevance_score", "title", "cluster_theme"
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
