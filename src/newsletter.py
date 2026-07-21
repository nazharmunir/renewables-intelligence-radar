from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd


def _badge(urgency: str) -> str:
    return f'<span class="badge {escape(urgency.lower())}">{escape(urgency)}</span>'


def build_executive_brief(
    signals: pd.DataFrame,
    output_path: str | Path,
    title: str = "Renewables Market Intelligence — Executive Signal Brief",
    top_n: int = 8,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    top = signals.head(top_n).copy()
    generated_for = pd.to_datetime(signals["published_at"]).max().strftime("%d %B %Y")

    category_counts = signals["category"].value_counts()
    category_items = "".join(
        f"<li><strong>{escape(category)}</strong>: {int(count)} signals</li>"
        for category, count in category_counts.items()
    )

    cards = []
    for row in top.itertuples(index=False):
        cards.append(f"""
        <article class="signal">
          <div class="meta">
            {_badge(str(row.urgency))}
            <span>{escape(str(row.category))}</span>
            <span>{escape(str(row.market))}</span>
            <span>Score {int(row.strategic_relevance_score)}/100</span>
          </div>
          <h2>{escape(str(row.title))}</h2>
          <p class="source">{escape(str(row.source))} · {row.published_at:%d %b %Y}</p>
          <p>{escape(str(row.summary))}</p>
          <p><strong>Why it matters:</strong> {escape(str(row.strategic_implication))}</p>
          <p><strong>Suggested action:</strong> {escape(str(row.recommended_action))}</p>
          <a href="{escape(str(row.url), quote=True)}">Open public source</a>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
:root {{
  --ink: #14212b;
  --muted: #5c6973;
  --line: #dfe5e8;
  --panel: #f6f8f9;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  color: var(--ink);
  background: white;
  line-height: 1.55;
}}
main {{ max-width: 980px; margin: 0 auto; padding: 48px 28px 72px; }}
header {{ border-bottom: 1px solid var(--line); padding-bottom: 26px; margin-bottom: 26px; }}
h1 {{ font-size: 38px; line-height: 1.1; margin: 0 0 12px; }}
.subtitle {{ color: var(--muted); max-width: 760px; }}
.summary {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px 24px;
  margin: 28px 0;
}}
.signal {{
  border-bottom: 1px solid var(--line);
  padding: 26px 0 30px;
}}
.signal h2 {{ font-size: 23px; line-height: 1.25; margin: 12px 0 5px; }}
.meta {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; color: var(--muted); font-size: 13px; }}
.badge {{ border: 1px solid var(--ink); border-radius: 999px; padding: 3px 9px; font-weight: 700; }}
.source {{ color: var(--muted); margin-top: 0; }}
a {{ color: inherit; font-weight: 700; }}
footer {{ color: var(--muted); font-size: 13px; margin-top: 34px; }}
</style>
</head>
<body>
<main>
<header>
  <h1>{escape(title)}</h1>
  <p class="subtitle">
    An independent demonstration that converts fragmented public renewable-energy
    updates into prioritised, decision-ready signals. It does not represent any
    organisation's internal systems or views.
  </p>
  <p><strong>Reference date:</strong> {generated_for}</p>
</header>
<section class="summary">
  <h2>Portfolio overview</h2>
  <ul>{category_items}</ul>
  <p>
    The ranking is generated using transparent source-priority, keyword-signal and
    recency components. Topic themes are identified using unsupervised NLP clustering.
  </p>
</section>
{''.join(cards)}
<footer>
  Built as an independent portfolio project using public information. Scores and
  implications are analytical demonstrations, not investment advice.
</footer>
</main>
</body>
</html>"""

    output.write_text(html, encoding="utf-8")
    return output
