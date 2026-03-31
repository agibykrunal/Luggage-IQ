import json
import os
import argparse
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")


def vader_score(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    normalized = int((compound + 1) / 2 * 100)
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return normalized, label


def llm_score(text, client, model="claude-sonnet-4-20250514"):
    prompt = (
        "Rate the sentiment of this product review on a scale of 0 to 100 "
        "(0=very negative, 50=neutral, 100=very positive). "
        "Reply with only a JSON object: {\"score\": <int>, \"label\": \"positive\"|\"neutral\"|\"negative\"}.\n\n"
        f"Review: {text[:800]}"
    )
    try:
        message = client.messages.create(
            model=model,
            max_tokens=64,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        return int(data["score"]), data["label"]
    except Exception:
        return vader_score(text)


def score_reviews(reviews, use_llm=False):
    client = None
    if use_llm:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        except Exception:
            use_llm = False

    scored = []
    for review in reviews:
        text = f"{review.get('title', '')} {review.get('body', '')}"
        if use_llm and client:
            score, label = llm_score(text, client)
        else:
            score, label = vader_score(text)

        review["sentiment_score"] = score
        review["sentiment_label"] = label
        scored.append(review)

    return scored


def aggregate_by_brand(scored_reviews):
    from collections import defaultdict

    brand_data = defaultdict(list)
    for r in scored_reviews:
        brand_data[r["brand"]].append(r)

    aggregated = {}
    for brand, reviews in brand_data.items():
        scores = [r["sentiment_score"] for r in reviews]
        aggregated[brand] = {
            "brand": brand,
            "review_count": len(reviews),
            "avg_sentiment": round(sum(scores) / len(scores)),
            "positive_pct": round(sum(1 for r in reviews if r["sentiment_label"] == "positive") / len(reviews) * 100, 1),
            "negative_pct": round(sum(1 for r in reviews if r["sentiment_label"] == "negative") / len(reviews) * 100, 1),
        }

    return aggregated


def main(input_file, output_dir, use_llm):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Scoring {len(reviews)} reviews...")
    scored = score_reviews(reviews, use_llm=use_llm)

    out_reviews = Path(output_dir) / "reviews_scored.json"
    with open(out_reviews, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)

    aggregated = aggregate_by_brand(scored)
    out_agg = Path(output_dir) / "brand_sentiment.json"
    with open(out_agg, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2, ensure_ascii=False)

    print(f"Saved scored reviews to {out_reviews}")
    print(f"Saved brand aggregation to {out_agg}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/reviews.json")
    parser.add_argument("--output", default="data/processed")
    parser.add_argument("--llm", action="store_true")
    args = parser.parse_args()
    main(args.input, args.output, args.llm)
