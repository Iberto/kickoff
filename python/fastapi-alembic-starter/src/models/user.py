from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models.shared.mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # created_at and updated_at are defined in the TimestampMixin
    # is_deleted and deleted_at are defined in the SoftDeleteMixin
    def __repr__(self) -> str:
        return f"<User {self.email}>"
