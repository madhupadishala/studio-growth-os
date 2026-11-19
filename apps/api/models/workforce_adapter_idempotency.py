"""SQLAlchemy model for durable RunGrow adapter write idempotency."""
from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid

class Base(DeclarativeBase):
    pass

class WorkforceAdapterIdempotency(Base):
    __tablename__ = "workforce_adapter_idempotency"
    __table_args__ = (
        UniqueConstraint("external_tenant_id", "endpoint", "idempotency_key",
                         name="uq_workforce_adapter_idempotency"),
        CheckConstraint("status IN ('PROCESSING', 'COMPLETED')", name="ck_workforce_adapter_idempotency_status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_tenant_id: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PROCESSING")
    response_status_code: Mapped[int | None] = mapped_column(Integer)
    response_body_json: Mapped[dict | list | None] = mapped_column(JSONB)
    correlation_id: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
