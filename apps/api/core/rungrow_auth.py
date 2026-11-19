"""HMAC-authenticated RunGrow Workforce service boundary."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import urlsplit

from fastapi import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

EXPECTED_PRODUCT_ID = "photo-studio-growth-os"
MAX_SIGNED_BODY_BYTES = 2 * 1024 * 1024


def verify_rungrow_request(headers: dict[str, str], body: bytes, secret: str,
                            tenant_map: dict[str, str], now: float | None = None) -> dict[str, str]:
    signature = headers.get("x-rungrow-signature", "")
    timestamp = headers.get("x-rungrow-timestamp", "")
    product_id = headers.get("x-rungrow-product-id", "")
    external_tenant_id = headers.get("x-rungrow-external-tenant-id", "")
    workforce_tenant_id = headers.get("x-rungrow-org-id", "")
    correlation_id = headers.get("x-correlation-id", "")

    if not secret or len(secret.encode("utf-8")) < 32:
        raise HTTPException(status_code=503, detail="RunGrow service HMAC secret is not configured securely")
    if not all((signature, timestamp, product_id, external_tenant_id, workforce_tenant_id)):
        raise HTTPException(status_code=401, detail="Incomplete RunGrow service authentication headers")
    if product_id != EXPECTED_PRODUCT_ID:
        raise HTTPException(status_code=403, detail="RunGrow product binding mismatch")
    if external_tenant_id == workforce_tenant_id:
        raise HTTPException(status_code=403, detail="External and Workforce tenant IDs must be distinct")
    if tenant_map.get(external_tenant_id) != workforce_tenant_id:
        raise HTTPException(status_code=403, detail="External tenant is not mapped to this Workforce organization")
    try:
        issued = int(timestamp)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid RunGrow request timestamp") from exc
    if abs((time.time() if now is None else now) - issued) > 300:
        raise HTTPException(status_code=401, detail="RunGrow request timestamp outside 300-second replay window")

    binding = ".".join((timestamp, external_tenant_id, workforce_tenant_id, product_id)).encode("utf-8")
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), binding + b"." + body, hashlib.sha256).hexdigest()
    supplied = signature if signature.startswith("sha256=") else "sha256=" + signature
    if not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Invalid RunGrow service signature")
    return {
        "external_tenant_id": external_tenant_id,
        "workforce_tenant_id": workforce_tenant_id,
        "product_id": product_id,
        "correlation_id": correlation_id or "rungrow-service",
    }


class RunGrowHMACAuthMiddleware:
    """Verifies every request carrying RunGrow service headers before route dispatch."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        raw_headers = {k.decode("latin-1").lower(): v.decode("latin-1")
                       for k, v in scope.get("headers", [])}
        has_service_headers = any(key.startswith("x-rungrow-") for key in raw_headers)
        if not has_service_headers:
            await self.app(scope, receive, send)
            return

        body_parts: list[bytes] = []
        body_size = 0
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            part = message.get("body", b"")
            body_size += len(part)
            if body_size > MAX_SIGNED_BODY_BYTES:
                response = HTTPException(status_code=413, detail="Signed service request body too large")
                await self._send_error(response, send)
                return
            body_parts.append(part)
            more_body = message.get("more_body", False)
        body = b"".join(body_parts)
        try:
            tenant_context = verify_rungrow_request(
                raw_headers, body,
                settings_secret(),
                tenant_mapping(),
            )
        except HTTPException as exc:
            await self._send_error(exc, send)
            return

        state = scope.setdefault("state", {})
        state["rungrow_service"] = tenant_context
        delivered = False

        async def replay_receive() -> Message:
            nonlocal delivered
            if delivered:
                return {"type": "http.request", "body": b"", "more_body": False}
            delivered = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _send_error(exc: HTTPException, send: Send) -> None:
        from starlette.responses import JSONResponse
        response = JSONResponse({"detail": exc.detail}, status_code=exc.status_code,
                                 headers=exc.headers)
        await response({"type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"},
                        "method": "POST", "scheme": "https", "path": "/", "raw_path": b"/",
                        "query_string": b"", "root_path": "", "headers": []},
                       _empty_receive, send)


async def _empty_receive() -> Message:
    return {"type": "http.request", "body": b"", "more_body": False}


def settings_secret() -> str:
    from core.config import settings
    return settings.RUNGROW_WORKFORCE_HMAC_SECRET


def tenant_mapping() -> dict[str, str]:
    from core.config import settings
    try:
        value: Any = json.loads(settings.RUNGROW_WORKFORCE_TENANT_MAP)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=503, detail="RUNGROW_WORKFORCE_TENANT_MAP must be valid JSON") from exc
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise HTTPException(status_code=503, detail="RUNGROW_WORKFORCE_TENANT_MAP must map tenant IDs to tenant IDs")
    return value


def validate_production_service_config(settings_obj) -> None:
    if settings_obj.ENVIRONMENT.lower() != "production":
        return
    if not settings_obj.DATABASE_URL or "localhost" in settings_obj.DATABASE_URL:
        raise RuntimeError("Production DATABASE_URL must point to the managed PostgreSQL database")
    if settings_obj.SECRET_KEY in {"dev-secret-change-in-production", ""} or len(settings_obj.SECRET_KEY) < 32:
        raise RuntimeError("Production SECRET_KEY must be a strong secret")
    if settings_obj.JWT_SECRET in {"dev-jwt-secret-change-in-production", ""} or len(settings_obj.JWT_SECRET) < 32:
        raise RuntimeError("Production JWT_SECRET must be a strong secret")
    if len(settings_obj.RUNGROW_WORKFORCE_HMAC_SECRET.encode("utf-8")) < 32:
        raise RuntimeError("RUNGROW_WORKFORCE_HMAC_SECRET must contain at least 32 bytes")
    try:
        mapping = json.loads(settings_obj.RUNGROW_WORKFORCE_TENANT_MAP)
    except json.JSONDecodeError as exc:
        raise RuntimeError("RUNGROW_WORKFORCE_TENANT_MAP must be valid JSON") from exc
    if not isinstance(mapping, dict):
        raise RuntimeError("RUNGROW_WORKFORCE_TENANT_MAP must be a JSON object")
