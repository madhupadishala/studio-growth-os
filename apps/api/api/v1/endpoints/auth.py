"""
Studio Growth OS - Authentication Endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from passlib.context import CryptContext
from prisma import Prisma

from core.config import settings
from core.database import get_db
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None
    tenant_id: str | None = None
    role: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_e164: str | None = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone_e164: str | None
    avatar_url: str | None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) if expires_delta is None else expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Prisma = Depends(get_db),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, tenant_id=tenant_id, role=role)
    except JWTError:
        raise credentials_exception

    user = await db.user.find_unique(where={"id": token_data.user_id})
    if user is None:
        raise credentials_exception

    membership = await db.membership.find_unique(
        where={"userId_tenantId": {"userId": user_id, "tenantId": token_data.tenant_id}}
    )
    if membership is None or membership.status != "active":
        raise credentials_exception

    return {
        "user": user,
        "tenant_id": token_data.tenant_id,
        "role": token_data.role,
        "membership": membership,
    }

def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Endpoints
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: Prisma = Depends(get_db)):
    """Register a new user (platform-level, not tenant-scoped)"""
    existing = await db.user.find_unique(where={"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    user = await db.user.create(
        data={
            "email": user_data.email,
            "name": user_data.name,
            "phoneE164": user_data.phone_e164,
            "passwordHash": hashed_password,  # Note: add passwordHash field to Prisma schema
        }
    )
    logger.info("User registered", user_id=user.id, email=user.email)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone_e164=user.phoneE164,
        avatar_url=user.avatarUrl,
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Prisma = Depends(get_db)):
    """Login and get access + refresh tokens"""
    user = await db.user.find_unique(where={"email": form_data.username})
    if not user or not verify_password(form_data.password, user.passwordHash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Get user's first active membership
    membership = await db.membership.find_first(
        where={"userId": user.id, "status": "active"},
        include={"tenant": True},
    )
    if not membership:
        raise HTTPException(status_code=403, detail="No active tenant membership")

    access_token = create_access_token(
        data={"sub": user.id, "tenant_id": membership.tenantId, "role": membership.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "tenant_id": membership.tenantId, "role": membership.role}
    )

    logger.info("User logged in", user_id=user.id, tenant_id=membership.tenantId)
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: Prisma = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(request.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Verify membership still exists and active
    membership = await db.membership.find_unique(
        where={"userId_tenantId": {"userId": user_id, "tenantId": tenant_id}}
    )
    if not membership or membership.status != "active":
        raise HTTPException(status_code=403, detail="Membership no longer active")

    access_token = create_access_token(data={"sub": user_id, "tenant_id": tenant_id, "role": role})
    new_refresh_token = create_refresh_token(data={"sub": user_id, "tenant_id": tenant_id, "role": role})

    return Token(access_token=access_token, refresh_token=new_refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user = current_user["user"]
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone_e164=user.phoneE164,
        avatar_url=user.avatarUrl,
    )

@router.post("/logout")
async def logout():
    """Logout (client should discard tokens)"""
    return {"message": "Successfully logged out"}

# Dependency for tenant-scoped endpoints
async def get_tenant_context(current_user: dict = Depends(get_current_user)) -> dict:
    """Extract tenant context for scoped operations"""
    return {
        "tenant_id": current_user["tenant_id"],
        "user_id": current_user["user"].id,
        "role": current_user["role"],
    }