"""Media boundary. Storage actions remain unavailable until configured."""
from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def media_unconfigured(path: str):
    raise HTTPException(status_code=503, detail="Media storage provider is not configured")
