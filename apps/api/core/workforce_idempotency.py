"""PostgreSQL-backed idempotency claims shared by all workforce write routes."""
from __future__ import annotations
import hashlib, json, os
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from fastapi import HTTPException
from core.config import settings
from models.workforce_adapter_idempotency import WorkforceAdapterIdempotency

def _database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    return url

_engine = create_async_engine(_database_url(), pool_pre_ping=True)
_sessions = async_sessionmaker(_engine, expire_on_commit=False)

def _hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()

async def claim(external_tenant_id: str, endpoint: str, key: str, payload: dict, correlation_id: str):
    if not key or len(key) > 255:
        raise HTTPException(status_code=400, detail="A valid Idempotency-Key header is required")
    digest = _hash(payload)
    async with _sessions() as session, session.begin():
        stmt = insert(WorkforceAdapterIdempotency).values(
            external_tenant_id=external_tenant_id, endpoint=endpoint, idempotency_key=key,
            request_hash=digest, status="PROCESSING", correlation_id=correlation_id
        ).on_conflict_do_nothing(
            index_elements=["external_tenant_id", "endpoint", "idempotency_key"]
        ).returning(WorkforceAdapterIdempotency.id)
        created_id = (await session.execute(stmt)).scalar_one_or_none()
        if created_id:
            return {"created": True, "request_hash": digest}
        row = (await session.execute(select(WorkforceAdapterIdempotency).where(
            WorkforceAdapterIdempotency.external_tenant_id == external_tenant_id,
            WorkforceAdapterIdempotency.endpoint == endpoint,
            WorkforceAdapterIdempotency.idempotency_key == key
        ).with_for_update())).scalar_one()
        if row.request_hash != digest:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request payload")
        if row.status == "COMPLETED":
            return {"created": False, "status_code": row.response_status_code or 200,
                    "body": row.response_body_json}
        raise HTTPException(status_code=409, detail="A request with this Idempotency-Key is already processing")

async def complete(external_tenant_id: str, endpoint: str, key: str, status_code: int, body: dict):
    async with _sessions() as session, session.begin():
        await session.execute(update(WorkforceAdapterIdempotency).where(
            WorkforceAdapterIdempotency.external_tenant_id == external_tenant_id,
            WorkforceAdapterIdempotency.endpoint == endpoint,
            WorkforceAdapterIdempotency.idempotency_key == key,
            WorkforceAdapterIdempotency.status == "PROCESSING"
        ).values(status="COMPLETED", response_status_code=status_code,
                 response_body_json=body, completed_at=func.now()))
