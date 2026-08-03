import uuid
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func


class PublicIdMixin:
    public_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OwnedMixin:
    @declared_attr
    def user_id(cls):
        return Column(
            Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )


class SoftDeleteMixin:
    is_deleted = Column(Boolean, nullable=False, default=False)
