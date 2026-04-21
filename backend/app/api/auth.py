"""
用户权限API
- 登录、注册、token管理
- JWT身份校验
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.user import UserModel
from ..core.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


class UserRegisterRequest(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=64)
    username: str = Field(..., min_length=1, max_length=128)
    email: Optional[str] = None
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    student_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
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


@router.post("/register")
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    existing = db.query(UserModel).filter(UserModel.student_id == request.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="student_id already exists")
    user = UserModel(
        student_id=request.student_id,
        username=request.username,
        email=request.email,
        hashed_password=pwd_context.hash(request.password),
        is_active=True,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "success", "message": "User registered", "student_id": user.student_id}


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(UserModel).filter(UserModel.student_id == request.student_id).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
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
