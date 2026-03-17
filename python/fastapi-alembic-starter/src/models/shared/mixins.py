from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, validates

# Use declared_attr so SQLAlchemy copies the column definition per
# concrete table rather than sharing a single Column object (which
# would silently break multi-table inheritance and cause mapping
# collisions when the mixin is used by more than one model).
# ===============================================================
# Use declared_attr so that each ORM model receives its own Column instance.
# If the columns were defined directly on the mixin, Python would create a
# single Column object and all models inheriting from the mixin would share it.
# However, in SQLAlchemy a Column can belong to only one Table. Reusing the
# same Column across multiple models would therefore cause mapping conflicts
# or incorrect table bindings when the ORM builds the metadata.
#
# declared_attr solves this by turning the attribute into a factory: the
# function is executed for every concrete model class that inherits the mixin,
# producing a fresh mapped_column for that specific table. This makes the
# mixin safe to reuse across many models and prevents subtle issues with
# multi-table inheritance or ORM mapping collisions.
# ===============================================================


class TimestampMixin:
    """Adds server-managed created_at / updated_at to any ORM model."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    """Adds soft delete to any ORM model."""

    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:
        return mapped_column(Boolean, default=False, nullable=False)

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), nullable=True)

    @validates("is_deleted")
    def _sync_deleted_at(self, _: str, value: bool) -> bool:
        if value is True:
            self.deleted_at = datetime.now(UTC)
        elif value is False:
            self.deleted_at = None
        return value
