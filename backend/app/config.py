"""
配置管理模块
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR.parent / "templates"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# BU2Ama 核心引擎配置
BU2AMA_ENGINE = os.getenv("BU2AMA_ENGINE", "auto")
BU2AMA_CORE_PATH = os.getenv(
    "BU2AMA_CORE_PATH",
    str((BASE_DIR.parent.parent / "BU2Ama" / "backend" / "app" / "core").resolve()),
)
BU2AMA_DATA_PATH = os.getenv(
    "BU2AMA_DATA_PATH",
    str((BASE_DIR.parent.parent / "BU2Ama" / "data").resolve()),
)
BU2AMA_TEMPLATES_PATH = os.getenv(
    "BU2AMA_TEMPLATES_PATH",
    str((BASE_DIR.parent.parent / "BU2Ama" / "templates").resolve()),
)
BU2AMA_API_BASE_URL = os.getenv("BU2AMA_API_BASE_URL", "http://127.0.0.1:8001")
BU2AMA_TIMEOUT_SECONDS = float(os.getenv("BU2AMA_TIMEOUT_SECONDS", "30"))


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "Amazon Listing Automation"
    app_version: str = "0.1.0"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS 配置
    cors_origins: str = "http://localhost:5174"

    # 数据库配置
    database_url: str = "postgresql://postgres:postgres@localhost:5432/amazon_listing"

    # BU2Ama 引擎配置
    bu2ama_engine: str = BU2AMA_ENGINE
    bu2ama_core_path: str = BU2AMA_CORE_PATH
    bu2ama_api_base_url: str = BU2AMA_API_BASE_URL
    bu2ama_timeout_seconds: float = BU2AMA_TIMEOUT_SECONDS

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # 合规检查配置
    enable_trademark_check: bool = True
    enable_ip_check: bool = True
    enable_forbidden_word_check: bool = True
    risk_threshold: float = 0.7

    # 质检配置
    min_title_length: int = 50
    max_title_length: int = 200
    required_images: int = 5
    enable_variant_check: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

# CORS 源列表
CORS_ORIGINS = settings.cors_origins.split(",")

# 合规检查配置
COMPLIANCE_CONFIG = {
    "enable_trademark_check": settings.enable_trademark_check,
    "enable_ip_check": settings.enable_ip_check,
    "enable_forbidden_word_check": settings.enable_forbidden_word_check,
    "risk_threshold": settings.risk_threshold,
}

# 质检配置
QA_CONFIG = {
    "min_title_length": settings.min_title_length,
    "max_title_length": settings.max_title_length,
    "required_images": settings.required_images,
    "enable_variant_check": settings.enable_variant_check,
}
