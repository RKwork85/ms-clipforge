import datetime
import uvicorn
from fastapi import FastAPI
from app.utils.logger import logger
from app.apis.v1.endpoints import oss_upload, user_upload, tasks_detail  # 导入 redis_api 路由
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ms-clipforge")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """服务健康检查"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}

# 将文件上传端点路由添加到 FastAPI 应用中
app.include_router(user_upload.router, prefix="/v1/user_upload", tags=["user_upload"])

# 将OSS上传端点路由添加到 FastAPI 应用中
app.include_router(oss_upload.router, prefix="/v1/oss_upload", tags=["oss_upload"])

# 将Redis相关端点路由添加到 FastAPI 应用中
app.include_router(tasks_detail.router, prefix="/v1/tasks_detail", tags=["tasks_detail"])

if __name__ == "__main__":
    uvicorn.run(
        app='main:app',
        host="0.0.0.0",
        port=8888,
        log_level="info",
        access_log=True,
        reload=True
    )
