import json
import re
import argparse
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path("data/processed")

ASPECT_KEYWORDS = {
    "wheels": [
        "wheel", "roller", "spinner", "360", "rotate", "roll",
        "smooth rolling", "wheel quality", "castors",
    ],
    "handle": [
        "handle", "grip", "telescopic", "retractable", "pull rod",
        "carry handle", "top handle", "ergonomic",
    ],
    "material": [
        "material", "shell", "plastic", "polycarbonate", "abs", "fabric",
        "hard shell", "soft shell", "outer", "surface", "finish",
    ],
    "zipper": [
        "zipper", "zip", "closure", "lock", "tsa", "buckle",
        "zipping", "zip quality",
    ],
    "size": [
        "size", "capacity", "space", "spacious", "roomy", "fit",
        "compartment", "storage", "packing", "cabin", "check.in",
    ],
    "durability": [
        "durable", "durability", "last", "quality", "sturdy", "strong",
        "build quality", "solid", "well.made", "broke", "break", "damage",
    ],
}

NEGATIVE_INDICATORS = [
    "bad", "poor", "worst", "broke", "broken", "issues", "problem",
    "doesn't", "not", "no", "never", "fail", "failed", "cheap",
    "flimsy", "weak", "stiff", "stuck", "scratch", "damaged",
]

POSITIVE_INDICATORS = [
    "good", "great", "excellent", "amazing", "perfect", "best",
    "smooth", "strong", "solid", "durable", "easy", "lightweight",
    "quality", "well", "nice", "love", "happy",
]


def extract_aspect_sentiment(text):
    text_lower = text.lower()
    scores = {}

    for aspect, keywords in ASPECT_KEYWORDS.items():
        mentions = []
        for kw in keywords:
            pattern = rf"\b{kw}\b"
            for match in re.finditer(pattern, text_lower):
                start = max(0, match.start() - 60)
                end = min(len(text_lower), match.end() + 60)
                context = text_lower[start:end]
                mentions.append(context)

        if not mentions:
            scores[aspect] = None
            continue

        pos_count = 0
        neg_count = 0
        for context in mentions:
            for ind in POSITIVE_INDICATORS:
                if ind in context:
                    pos_count += 1
            for ind in NEGATIVE_INDICATORS:
                if ind in context:
                    neg_count += 1

        total = pos_count + neg_count
        if total == 0:
            scores[aspect] = 60
        else:
            scores[aspect] = int(pos_count / total * 100)

    return scores


def aggregate_aspect_scores(reviews):
    brand_aspects = defaultdict(lambda: defaultdict(list))

    for review in reviews:
        brand = review.get("brand", "unknown")
        text = f"{review.get('title', '')} {review.get('body', '')}"
        scores = extract_aspect_sentiment(text)

        for aspect, score in scores.items():
            if score is not None:
                brand_aspects[brand][aspect].append(score)

    result = {}
    for brand, aspects in brand_aspects.items():
        result[brand] = {"brand": brand}
        for aspect, scores in aspects.items():
            if scores:
                result[brand][aspect] = round(sum(scores) / len(scores))
            else:
                result[brand][aspect] = 50

    return result


def main(input_file, output_dir):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Extracting aspect sentiment from {len(reviews)} reviews...")
    aspect_scores = aggregate_aspect_scores(reviews)

    out_file = Path(output_dir) / "aspect_scores.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(aspect_scores, f, indent=2, ensure_ascii=False)

    print(f"Aspect scores saved to {out_file}")
    for brand, data in aspect_scores.items():
        print(f"\n{brand}:")
        for aspect in ["wheels", "handle", "material", "zipper", "size", "durability"]:
            print(f"  {aspect}: {data.get(aspect, 'N/A')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/reviews.json")
    parser.add_argument("--output", default="data/processed")
    args = parser.parse_args()
    main(args.input, args.output)
