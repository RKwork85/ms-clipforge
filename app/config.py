import os
from pathlib import Path
from typing import List

# 基础路径配置
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "user_uploads"))
LOG_DIR = Path(os.getenv("LOG_DIR", BASE_DIR / "logs"))

# 数据库配置
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_MAX_FILE_SIZE = int(os.getenv("LOG_MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
LOG_ENABLE_CONSOLE = os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true"
LOG_ENABLE_FILE = os.getenv("LOG_ENABLE_FILE", "true").lower() == "true"

# 应用配置
APP_NAME = os.getenv("APP_NAME", "ms-clipforge")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 文件上传配置
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 200 * 1024 * 1024))  # 100MB
ALLOWED_FILE_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS", "").split(",") if os.getenv("ALLOWED_FILE_EXTENSIONS") else []
UPLOAD_TIMEOUT = int(os.getenv("UPLOAD_TIMEOUT", 300))  # 5分钟

# 安全配置
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "rkwork,muzi").split(",")

# CORS配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["*"]

# API配置
API_V1_PREFIX = "/api/v1"

# 监控配置
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
METRICS_PATH = os.getenv("METRICS_PATH", "/metrics")

# 确保必要的目录存在
def create_directories():
    """创建必要的目录"""
    UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    LOG_DIR.mkdir(exist_ok=True, parents=True)

"""
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # OSS服务配置
    OSS_SERVICE_URL: str = "http://localhost:8889"  # OSS上传服务地址
    OSS_SERVICE_TIMEOUT: int = 120  # 超时时间(秒)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
"""

# 在导入时创建目录
create_directories()