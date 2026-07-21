# Renewables Intelligence Radar

A practical market-intelligence prototype that turns scattered public renewable-energy updates into structured, prioritised insights.

🔗 **Live demo:** https://renewables-intelligence-radar.streamlit.app  
💻 **GitHub:** https://github.com/nazharmunir/renewables-intelligence-radar

## The idea behind the project

Renewable-energy strategy teams follow information from many different sources: regulators, system operators, competitors, suppliers and market authorities.

Finding the information is usually not the hardest part. The real challenge is:

- deciding which updates are actually important;
- understanding how they may affect the market;
- comparing developments across different sources;
- and communicating the findings clearly to decision-makers.

I built the Renewables Intelligence Radar to explore how this process could be partially automated using Python, transparent scoring rules and NLP.

The prototype collects structured public updates, validates and classifies them, calculates their strategic relevance and presents the results through an interactive dashboard and executive brief.

> This is an independent portfolio project created by Muhammad Mazhar Munir. It is based entirely on publicly available information and is not commissioned by, affiliated with or representative of Vattenfall or any other organisation included in the dataset.

## How it works

```text
Public market updates
        ↓
Data validation and duplicate removal
        ↓
Strategic category classification
        ↓
Relevance scoring based on source, keywords, recency and market
        ↓
NLP-based topic clustering
        ↓
Interactive dashboard and executive intelligence brief
