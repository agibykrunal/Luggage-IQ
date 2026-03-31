import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
import re

OUTPUT_DIR = Path("data/processed")

DUPLICATE_THRESHOLD = 0.85
MIN_REVIEWS_FOR_ANALYSIS = 10


def jaccard_similarity(text_a, text_b):
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def detect_duplicate_reviews(reviews, threshold=DUPLICATE_THRESHOLD):
    flagged = []
    texts = [r.get("body", "") for r in reviews]

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = jaccard_similarity(texts[i], texts[j])
            if sim >= threshold:
                flagged.append({
                    "review_a": reviews[i].get("review_id"),
                    "review_b": reviews[j].get("review_id"),
                    "similarity": round(sim, 3),
                    "brand": reviews[i].get("brand"),
                })

    return flagged


def detect_rating_sentiment_divergence(reviews):
    divergent = []
    for r in reviews:
        rating = r.get("rating", 0)
        sentiment = r.get("sentiment_score", 50)

        normalized_rating = rating / 5 * 100

        if abs(normalized_rating - sentiment) > 35:
            divergent.append({
                "review_id": r.get("review_id"),
                "brand": r.get("brand"),
                "rating": rating,
                "sentiment_score": sentiment,
                "delta": round(abs(normalized_rating - sentiment), 1),
                "direction": "positive_rating_negative_text" if normalized_rating > sentiment else "negative_rating_positive_text",
            })

    return divergent


def detect_review_clustering(reviews, window_hours=48):
    from datetime import datetime

    brand_dates = defaultdict(list)
    for r in reviews:
        date_raw = r.get("date_raw", "")
        brand = r.get("brand", "unknown")
        try:
            date_str = re.search(r"\d{1,2}\s+\w+\s+\d{4}", date_raw)
            if date_str:
                parsed = datetime.strptime(date_str.group(), "%d %B %Y")
                brand_dates[brand].append(parsed)
        except Exception:
            continue

    clusters = {}
    for brand, dates in brand_dates.items():
        if len(dates) < MIN_REVIEWS_FOR_ANALYSIS:
            continue

        dates.sort()
        date_counts = Counter(d.date() for d in dates)
        max_single_day = max(date_counts.values())
        total = len(dates)

        clusters[brand] = {
            "brand": brand,
            "total_reviews": total,
            "max_reviews_single_day": max_single_day,
            "clustering_ratio": round(max_single_day / total, 3),
            "suspicious": max_single_day / total > 0.15,
        }

    return clusters


def run_anomaly_detection(reviews_file, output_dir):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(reviews_file, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Running anomaly detection on {len(reviews)} reviews...")

    duplicates = detect_duplicate_reviews(reviews)
    divergent = detect_rating_sentiment_divergence(reviews)
    clusters = detect_review_clustering(reviews)

    results = {
        "duplicate_reviews": duplicates,
        "rating_sentiment_divergence": divergent,
        "review_clustering": clusters,
        "summary": {
            "total_duplicates_found": len(duplicates),
            "rating_divergence_count": len(divergent),
            "suspicious_brands": [b for b, d in clusters.items() if d.get("suspicious")],
        },
    }

    out_file = Path(output_dir) / "anomalies.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Anomalies saved to {out_file}")
    print(f"  Duplicate pairs: {len(duplicates)}")
    print(f"  Rating/sentiment divergence: {len(divergent)}")
    print(f"  Suspicious clustering brands: {results['summary']['suspicious_brands']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/reviews_scored.json")
    parser.add_argument("--output", default="data/processed")
    args = parser.parse_args()
    run_anomaly_detection(args.input, args.output)
