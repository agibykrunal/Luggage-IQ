from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.services.data_service import invalidate_cache
import subprocess
import sys
#aaaa
router = APIRouter()

pipeline_status = {
    "stage": "idle",
    "status": "idle",
    "message": "No pipeline run yet.",
    "records_processed": None,
}


def run_stage(cmd: list, stage_name: str):
    global pipeline_status
    pipeline_status = {"stage": stage_name, "status": "running", "message": f"Running {stage_name}...", "records_processed": None}
    try:
        result = subprocess.run(
            [sys.executable] + cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            pipeline_status = {
                "stage": stage_name,
                "status": "complete",
                "message": result.stdout.strip()[-300:] if result.stdout else "Done.",
                "records_processed": None,
            }
        else:
            pipeline_status = {
                "stage": stage_name,
                "status": "error",
                "message": result.stderr.strip()[-300:] if result.stderr else "Unknown error.",
                "records_processed": None,
            }
    except subprocess.TimeoutExpired:
        pipeline_status = {"stage": stage_name, "status": "error", "message": "Timed out after 10 minutes.", "records_processed": None}
    except Exception as e:
        pipeline_status = {"stage": stage_name, "status": "error", "message": str(e), "records_processed": None}
    finally:
        invalidate_cache()


def run_full_pipeline():
    stages = [
        (["scraper/amazon_scraper.py"], "scrape_products"),
        (["scraper/review_scraper.py", "--input", "data/raw/products.json"], "scrape_reviews"),
        (["analysis/sentiment.py", "--input", "data/raw/reviews.json", "--output", "data/processed"], "sentiment"),
        (["analysis/theme_extractor.py", "--input", "data/raw/reviews.json", "--output", "data/processed"], "themes"),
        (["analysis/aspect_sentiment.py", "--input", "data/raw/reviews.json", "--output", "data/processed"], "aspects"),
        (["analysis/anomaly_detector.py", "--input", "data/processed/reviews_scored.json", "--output", "data/processed"], "anomalies"),
        (["analysis/agent_insights.py", "--output", "data/processed"], "insights"),
    ]
    for cmd, name in stages:
        run_stage(cmd, name)
        if pipeline_status["status"] == "error":
            break


@router.post("/run")
def trigger_pipeline(background_tasks: BackgroundTasks):
    if pipeline_status.get("status") == "running":
        raise HTTPException(status_code=409, detail="Pipeline already running.")
    background_tasks.add_task(run_full_pipeline)
    return {"message": "Pipeline started in background.", "status": "running"}


@router.post("/run/{stage}")
def trigger_stage(stage: str, background_tasks: BackgroundTasks):
    stage_map = {
        "sentiment": ["analysis/sentiment.py", "--input", "data/raw/reviews.json", "--output", "data/processed"],
        "themes": ["analysis/theme_extractor.py", "--input", "data/raw/reviews.json", "--output", "data/processed"],
        "aspects": ["analysis/aspect_sentiment.py", "--input", "data/raw/reviews.json", "--output", "data/processed"],
        "anomalies": ["analysis/anomaly_detector.py", "--input", "data/processed/reviews_scored.json", "--output", "data/processed"],
        "insights": ["analysis/agent_insights.py", "--output", "data/processed"],
    }
    if stage not in stage_map:
        raise HTTPException(status_code=400, detail=f"Unknown stage '{stage}'. Valid: {list(stage_map.keys())}")
    background_tasks.add_task(run_stage, stage_map[stage], stage)
    return {"message": f"Stage '{stage}' started.", "status": "running"}


@router.get("/status")
def get_status():
    return pipeline_status
