import asyncio
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
import structlog
from pydantic import ValidationError as PydanticValidationError
from structlog.stdlib import BoundLogger

from src.config import settings
from src.schemas.auth import TokenPayload

logger: BoundLogger = structlog.get_logger("security")


def _hash_password_sync(password: str) -> str:
    """Hash the password"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    """Verify plain against hashed"""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# Why async?
# bcrypt is CPU-bound, not I/O-bound
# asyncio.to_thread is a good way to run CPU-bound operations in a thread pool
# it's more efficient than running the operation in the main thread
# it's more efficient than running the operation in the event loop
# it's more efficient than running the operation in the main thread
# other requests will not be blocked by the hashing operation
# other requests will not be blocked by the verification operation
async def hash_password(password: str) -> str:
    """Async wrapper for bcrypt hashing (runs in thread pool)."""
    return await asyncio.to_thread(_hash_password_sync, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Async wrapper for bcrypt verification (runs in thread pool)."""
    return await asyncio.to_thread(
        _verify_password_sync, plain_password, hashed_password
    )


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    now = datetime.now(UTC)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {"sub": str(user_id), "exp": expire, "iat": now}

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode and validate a JWT"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError as e:
        logger.warning("jwt_expired_signature", error=str(e))
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("jwt_invalid_token", error=str(e))
        return None
    except PydanticValidationError as e:
        logger.warning("jwt_payload_invalid", error=str(e))
        return None
