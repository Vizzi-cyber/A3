"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""

    # 应用信息
    APP_NAME: str = "AI Learning System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ]

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_learning.db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DEBUG and len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production mode")

    # 科大讯飞配置
    SPARK_APP_ID: Optional[str] = None
    SPARK_API_KEY: Optional[str] = None
    SPARK_API_SECRET: Optional[str] = None
    SPARK_MODEL_ENDPOINT: str = "wss://spark-api.xf-yun.com/v3.1/chat"

    # 大模型提供商选择: spark / deepseek / openai / bigmodel
    DEFAULT_LLM_PROVIDER: str = "bigmodel"

    # DeepSeek配置（可选）
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # OpenAI配置（可选）
    OPENAI_API_KEY: Optional[str] = None

    # 智谱AI (BigModel) 配置（可选，支持 GLM-4V 等图文模型）
    BIGMODEL_API_KEY: Optional[str] = None
    BIGMODEL_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    BIGMODEL_MODEL: str = "glm-4.6v"

    # 火山引擎视觉智能（文生图）配置
    VOLC_ACCESS_KEY: Optional[str] = None
    VOLC_SECRET_KEY: Optional[str] = None
    VOLC_VISUAL_ENDPOINT: str = "https://visual.volcengineapi.com"
    VOLC_REGION: str = "cn-north-1"
    VOLC_SERVICE: str = "cv"

    # 火山方舟（ARK）文生图配置
    ARK_API_KEY: Optional[str] = None
    ARK_IMAGE_ENDPOINT: str = "ark-d8c6b140-28d3-4525-8a83-2dca0e99fa1f-d8d59"
    ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3/invoke"

    # LangSmith配置（可选）
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "ai-learning-system"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
