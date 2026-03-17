import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.stdlib import BoundLogger

from src.models.user import User

logger: BoundLogger = structlog.get_logger()


class UserRepository:
    """Data access layer for User entity"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # TODO: add get_many

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by id - by default discards deleted users"""
        result = await self.db.execute(
            select(User).where(User.id == user_id).where(User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email - by default discards deleted users"""
        result = await self.db.execute(
            select(User).where(User.email == email).where(User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create a new user"""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, **fields) -> User:
        """Update a user"""
        for field, value in fields.items():
            if hasattr(user, field):
                setattr(user, field, value)
            else:
                logger.warning(
                    "Updating an user with unknown field", field=field, value=value
                )
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def upsert(self, user: User) -> User:
        """Insert or update a user based on email (right now it's the constraint)"""

        stmt = insert(User).values(
            email=user.email,
            hashed_password=user.hashed_password,
            is_superuser=user.is_superuser,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_={
                "hashed_password": stmt.excluded.hashed_password,
                "is_superuser": stmt.excluded.is_superuser,
            },
        )

        await self.db.execute(stmt)
        await self.db.flush()

        # Cant use refresh here due rawness of insert/on_conflict_update
        return await self.get_by_email(user.email)

    async def delete(self, user: User, is_soft_deleted: bool = True):
        """Always soft delete a user"""
        await self.update(user, is_deleted=True)
        await self.db.flush()
        return user

    async def restore(self, user: User):
        """Restore a soft deleted user"""
        await self.update(user, is_deleted=False)
        await self.db.flush()
        return user
