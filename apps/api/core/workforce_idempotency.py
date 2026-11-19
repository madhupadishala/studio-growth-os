"""Durable idempotency using the application's single generated Prisma client."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from fastapi import HTTPException

from core.database import db


def _hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def claim(
    external_tenant_id: str,
    endpoint: str,
    key: str,
    payload: dict,
    correlation_id: str,
) -> dict:
    if not key or len(key) > 255:
        raise HTTPException(status_code=400, detail="A valid Idempotency-Key header is required")

    digest = _hash(payload)
    try:
        row = await db.workforceadapteridempotency.create(
            data={
                "externalTenantId": external_tenant_id,
                "endpoint": endpoint,
                "idempotencyKey": key,
                "requestHash": digest,
                "status": "PROCESSING",
                "correlationId": correlation_id,
            }
        )
        return {"created": True, "request_hash": digest, "record_id": row.id}
    except Exception as create_error:
        # The composite unique key serializes concurrent claims in PostgreSQL.
        row = await db.workforceadapteridempotency.find_first(
            where={
                "externalTenantId": external_tenant_id,
                "endpoint": endpoint,
                "idempotencyKey": key,
            }
        )
        if row is None:
            raise create_error

    if row.requestHash != digest:
        raise HTTPException(
            status_code=409,
            detail="Idempotency-Key was already used with a different request payload",
        )
    if row.status == "COMPLETED":
        return {
            "created": False,
            "status_code": row.responseStatusCode or 200,
            "body": row.responseBodyJson or {},
        }
    raise HTTPException(
        status_code=409,
        detail="A request with this Idempotency-Key is already processing",
    )


async def complete(
    external_tenant_id: str,
    endpoint: str,
    key: str,
    status_code: int,
    body: dict,
) -> None:
    result = await db.workforceadapteridempotency.update_many(
        where={
            "externalTenantId": external_tenant_id,
            "endpoint": endpoint,
            "idempotencyKey": key,
            "status": "PROCESSING",
        },
        data={
            "status": "COMPLETED",
            "responseStatusCode": status_code,
            "responseBodyJson": body,
            "completedAt": datetime.now(timezone.utc),
        },
    )
    if result.count < 1:
        raise RuntimeError("Idempotency claim disappeared before completion")
