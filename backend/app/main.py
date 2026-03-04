"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings, CORS_ORIGINS
from app.api import alerts, compliance, excel, followsell

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="亚马逊上新跟卖自动化系统",
    version=settings.app_version
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: 实际检查数据库连接
        "redis": "connected"  # TODO: 实际检查 Redis 连接
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


# 注册路由（待实现）
# from app.api import listing_qa, workflow
app.include_router(compliance.router)
app.include_router(excel.router)
app.include_router(followsell.router)
app.include_router(alerts.router)
# app.include_router(listing_qa.router)
# app.include_router(workflow.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    # TODO: 初始化数据库连接
    # TODO: 初始化 Redis 连接
    # TODO: 加载规则库


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"Shutting down {settings.app_name}")
    # TODO: 关闭数据库连接
    # TODO: 关闭 Redis 连接


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
