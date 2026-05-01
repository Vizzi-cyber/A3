"""
数据库连接与 ORM 基类
当前默认使用 SQLite，可通过环境变量切换为 PostgreSQL
"""
from datetime import datetime, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, QueuePool

from ..core.config import settings

# 根据数据库类型配置连接池
# SQLite 使用 StaticPool（单连接复用，避免文件锁竞争）
# PostgreSQL 使用 QueuePool（支持真实并发连接）
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# 条件构建引擎参数：QueuePool 支持 pool_size / max_overflow，StaticPool 不支持
_engine_kwargs: dict = {
    "pool_pre_ping": True,
}
if _is_sqlite:
    _engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
else:
    _engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    })

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)


# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()


@event.listens_for(Base, "before_insert", propagate=True)
def _set_created_at(mapper, connection, target):
    """自动填充 created_at 为 UTC 时间，避免 SQLite func.now() 生成 naive datetime"""
    if hasattr(target, "created_at") and target.created_at is None:
        target.created_at = datetime.now(timezone.utc)


@event.listens_for(Base, "before_update", propagate=True)
def _set_updated_at(mapper, connection, target):
    """自动填充 updated_at 为 UTC 时间"""
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(timezone.utc)


def get_db():
    """获取数据库会话（FastAPI Depends 用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
