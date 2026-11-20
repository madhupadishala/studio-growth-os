"""Settings boundary. No mock configuration is exposed."""
from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def settings_unconfigured(path: str):
    raise HTTPException(status_code=503, detail="Settings service is not configured")
