from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.services.data_service import get_products

router = APIRouter()


@router.get("/")
def list_products(
    brand: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    min_sentiment: Optional[int] = Query(None),
    max_sentiment: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("sentiment_score"),
):
    raw = get_products()
    if not raw:
        raise HTTPException(status_code=404, detail="No product data found. Run the scraper first.")

    all_products = []
    for brand_id, brand_products in raw.items():
        for p in brand_products:
            all_products.append({**p, "brand_id": brand_id})

    if brand:
        all_products = [p for p in all_products if p.get("brand", "").lower() == brand.lower() or p.get("brand_id") == brand]
    if category:
        all_products = [p for p in all_products if p.get("category", "").lower() == category.lower()]
    if min_rating:
        all_products = [p for p in all_products if p.get("rating", 0) >= min_rating]
    if min_sentiment:
        all_products = [p for p in all_products if p.get("sentiment_score", 0) >= min_sentiment]
    if max_sentiment:
        all_products = [p for p in all_products if p.get("sentiment_score", 100) <= max_sentiment]

    valid_sorts = ["sentiment_score", "rating", "sell_price", "discount_pct", "review_count"]
    key = sort_by if sort_by in valid_sorts else "sentiment_score"
    all_products.sort(key=lambda x: x.get(key, 0), reverse=True)

    return all_products


@router.get("/{product_id}")
def get_product(product_id: str):
    raw = get_products()
    if not raw:
        raise HTTPException(status_code=404, detail="No product data found.")

    for brand_products in raw.values():
        for p in brand_products:
            if p.get("asin") == product_id or p.get("id") == product_id:
                return p

    raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")
