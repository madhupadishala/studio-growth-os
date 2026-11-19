"""Payments boundary. Provider actions remain unavailable until configured."""
from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def payments_unconfigured(path: str):
    raise HTTPException(status_code=503, detail="Payments provider is not configured")
