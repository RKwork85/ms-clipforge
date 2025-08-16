from app.services.redis_api_service import AsyncRedisAPIService

# 单例服务
redis_service = AsyncRedisAPIService()

async def get_redis_service() -> AsyncRedisAPIService:
    """FastAPI 依赖注入"""
    return redis_service