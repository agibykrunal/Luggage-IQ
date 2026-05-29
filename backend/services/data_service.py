import json
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Optional

DATA_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_brand_sentiment() -> Optional[Dict]:
    return _load_json(DATA_DIR / "brand_sentiment.json")



@lru_cache(maxsize=1)
def get_aspect_scores() -> Optional[Dict]:
    return _load_json(DATA_DIR / "aspect_scores.json")


@lru_cache(maxsize=1)
def get_brand_themes() -> Optional[Dict]:
    return _load_json(DATA_DIR / "brand_themes.json")


@lru_cache(maxsize=1)
def get_agent_insights() -> Optional[List]:
    return _load_json(DATA_DIR / "agent_insights.json")


@lru_cache(maxsize=1)
def get_anomalies() -> Optional[Dict]:
    return _load_json(DATA_DIR / "anomalies.json")


@lru_cache(maxsize=1)
def get_products() -> Optional[Dict]:
    return _load_json(RAW_DIR / "products.json")


def invalidate_cache():
    get_brand_sentiment.cache_clear()
    get_aspect_scores.cache_clear()
    get_brand_themes.cache_clear()
    get_agent_insights.cache_clear()
    get_anomalies.cache_clear()
    get_products.cache_clear()
    get_salary.cache_clear()


def compute_vfm_index(sentiment: int, avg_price: int) -> int:
    price_tier = 1 if avg_price < 3000 else 2 if avg_price < 6000 else 3
    return round(sentiment / price_tier)
