from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.services.data_service import (
    get_brand_sentiment, get_aspect_scores, get_brand_themes, compute_vfm_index
)

router = APIRouter()

@router.get("/")
def list_brands(
    min_rating: Optional[float] = Query(None),
    price_band: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("sentiment"),
):
    sentiment_data = get_brand_sentiment()
    aspect_data = get_aspect_scores() or {}
    theme_data = get_brand_themes() or {}

    if not sentiment_data:
        raise HTTPException(status_code=404, detail="No brand data found. Run the pipeline first.")

    brands = []
    for brand_id, data in sentiment_data.items():
        avg_price = data.get("avg_price", 0)
        sentiment = data.get("avg_sentiment", 0)
        rating = data.get("avg_rating", 0)

        if min_rating and rating < min_rating:
            continue

        band = "value" if avg_price < 3000 else "mid" if avg_price <= 6000 else "premium"
        if price_band and price_band != band:
            continue

        aspects = aspect_data.get(brand_id, {})
        themes = theme_data.get(brand_id, {})

        brands.append({
            "id": brand_id,
            "name": data.get("brand", brand_id),
            "avg_price": avg_price,
            "list_price": data.get("avg_list_price", avg_price),
            "discount_pct": data.get("avg_discount", 0),
            "rating": rating,
            "review_count": data.get("review_count", 0),
            "sentiment_score": sentiment,
            "price_band": band,
            "top_pros": themes.get("top_pros", []),
            "top_cons": themes.get("top_cons", []),
            "aspects": {k: aspects.get(k) for k in ["wheels", "handle", "material", "zipper", "size", "durability"]},
            "synthesis": data.get("synthesis", ""),
            "vfm_index": compute_vfm_index(sentiment, avg_price),
        })

    sort_key = sort_by if sort_by in ["sentiment_score", "avg_price", "discount_pct", "rating", "review_count", "vfm_index"] else "sentiment_score"
    brands.sort(key=lambda x: x.get(sort_key, 0), reverse=True)

    return brands


@router.get("/{brand_id}")
def get_brand(brand_id: str):
    sentiment_data = get_brand_sentiment()
    if not sentiment_data or brand_id not in sentiment_data:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found.")
    return sentiment_data[brand_id]
