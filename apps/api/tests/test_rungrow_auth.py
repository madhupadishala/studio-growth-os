import hashlib
import hmac
import time

import pytest
from fastapi import HTTPException

from core.rungrow_auth import EXPECTED_PRODUCT_ID, verify_rungrow_request, validate_production_service_config
from types import SimpleNamespace


SECRET = "test-rungrow-workforce-secret-32-bytes"
EXTERNAL_TENANT = "studio-tenant-01"
WORKFORCE_TENANT = "rungrow-org-01"


def signed_headers(body: bytes, *, timestamp: int | None = None, product_id=EXPECTED_PRODUCT_ID):
    issued = int(time.time()) if timestamp is None else timestamp
    binding = ".".join((str(issued), product_id, WORKFORCE_TENANT, EXTERNAL_TENANT,
                        "photo-studio-growth-os:read", hashlib.sha256(body).hexdigest())).encode()
    signature = "sha256=" + hmac.new(SECRET.encode(), binding, hashlib.sha256).hexdigest()
    return {
        "x-rungrow-signature": signature,
        "x-rungrow-timestamp": str(issued),
        "x-rungrow-product-id": product_id,
        "x-rungrow-external-tenant-id": EXTERNAL_TENANT,
        "x-rungrow-tenant-id": WORKFORCE_TENANT,
        "x-rungrow-scopes": "photo-studio-growth-os:read",
        "x-correlation-id": "contract-test-001",
    }


def test_valid_signed_request_binds_external_tenant_product_and_workforce_org():
    body = b'{"range":"30d"}'
    context = verify_rungrow_request(signed_headers(body), body, SECRET,
                                     {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert context["external_tenant_id"] == EXTERNAL_TENANT
    assert context["workforce_tenant_id"] == WORKFORCE_TENANT
    assert context["product_id"] == EXPECTED_PRODUCT_ID


def test_signature_rejects_body_tampering():
    body = b'{"range":"30d"}'
    with pytest.raises(HTTPException) as error:
        verify_rungrow_request(signed_headers(body), b'{"range":"90d"}', SECRET,
                               {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert error.value.status_code == 401


def test_signature_rejects_expired_timestamp_and_wrong_product():
    body = b"{}"
    with pytest.raises(HTTPException) as expired:
        verify_rungrow_request(signed_headers(body, timestamp=int(time.time()) - 301),
                               body, SECRET, {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert expired.value.status_code == 401
    with pytest.raises(HTTPException) as wrong_product:
        verify_rungrow_request(signed_headers(body, product_id="another-product"),
                               body, SECRET, {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert wrong_product.value.status_code == 403


def test_signature_rejects_unmapped_or_cross_bound_tenant():
    body = b"{}"
    with pytest.raises(HTTPException) as unmapped:
        verify_rungrow_request(signed_headers(body), body, SECRET, {})
    assert unmapped.value.status_code == 403
    headers = signed_headers(body)
    headers["x-rungrow-tenant-id"] = EXTERNAL_TENANT
    with pytest.raises(HTTPException) as same_tenant:
        verify_rungrow_request(headers, body, SECRET, {EXTERNAL_TENANT: EXTERNAL_TENANT})
    assert same_tenant.value.status_code == 403


def test_signature_requires_strong_shared_secret_and_all_headers():
    body = b"{}"
    with pytest.raises(HTTPException) as weak:
        verify_rungrow_request(signed_headers(body), body, "short",
                               {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert weak.value.status_code == 503
    headers = signed_headers(body)
    headers.pop("x-rungrow-external-tenant-id")
    with pytest.raises(HTTPException) as missing:
        verify_rungrow_request(headers, body, SECRET, {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert missing.value.status_code == 401



def test_production_service_configuration_fails_closed_without_hmac_secret():
    production = SimpleNamespace(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://studio:secret@db.example.com/studio",
        SECRET_KEY="strong-secret-value-that-is-at-least-32-bytes",
        JWT_SECRET="strong-jwt-secret-value-that-is-at-least-32-bytes",
        RUNGROW_WORKFORCE_HMAC_SECRET="",
        RUNGROW_WORKFORCE_TENANT_MAP="{}",
    )
    with pytest.raises(RuntimeError, match="HMAC_SECRET"):
        validate_production_service_config(production)


def test_signature_binds_canonical_workforce_scopes():
    body = b'{"range":"30d"}'
    headers = signed_headers(body)
    headers["x-rungrow-scopes"] = "photo-studio-growth-os:write"
    with pytest.raises(HTTPException) as error:
        verify_rungrow_request(headers, body, SECRET, {EXTERNAL_TENANT: WORKFORCE_TENANT})
    assert error.value.status_code == 401
