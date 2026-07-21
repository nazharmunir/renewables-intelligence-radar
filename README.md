# Renewables Intelligence Radar

**An independent market-intelligence automation prototype for renewable-energy strategy teams.**

The system converts fragmented public updates from regulators, system operators,
competitors, suppliers and corporate portfolios into prioritised, decision-ready
signals.

> This is an independent portfolio project by Muhammad Mazhar Munir. It is not
> commissioned by, affiliated with, or representative of Vattenfall or any monitored
> organisation. It uses public information and transparent analytical rules.

## Why this project exists

Renewable-energy strategy teams must continuously monitor regulatory changes,
competitor projects, supplier developments, power-market signals and new technologies.
The challenge is not finding information; it is filtering a high volume of updates,
identifying what matters, explaining the strategic implication and distributing a
consistent executive brief.

This prototype demonstrates one possible workflow:

```text
Public updates
      ↓
Validation and deduplication
      ↓
Transparent strategic classification
      ↓
Source + keyword + recency relevance scoring
      ↓
Unsupervised NLP topic clustering
      ↓
Interactive dashboard + executive HTML brief
```

## What it demonstrates

- Python-based data acquisition and transformation
- Data validation and quality controls
- Regulatory, competitor, supplier and market monitoring
- Transparent strategic relevance scoring
- Unsupervised NLP topic discovery using TF-IDF and K-Means
- Interactive Streamlit/Plotly visualisation
- Automated executive newsletter generation
- CSV output suitable for Power BI, Excel or SharePoint workflows
- Reusable RSS adapter for permitted public feeds
- Unit tests for core decision logic

## Project structure

```text
renewables-intelligence-radar/
├── app.py
├── run_pipeline.py
├── requirements.txt
├── config/
│   └── feeds.example.json
├── data/
│   └── public_updates.csv
├── outputs/
│   ├── executive_brief.html
│   └── prioritised_signals.csv
├── src/
│   ├── market_intelligence.py
│   ├── newsletter.py
│   └── rss_ingest.py
└── tests/
    └── test_market_intelligence.py
```

## Run locally

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python run_pipeline.py
streamlit run app.py
```

Open the URL printed by Streamlit, normally `http://localhost:8501`.

## Outputs

Running `python run_pipeline.py` creates:

- `outputs/prioritised_signals.csv` — enriched dataset for analysis or Power BI
- `outputs/executive_brief.html` — management-ready market-intelligence brief

## Scoring logic

The score is intentionally transparent rather than a black box.

```text
Strategic relevance =
    source priority
  + detected strategic keywords
  + recency
  + core-market relevance
```

The result is capped at 100 and mapped to High, Medium or Low urgency. Each signal
also receives:

- a strategic category;
- a short implication;
- a recommended follow-up action;
- an NLP-generated topic theme.

In a production setting, weights would be calibrated with strategy-team feedback,
historical decisions and precision/recall evaluation.

## Public demonstration data

The bundled dataset contains a small set of public 2026 updates from organisations
including Vattenfall, RWE, Ørsted, Vestas, ENTSO-E, the European Commission and the
Bundesnetzagentur. Summaries are paraphrased for this demonstration. Source URLs
are included in the CSV.

The dataset is a portfolio demonstration, not a complete market database.

## Production roadmap

1. Connect approved RSS feeds, subscriptions and paid market-data providers.
2. Store raw and processed records in a governed database.
3. Add source reliability, market materiality and confidence dimensions.
4. Add human feedback to recalibrate relevance scoring.
5. Connect approved generative-AI tooling for source-grounded summaries.
6. Add Power Automate workflows for Teams, SharePoint and newsletter distribution.
7. Add audit trails, monitoring, access control and source-retention policies.

## Business value hypothesis

The prototype is designed to reduce repetitive scanning and formatting, improve
consistency, preserve traceability to sources and help analysts focus attention on
the updates most likely to affect strategy.

No financial-savings claim is made without internal workflow and time-on-task data.
