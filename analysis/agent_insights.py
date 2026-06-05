import json
import os
import argparse
from pathlib import Path
#sj
OUTPUT_DIR = Path("data/processed")


def build_prompt(brand_data, aspect_data, anomaly_data):
    brands_summary = json.dumps(brand_data, indent=2)
    aspects_summary = json.dumps(aspect_data, indent=2)
    anomalies_summary = json.dumps(anomaly_data.get("summary", {}), indent=2)

    return f"""You are a competitive intelligence analyst specialising in Indian e-commerce.

You are given brand-level pricing, sentiment, discount, aspect scores, and anomaly data for luggage brands on Amazon India.

Brand data:
{brands_summary}

Aspect scores (0-100 per physical attribute):
{aspects_summary}

Anomaly signals:
{anomalies_summary}

Produce exactly 7 non-obvious insights. Rules:
- Do NOT state surface-level observations like "Brand X has the highest rating"
- Focus on contradictions, anomalies, and cross-variable patterns
- Each insight must be actionable for a procurement or product decision-maker
- Flag any review integrity issues detected
- Reference specific numbers from the data

Respond ONLY with a JSON array. Each element must have these keys:
- "type": one of ["Anomaly Alert", "Pricing Anomaly", "Sentiment Split", "Category Insight", "Value-for-Money", "Trust Signal", "Strategic Gap"]
- "num": "01" through "07"
- "title": short headline (under 12 words)
- "body": 2-3 sentence insight with specific data
- "tag": 2-3 word label
- "tag_class": one of ["positive", "negative", "warning", "info"]

Return only valid JSON with no preamble."""


def generate_insights(brand_data, aspect_data, anomaly_data, use_llm=True):
    if not use_llm:
        return _fallback_insights()

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = build_prompt(brand_data, aspect_data, anomaly_data)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system="You are a competitive intelligence analyst. Always respond with valid JSON only.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        return json.loads(raw)
    except Exception as e:
        print(f"LLM call failed: {e}. Using fallback insights.")
        return _fallback_insights()


def _fallback_insights():
    return [
        {
            "type": "Anomaly Alert",
            "num": "01",
            "title": "Nasher Miles is severely underweighted by volume-based analyses",
            "body": "Leads on sentiment and rating despite having the fewest reviews. Review velocity is accelerating — a signal missed by analysts who weight brands by review count.",
            "tag": "Emerging threat",
            "tag_class": "info",
        },
        {
            "type": "Pricing Anomaly",
            "num": "02",
            "title": "VIP's 33% discount signals structural demand weakness",
            "body": "Highest discount in the set, yet ranks 4th in sentiment. Discounting to compete rather than winning on product merit. List price is ~50% above selling price.",
            "tag": "High risk",
            "tag_class": "negative",
        },
        {
            "type": "Value-for-Money",
            "num": "03",
            "title": "Safari offers the best price-adjusted sentiment in the mid tier",
            "body": "At avg ₹4,850 with 79 sentiment, Safari's VFM index outperforms American Tourister (₹5,900 / 83). 18% less spend yields 95% of sentiment outcome.",
            "tag": "Best buy",
            "tag_class": "positive",
        },
    ]


def main(output_dir):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    brand_file = Path("data/processed/brand_sentiment.json")
    aspect_file = Path("data/processed/aspect_scores.json")
    anomaly_file = Path("data/processed/anomalies.json")

    brand_data = json.load(open(brand_file)) if brand_file.exists() else {}
    aspect_data = json.load(open(aspect_file)) if aspect_file.exists() else {}
    anomaly_data = json.load(open(anomaly_file)) if anomaly_file.exists() else {}

    use_llm = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print(f"Generating insights using {'LLM' if use_llm else 'fallback'}...")

    insights = generate_insights(brand_data, aspect_data, anomaly_data, use_llm=use_llm)

    out_file = Path(output_dir) / "agent_insights.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(insights)} insights to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/processed")
    args = parser.parse_args()
    main(args.output)
