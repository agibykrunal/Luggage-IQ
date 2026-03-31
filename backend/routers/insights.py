from fastapi import APIRouter, HTTPException
from backend.services.data_service import get_agent_insights, get_anomalies

router = APIRouter()


@router.get("/")
def list_insights():
    insights = get_agent_insights()
    if not insights:
        raise HTTPException(status_code=404, detail="No insights found. Run analysis/agent_insights.py first.")
    return insights


@router.get("/anomalies")
def list_anomalies():
    anomalies = get_anomalies()
    if not anomalies:
        raise HTTPException(status_code=404, detail="No anomaly data found. Run analysis/anomaly_detector.py first.")
    return anomalies


@router.get("/anomalies/summary")
def anomaly_summary():
    anomalies = get_anomalies()
    if not anomalies:
        raise HTTPException(status_code=404, detail="No anomaly data found.")
    return anomalies.get("summary", {})
