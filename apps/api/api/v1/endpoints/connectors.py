"""
Studio Growth OS - Connector Endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from prisma import Prisma

from core.database import get_db
from core.logging import get_logger
from api.v1.endpoints.auth import get_tenant_context

logger = get_logger(__name__)

router = APIRouter()

# Schemas
class ConnectorConfigBase(BaseModel):
    provider: str
    config_json: dict

class ConnectorConfigResponse(BaseModel):
    id: str
    tenant_id: str
    provider: str
    config_json: dict
    status: str
    authorized_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    error_count: int

class ConnectorSyncRequest(BaseModel):
    force: bool = False

class ConnectorHealthResponse(BaseModel):
    provider: str
    status: str
    last_success_at: Optional[datetime]
    error_rate_5m: float
    error_rate_24h: float
    quota_remaining: int
    details: Optional[dict] = None

# Endpoints
@router.get("", response_model=List[ConnectorConfigResponse])
async def list_connectors(
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """List all connector configurations for tenant"""
    connectors = await db.connectorConfig.find_many(
        where={"tenantId": tenant_ctx["tenant_id"]}
    )
    return [ConnectorConfigResponse.model_validate(c) for c in connectors]

@router.get("/{provider}", response_model=ConnectorConfigResponse)
async def get_connector(
    provider: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get a specific connector configuration"""
    connector = await db.connectorConfig.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "provider": provider}
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return ConnectorConfigResponse.model_validate(connector)

@router.post("/{provider}", response_model=ConnectorConfigResponse, status_code=201)
async def create_connector(
    provider: str,
    config: ConnectorConfigBase,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Create or update a connector configuration"""
    # Validate provider
    valid_providers = ["instagram", "youtube", "whatsapp", "google_business_profile"]
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {valid_providers}")

    connector = await db.connectorConfig.upsert(
        where={"id": f"conn_{provider}"},
        create={
            "id": f"conn_{provider}",
            "tenantId": tenant_ctx["tenant_id"],
            "provider": provider,
            "configJson": config.config_json,
            "status": "not_authorized",
        },
        update={
            "configJson": config.config_json,
            "status": "not_authorized",
        },
    )

    logger.info("Connector configured", provider=provider, tenant=tenant_ctx["tenant_id"])
    return ConnectorConfigResponse.model_validate(connector)

@router.post("/{provider}/sync")
async def sync_connector(
    provider: str,
    request: ConnectorSyncRequest,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Trigger a manual sync for a connector"""
    connector = await db.connectorConfig.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "provider": provider}
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    if connector.status not in ["authorized", "configured"]:
        raise HTTPException(status_code=400, detail="Connector not authorized")

    # In production: trigger background sync job
    # For now, update last_sync_at
    await db.connectorConfig.update(
        where={"id": connector.id},
        data={"lastSyncAt": datetime.utcnow()}
    )

    logger.info("Connector sync triggered", provider=provider, tenant=tenant_ctx["tenant_id"])
    return {"message": f"Sync triggered for {provider}", "status": "queued"}

@router.get("/{provider}/health", response_model=ConnectorHealthResponse)
async def get_connector_health(
    provider: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get health status for a specific connector"""
    health = await db.connectorHealth.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "provider": provider}
    )
    if not health:
        raise HTTPException(status_code=404, detail="Health data not found")
    return ConnectorHealthResponse.model_validate(health)

@router.get("/{provider}/capabilities")
async def get_connector_capabilities(
    provider: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Get supported capabilities for a connector"""
    connector = await db.connectorConfig.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "provider": provider}
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    capabilities = connector.configJson.get("capabilities", {})
    return {
        "provider": provider,
        "authorized": connector.status == "authorized",
        "capabilities": capabilities,
        "supported_operations": [k for k, v in capabilities.items() if v],
    }

@router.delete("/{provider}", status_code=204)
async def delete_connector(
    provider: str,
    tenant_ctx: dict = Depends(get_tenant_context),
    db: Prisma = Depends(get_db),
):
    """Delete a connector configuration"""
    connector = await db.connectorConfig.find_first(
        where={"tenantId": tenant_ctx["tenant_id"], "provider": provider}
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    await db.connectorConfig.delete(where={"id": connector.id})
    logger.info("Connector deleted", provider=provider, tenant=tenant_ctx["tenant_id"])