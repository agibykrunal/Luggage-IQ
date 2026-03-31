import json
import re
import argparse
from pathlib import Path
from collections import Counter, defaultdict

OUTPUT_DIR = Path("data/processed")

POSITIVE_PATTERNS = [
    (r"\bgood (wheel|roller)s?\b", "Smooth wheels"),
    (r"\b(smooth|silent|360|spinner) (wheel|roller)s?\b", "Smooth wheels"),
    (r"\b(sturdy|strong|solid|durable) (build|shell|frame|body)\b", "Durable build"),
    (r"\b(lightweight|light weight|easy to carry)\b", "Lightweight"),
    (r"\b(spacious|good (capacity|space|storage)|roomy)\b", "Good capacity"),
    (r"\b(good|sturdy|strong|reliable) (zip|zipper|lock)\b", "Reliable zipper"),
    (r"\b(comfortable|ergonomic|easy grip) (handle|grip)\b", "Comfortable handle"),
    (r"\b(good|great|excellent|value for money|worth the price)\b", "Good value"),
    (r"\b(nice|beautiful|stylish|trendy) (design|look|color|style)\b", "Attractive design"),
    (r"\b(good|excellent|strong|durable) (material|quality)\b", "Quality material"),
    (r"\btsa (lock|approved)\b", "TSA lock"),
    (r"\b(warranty|after.?sale|customer service) (good|excellent|helpful)\b", "Good warranty support"),
]

NEGATIVE_PATTERNS = [
    (r"\b(bad|poor|scratchy|noisy|broken|stiff|loose|wobbl) (wheel|roller)s?\b", "Wheel issues"),
    (r"\b(zip|zipper) (broke|broken|stuck|poor|bad|weak)\b", "Zipper failure"),
    (r"\b(handle|grip) (broke|broken|loose|poor|bad|came off)\b", "Handle problems"),
    (r"\b(thin|cheap|flimsy|low.?quality) (shell|material|plastic)\b", "Thin material"),
    (r"\b(heavy|too heavy|overweight)\b", "Heavy"),
    (r"\b(poor|bad|no) (customer.?service|support|warranty)\b", "Poor customer service"),
    (r"\b(overpriced|expensive|costly|not worth)\b", "Overpriced"),
    (r"\b(quality.?control|inconsistent|varies|bad batch)\b", "Inconsistent quality"),
    (r"\b(stitching|seam) (poor|bad|came off|loose|weak)\b", "Poor stitching"),
    (r"\b(deliver|packaging) (damage|damaged|poor|bad)\b", "Delivery damage"),
]


def extract_themes_from_text(text):
    text_lower = text.lower()
    pos_themes = []
    neg_themes = []

    for pattern, label in POSITIVE_PATTERNS:
        if re.search(pattern, text_lower):
            pos_themes.append(label)

    for pattern, label in NEGATIVE_PATTERNS:
        if re.search(pattern, text_lower):
            neg_themes.append(label)

    return pos_themes, neg_themes


def extract_brand_themes(reviews):
    brand_pos = defaultdict(Counter)
    brand_neg = defaultdict(Counter)

    for review in reviews:
        brand = review.get("brand", "unknown")
        text = f"{review.get('title', '')} {review.get('body', '')}"
        pos, neg = extract_themes_from_text(text)

        for theme in pos:
            brand_pos[brand][theme] += 1
        for theme in neg:
            brand_neg[brand][theme] += 1

    result = {}
    for brand in set(list(brand_pos.keys()) + list(brand_neg.keys())):
        total = sum(brand_pos[brand].values()) + sum(brand_neg[brand].values()) or 1
        result[brand] = {
            "brand": brand,
            "top_pros": [t for t, _ in brand_pos[brand].most_common(5)],
            "top_cons": [t for t, _ in brand_neg[brand].most_common(5)],
            "pos_theme_counts": dict(brand_pos[brand].most_common(10)),
            "neg_theme_counts": dict(brand_neg[brand].most_common(10)),
        }

    return result


def main(input_file, output_dir):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Extracting themes from {len(reviews)} reviews...")
    themes = extract_brand_themes(reviews)

    out_file = Path(output_dir) / "brand_themes.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(themes, f, indent=2, ensure_ascii=False)

    print(f"Themes saved to {out_file}")
    for brand, data in themes.items():
        print(f"\n{brand}")
        print(f"  Pros: {', '.join(data['top_pros'][:3])}")
        print(f"  Cons: {', '.join(data['top_cons'][:3])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/reviews.json")
    parser.add_argument("--output", default="data/processed")
    args = parser.parse_args()
    main(args.input, args.output)
