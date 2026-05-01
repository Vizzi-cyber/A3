"""
用户权限API
- 登录、注册、token管理
- JWT身份校验
"""
import asyncio
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import get_db
from ..models.user import UserModel

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

class UserRegisterRequest(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=64)
    username: str = Field(..., min_length=1, max_length=128)
    email: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含至少一个字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserLoginRequest(BaseModel):
    student_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def _verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_student_id(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    """依赖注入：从请求头提取并校验token（允许匿名）"""
    if not credentials:
        return "anonymous"
    token = credentials.credentials
    student_id = _verify_token(token)
    if not student_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return student_id


async def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    """严格认证：无token或token无效时直接抛401"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    student_id = _verify_token(token)
    if not student_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return student_id


def verify_token_for_websocket(token: str | None) -> str | None:
    """用于WebSocket的token校验（不抛HTTP异常，返回None表示失败）"""
    if not token:
        return None
    return _verify_token(token)


@router.post("/register")
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    existing = db.query(UserModel).filter(UserModel.student_id == request.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="student_id already exists")
    hashed = await asyncio.to_thread(pwd_context.hash, request.password)
    user = UserModel(
        student_id=request.student_id,
        username=request.username,
        email=request.email,
        hashed_password=hashed,
        is_active=True,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "success", "message": "User registered", "student_id": user.student_id}


# 临时调试端点：仅 DEBUG 模式可用
@router.post("/_debug/validate-password")
async def debug_validate(password: str):
    from ..core.config import settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    from pydantic import ValidationError
    try:
        req = UserRegisterRequest(student_id="debug", username="debug", password=password)
        return {"valid": True, "password": req.password}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(UserModel).filter(UserModel.student_id == request.student_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    valid = await asyncio.to_thread(pwd_context.verify, request.password, user.hashed_password)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_access_token({"sub": user.student_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_DAYS * 86400,
    }


@router.get("/me")
async def get_me(student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    if student_id == "anonymous":
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(UserModel).filter(UserModel.student_id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "success",
        "data": {
            "student_id": user.student_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    }
