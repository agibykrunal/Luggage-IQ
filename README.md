# LuggageIQ — Amazon India Competitive Intelligence Dashboard

> A competitive intelligence platform that scrapes, analyses, and visualises customer reviews and pricing data for major luggage brands on Amazon India.

---

## Repository Name & Description

| Field | Recommendation |
|---|---|
| **Repository name** | `luggageiq` |
| **Tagline** | *Competitive intelligence dashboard for luggage brands on Amazon India — sentiment analysis, pricing insights, and agent-generated conclusions from 1,200+ reviews.* |
| **Topics** | `amazon-india` `competitive-intelligence` `sentiment-analysis` `web-scraping` `data-dashboard` `playwright` `fastapi` `nlp` `e-commerce` `luggage` |

---

## Overview

LuggageIQ turns raw Amazon India product listings and customer reviews into a decision-ready competitive intelligence dashboard. It covers 6 major luggage brands — Safari, Skybags, American Tourister, VIP, Aristocrat, and Nasher Miles — and surfaces non-obvious insights that ratings and discounts alone cannot reveal.

### What it answers

- Which brands are priced at a premium versus value-focused price bands?
- Which brands rely on heavy discounting to drive demand — and why that is a weakness signal?
- What do customers consistently praise or complain about, at the aspect level?
- Which brands win on sentiment relative to their price tier?
- What non-obvious conclusions can an AI agent synthesise from the data?

---

## Features

| Module | Description |
|---|---|
| **Market Overview** | KPI strip, price vs list price chart, sentiment vs rating, discount analysis, review volume, theme heatmap |
| **Brand Comparison** | Sortable, filterable side-by-side table with VFM index, scatter plot, and value-for-money chart |
| **Product Drilldown** | Per-product cards with sentiment tags, praise/complaint themes, synthesis, and pricing breakdown |
| **Agent Insights** | 7 AI-synthesised non-obvious conclusions + anomaly detection table |
| **Aspect Analysis** | Attribute-level scoring (Wheels, Handle, Material, Zipper, Size, Durability) with radar and complaint charts |

---

## Project Structure

```
luggageiq/
├── scraper/
│   ├── amazon_scraper.py
│   ├── review_scraper.py
│   └── utils.py
│
├── analysis/
│   ├── sentiment.py
│   ├── theme_extractor.py
│   ├── aspect_sentiment.py
│   ├── anomaly_detector.py
│   └── agent_insights.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── luggage_dataset.csv
│   └── aspect_scores.csv
│
├── dashboard/
│   └── index.html
│
├── backend/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   ├── brands.py
│   │   ├── products.py
│   │   ├── insights.py
│   │   └── pipeline.py
│   └── services/
│       └── data_service.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python 3.11+, Playwright |
| Data processing | Pandas, NumPy |
| Sentiment analysis | VADER (offline) or Claude / OpenAI API |
| Dashboard | Vanilla HTML + CSS + Chart.js (no build step) |
| Backend API | FastAPI + Uvicorn |

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/your-username/luggageiq.git
cd luggageiq
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key if using LLM-based sentiment:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Run the scraper

```bash
python scraper/amazon_scraper.py --brands safari skybags american-tourister vip aristocrat nasher-miles

python scraper/review_scraper.py --input data/raw/products.json --min-reviews 50
```

### 5. Run analysis

```bash
python analysis/sentiment.py --input data/raw/reviews.json --output data/processed
python analysis/theme_extractor.py
python analysis/aspect_sentiment.py
python analysis/anomaly_detector.py
python analysis/agent_insights.py
```

### 6. Open the dashboard

```bash
open dashboard/index.html
```

No server required — the dashboard is a single self-contained HTML file.

### 7. Run the backend API (optional)

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/brands` | List all brands with filters and sorting |
| GET | `/api/brands/{id}` | Single brand detail |
| GET | `/api/products` | List products with filters |
| GET | `/api/products/{id}` | Single product detail |
| GET | `/api/insights` | Agent insights list |
| GET | `/api/insights/anomalies` | Anomaly detection results |
| POST | `/api/pipeline/run` | Trigger full pipeline |
| POST | `/api/pipeline/run/{stage}` | Trigger single analysis stage |
| GET | `/api/pipeline/status` | Pipeline run status |
| GET | `/api/health` | Health check |

---

## Data Schema

### Products (`luggage_dataset.csv`)

| Column | Type | Description |
|---|---|---|
| `brand` | string | Brand name |
| `product_title` | string | Full product name |
| `asin` | string | Amazon ASIN |
| `sell_price` | int | Current selling price (₹) |
| `list_price` | int | MRP / list price (₹) |
| `discount_pct` | float | Discount percentage |
| `rating` | float | Avg star rating |
| `review_count` | int | Total review count |
| `category` | string | Trolley / Backpack / Duffle |
| `sentiment_score` | int | Overall sentiment 0–100 |
| `top_pros` | string | Comma-separated praise themes |
| `top_cons` | string | Comma-separated complaint themes |

### Aspect Scores (`aspect_scores.csv`)

| Column | Type | Description |
|---|---|---|
| `brand` | string | Brand name |
| `wheels` | int | Wheel quality sentiment 0–100 |
| `handle` | int | Handle ergonomics sentiment 0–100 |
| `material` | int | Shell/material sentiment 0–100 |
| `zipper` | int | Zipper quality sentiment 0–100 |
| `size` | int | Size/capacity sentiment 0–100 |
| `durability` | int | Durability sentiment 0–100 |

---

## Sentiment Methodology

Sentiment scoring uses a two-pass approach:

1. **Polarity pass** — Each review is scored positive / neutral / negative using VADER or an LLM prompt. Weighted by review helpfulness votes where available.
2. **Aspect extraction pass** — Reviews are parsed for mentions of key physical attributes. Each mention is scored independently using surrounding context.
3. **Brand-level aggregation** — Scores are aggregated per brand, weighted by recency (reviews from the last 6 months carry 1.5× weight).

The final sentiment score (0–100) is derived entirely from review text — not a transformed star rating — to detect divergence cases.

---

## Limitations

- Amazon India aggressively rate-limits scrapers. The scraper uses random delays (3–8s) and randomised user-agent rotation. Expect ~60–90 minutes for a full scrape across 6 brands.
- List prices on Amazon are set by sellers and may be artificially inflated. Discount percentage is a pricing strategy signal, not a genuine savings metric.
- Aspect sentiment is extracted from review text only — does not incorporate Q&A sections or seller responses.
- Review counts are point-in-time snapshots. Fast-growing brands (e.g. Nasher Miles) may show different profiles within weeks.

---

## Evaluation Rubric (Assignment Reference)

| Criteria | Implementation |
|---|---|
| Data collection quality | Playwright scraper with structured JSON output, documented schema |
| Analytical depth | Two-pass sentiment, aspect-level scoring, anomaly detection |
| Dashboard UX/UI | Fully interactive HTML dashboard, filterable, sortable, drilldown |
| Competitive intelligence quality | Brand comparison, VFM index, scatter plot, Agent Insights |
| Technical execution | Modular Python pipeline, FastAPI backend, clean dataset |
| Product thinking | Decision-maker framing throughout |

**Bonus features implemented:** Aspect-level sentiment · Anomaly detection · VFM index · Review trust signals · Agent Insights with 7 non-obvious conclusions.

---

## License

MIT — free to use, modify, and distribute with attribution.

---

## Author

Built as part of the Moonshot AI Agent Internship Assignment.
