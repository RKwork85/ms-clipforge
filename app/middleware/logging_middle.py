import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import get_logger, set_request_id, clear_request_id

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""
    
    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 为每个请求生成唯一ID
        request_id = str(uuid.uuid4())[:8]
        set_request_id(request_id)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 记录请求信息
        if request.url.path not in self.skip_paths:
            await self._log_request(request, request_id, client_ip)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            if request.url.path not in self.skip_paths:
                self._log_response(request, response, process_time, request_id)
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"请求处理异常 | RequestID: {request_id} | "
                f"方法: {request.method} | 路径: {request.url.path} | "
                f"客户端: {client_ip} | 耗时: {process_time:.4f}s | "
                f"异常: {str(e)}",
                exc_info=True
            )
            raise
        finally:
            # 清理请求ID
            clear_request_id()
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _log_request(self, request: Request, request_id: str, client_ip: str):
        """记录请求信息"""
        # 获取请求体（小心处理，避免消耗stream）
        body_info = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    # 注意：这里需要小心处理，因为body只能读取一次
                    # 在实际应用中，可能需要更复杂的处理
                    body_info = "JSON数据"
                except:
                    body_info = "无法解析的请求体"
            elif "multipart/form-data" in content_type:
                body_info = "文件上传"
            elif "application/x-www-form-urlencoded" in content_type:
                body_info = "表单数据"
        
        logger.info(
            f"请求开始 | RequestID: {request_id} | "
            f"方法: {request.method} | 路径: {request.url.path} | "
            f"查询参数: {dict(request.query_params)} | "
            f"客户端: {client_ip} | "
            f"用户代理: {request.headers.get('user-agent', 'N/A')[:100]} | "
            f"请求体类型: {body_info}"
        )
    
    def _log_response(self, request: Request, response: Response, process_time: float, request_id: str):
        """记录响应信息"""
        # 根据状态码确定日志级别
        if response.status_code >= 500:
            log_level = logger.error
        elif response.status_code >= 400:
            log_level = logger.warning
        else:
            log_level = logger.info
        
        log_level(
            f"请求完成 | RequestID: {request_id} | "
            f"方法: {request.method} | 路径: {request.url.path} | "
            f"状态码: {response.status_code} | "
            f"耗时: {process_time:.4f}s | "
            f"响应大小: {response.headers.get('content-length', 'N/A')} bytes"
        )

class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件，用于在整个请求生命周期中保持上下文信息"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 可以在这里添加更多上下文信息
        request.state.start_time = time.time()
        request.state.request_id = getattr(request.state, 'request_id', str(uuid.uuid4())[:8])
        
        response = await call_next(request)
        return response