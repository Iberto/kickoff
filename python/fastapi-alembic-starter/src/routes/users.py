from fastapi import APIRouter, Request, status

from src.dependencies import AuthServiceDep, CurrentUser
from src.limiter import limiter
from src.schemas.auth import LoginResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# For versioning
# router = APIRouter(prefix="/v1")
# router.include_router(_auth_router)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")  # NOTE: limiter requires Request as first param
async def register(request: Request, data: UserRegister, authService: AuthServiceDep):
    """Create a new user"""
    return await authService.register(data.email, data.password)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # NOTE: limiter requires Request as first param
async def login(request: Request, data: UserLogin, authService: AuthServiceDep):
    """Login"""
    result = await authService.login(data.email, data.password)
    return LoginResponse(access_token=result.access_token, expires_in=result.expires_in)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: CurrentUser):
    """Get me"""

    return user
