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
    DEBUG: bool = False
    SECRET_KEY: str = ""

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ]

    def model_post_init(self, __context):
        """Pydantic v2 post-init: 校验安全关键配置并合并动态 CORS 域名"""
        # 合并环境变量中的 CORS 域名（逗号分隔）
        import os
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            extra = [o.strip() for o in cors_env.split(",") if o.strip()]
            object.__setattr__(self, 'ALLOWED_ORIGINS', self.ALLOWED_ORIGINS + extra)

        if not self.DEBUG:
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "生产环境必须设置强SECRET_KEY（至少32字符）。"
                    "建议运行: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
        else:
            # DEBUG模式：如果未设置，使用默认dev key并发出警告
            if not self.SECRET_KEY:
                import warnings
                warnings.warn(
                    "DEBUG模式使用默认SECRET_KEY，生产部署前务必设置环境变量！",
                    RuntimeWarning,
                    stacklevel=2,
                )
                object.__setattr__(self, 'SECRET_KEY', "dev-secret-32-chars-long-please-change-me!")

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_learning_v2.db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # 大模型提供商选择: spark / deepseek / openai / bigmodel
    DEFAULT_LLM_PROVIDER: str = "bigmodel"

    # 科大讯飞配置（支持 HTTP OpenAI 兼容接口）
    SPARK_API_KEY: Optional[str] = None
    SPARK_HTTP_BASE_URL: str = "https://spark-api-open.xf-yun.com/v1"
    SPARK_MODEL: str = "generalv3.5"

    # DeepSeek配置（可选）
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # OpenAI配置（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"

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
        extra = "ignore"


# 全局配置实例
settings = Settings()
