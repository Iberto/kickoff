from dataclasses import dataclass

import structlog
from structlog.stdlib import BoundLogger

import src.exceptions.users as exc
from src.config import settings
from src.models.user import User
from src.repositories.user import UserRepository
from src.security import create_access_token, hash_password, verify_password

logger: BoundLogger = structlog.get_logger()


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    expires_in: int


class AuthService:
    """Business"""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise exc.EmailAlreadyExistsError(email)
        user = User(email=email, hashed_password=await hash_password(password))
        return await self.user_repo.create(user)
        # return await self.user_repo.upsert(user)

    async def login(self, email: str, password: str) -> LoginResult:
        user = await self.user_repo.get_by_email(email)
        if not user or not await verify_password(password, user.hashed_password):
            logger.info("login_failed_invalid_credentials")
            raise exc.InvalidCredentialsOrUserDisabledError()

        token = create_access_token(user.id)
        expires_in = settings.jwt_expire_minutes * 60

        return LoginResult(access_token=token, expires_in=expires_in)
