"""
Studio Growth OS - API v1 Router
"""
from fastapi import APIRouter

from api.v1.endpoints import (
    auth,
    leads,
    quotes,
    bookings,
    conversations,
    analytics,
    webhooks,
    connectors,
    agent,
    payments,
    media,
    settings as settings_ep,
)

api_router = APIRouter()

# Public endpoints (no auth required)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Protected endpoints (require auth)
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(connectors.router, prefix="/connectors", tags=["Connectors"])
api_router.include_router(agent.router, prefix="/agent", tags=["AI Agent"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(settings_ep.router, prefix="/settings", tags=["Settings"])