"""
Studio Growth OS - Analytics Endpoints
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from prisma import Prisma

from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Schemas
class DashboardMetrics(BaseModel):
    today: Dict[str, Any]
    tomorrow: Dict[str, Any]
    this_week: Dict[str, Any]
    this_month: Dict[str, Any]
    past_months: Dict[str, Any]

class FunnelData(BaseModel):
    channel: str
    impressions: int
    clicks: int
    leads: int
    qualified: int
    quotes: int
    bookings: int
    revenue: int

class AttributionModel(BaseModel):
    model: str
    data: List[Dict[str, Any]]

class BenchmarkData(BaseModel):
    metric: str
    p25: float
    p50: float
    p75: float
    p90: float
    sample_count: int
    your_value: Optional[float] = None

# Endpoints
@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    range: str = Query("today", pattern="^(today|tomorrow|7d|30d|90d|custom)$"),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get dashboard metrics for specified time range"""
    # In production: query materialized views / compute from events
    # For now, return mock data matching the demo scenario

    now = datetime.utcnow()

    return DashboardMetrics(
        today={
            "shoots_scheduled": 2,
            "prep_tasks": 3,
            "unresponded_leads": 1,
            "pending_approvals": 0,
            "leads_new": 3,
            "leads_qualified": 2,
            "quotes_sent": 2,
            "bookings_confirmed": 2,
            "revenue_collected": 12500000,
            "pipeline_value": 4500000,
            "conversations_unread": 2,
            "overdue_followups": 1,
            "bot_escalations": 0,
            "avg_response_minutes": 12,
        },
        tomorrow={
            "upcoming_shoots": 1,
            "required_prep": 2,
            "client_confirmations_needed": 1,
        },
        this_week={
            "calendar_heatmap": {
                "Mon": 1, "Tue": 0, "Wed": 1, "Thu": 0, "Fri": 1, "Sat": 1, "Sun": 0
            },
            "pipeline_value": 4500000,
            "utilization_pct": 65,
            "leads_by_source": {
                "instagram": 12, "website": 8, "whatsapp": 5, "referral": 3
            },
        },
        this_month={
            "leads_new": 47,
            "leads_qualified": 31,
            "quotes_sent": 18,
            "bookings_confirmed": 12,
            "revenue_collected": 8900000,
            "conversion_rate": 25.5,
            "cac": 1850,
            "ltv": 156000,
        },
        past_months={
            "trend": "up",
            "leads_mom_pct": 12.3,
            "revenue_mom_pct": 8.7,
            "conversion_mom_pct": -2.1,
            "monthly_data": [
                {"month": "2026-08", "leads": 38, "revenue": 7200000, "conversion": 28.0},
                {"month": "2026-09", "leads": 42, "revenue": 8100000, "conversion": 26.5},
                {"month": "2026-10", "leads": 47, "revenue": 8900000, "conversion": 25.5},
            ],
        },
    )

@router.get("/funnel")
async def get_funnel_analytics(
    range: str = Query("30d", pattern="^(7d|30d|90d)$"),
    model: str = Query("time_decay", pattern="^(first_touch|last_touch|linear|time_decay|u_shaped)$"),
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get funnel analytics with multi-touch attribution"""
    # In production: query attribution_events materialized view
    return {
        "range": range,
        "model": model,
        "funnel": [
            {"stage": "impression", "count": 125000, "conversion_rate": 100.0},
            {"stage": "click", "count": 12500, "conversion_rate": 10.0},
            {"stage": "lead", "count": 1250, "conversion_rate": 10.0},
            {"stage": "qualified", "count": 625, "conversion_rate": 50.0},
            {"stage": "quote", "count": 312, "conversion_rate": 50.0},
            {"stage": "booking", "count": 156, "conversion_rate": 50.0},
            {"stage": "payment", "count": 140, "conversion_rate": 89.7},
        ],
        "attribution": {
            "first_touch": {"instagram": 0.45, "website": 0.30, "whatsapp": 0.15, "referral": 0.10},
            "last_touch": {"instagram": 0.40, "website": 0.35, "whatsapp": 0.20, "referral": 0.05},
            "linear": {"instagram": 0.35, "website": 0.30, "whatsapp": 0.20, "referral": 0.15},
            "time_decay": {"instagram": 0.38, "website": 0.32, "whatsapp": 0.18, "referral": 0.12},
            "u_shaped": {"instagram": 0.42, "website": 0.28, "whatsapp": 0.18, "referral": 0.12},
        },
        "cohorts": [
            {"period": "2026-10", "leads": 47, "bookings": 12, "conversion": 25.5, "revenue": 8900000},
            {"period": "2026-09", "leads": 42, "bookings": 11, "conversion": 26.2, "revenue": 8100000},
            {"period": "2026-08", "leads": 38, "bookings": 10, "conversion": 26.3, "revenue": 7200000},
        ],
    }

@router.get("/benchmark")
async def get_benchmark_data(
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get anonymized benchmark data (opt-in required)"""
    # Check if tenant has opted in
    settings = await db.businessSettings.find_unique(where={"tenantId": tenant_ctx["tenant_id"]})
    if not settings or not settings.settingsJson.get("benchmarking_opt_in", False):
        raise HTTPException(status_code=403, detail="Benchmarking requires opt-in")

    # In production: query benchmark_aggregates table
    return {
        "conversion_rate": {"p25": 18.5, "p50": 24.0, "p75": 31.2, "p90": 38.7, "sample_count": 45},
        "cac": {"p25": 1200, "p50": 1850, "p75": 2800, "p90": 4200, "sample_count": 42},
        "ltv": {"p25": 95000, "p50": 156000, "p75": 245000, "p90": 380000, "sample_count": 40},
        "response_time_minutes": {"p25": 8, "p50": 15, "p75": 35, "p90": 72, "sample_count": 45},
        "booking_value": {"p25": 25000, "p50": 45000, "p75": 85000, "p90": 150000, "sample_count": 45},
    }

@router.get("/connector-health")
async def get_connector_health(
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get health status of all connectors"""
    health = await db.connectorHealth.find_many(
        where={"tenantId": tenant_ctx["tenant_id"]}
    )
    return {
        "connectors": [
            {
                "provider": h.provider,
                "status": h.status,
                "last_success_at": h.lastSuccessAt,
                "error_rate_5m": h.errorRate5m,
                "error_rate_24h": h.errorRate24h,
                "quota_remaining": h.quotaRemaining,
            }
            for h in health
        ]
    }