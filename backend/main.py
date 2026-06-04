from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.routers import brands, products, insights, pipeline
#sjs
app = FastAPI(
    title="LuggageIQ API",
    description="Competitive intelligence backend for Amazon India luggage brands",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])

dashboard_path = Path("dashboard")
if dashboard_path.exists():
    app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "luggageiq"}
