from pydantic import BaseModel
from typing import Optional, List, Dict

#ssm
class AspectScores(BaseModel):
    wheels: Optional[int] = None
    handle: Optional[int] = None
    material: Optional[int] = None
    zipper: Optional[int] = None
    size: Optional[int] = None
    durability: Optional[int] = None


class BrandSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    avg_price: int
    list_price: int
    discount_pct: float
    rating: float
    review_count: int
    sentiment_score: int
    price_band: str
    top_pros: List[str]
    top_cons: List[str]
    aspects: AspectScores
    synthesis: str
    vfm_index: int
    salary: int
    avg_month_int


class ProductItem(BaseModel):
    id: str
    brand: str
    asin: str
    product_title: str
    sell_price: int
    list_price: int
    discount_pct: float
    rating: float
    review_count: int
    category: str
    sentiment_score: int
    top_pros: List[str]
    top_cons: List[str]
    date: int


class InsightItem(BaseModel):
    type: str
    num: str
    title: str
    body: str
    tag: str
    tag_class: str


class AnomalyItem(BaseModel):
    brand: str
    signal: str
    expected: str
    actual: str
    severity: str
    feedback: str


class PipelineStatus(BaseModel):
    stage: str
    status: str
    message: str
    records_processed: Optional[int] = None
