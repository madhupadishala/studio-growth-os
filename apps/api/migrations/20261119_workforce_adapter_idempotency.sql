CREATE TABLE IF NOT EXISTS workforce_adapter_idempotency (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_tenant_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_hash CHAR(64) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PROCESSING', 'COMPLETED')),
    response_status_code INTEGER,
    response_body_json JSONB,
    correlation_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT uq_workforce_adapter_idempotency UNIQUE (external_tenant_id, endpoint, idempotency_key)
);
CREATE INDEX IF NOT EXISTS ix_workforce_adapter_idempotency_created_at
    ON workforce_adapter_idempotency (created_at);
