import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅在控制台输出时使用）"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'ENDC': '\033[0m'        # 结束颜色
    }

    def format(self, record):
        if hasattr(record, 'request_id'):
            # 如果有请求ID，添加到日志中
            original_format = self._style._fmt
            self._style._fmt = f'%(asctime)s - %(name)s - %(levelname)s - [RequestID: {record.request_id}] - %(message)s'
        
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['ENDC']}"
        
        formatted = super().format(record)
        
        # 恢复原始格式
        if hasattr(record, 'request_id'):
            self._style._fmt = original_format
            
        return formatted

class RequestIdFilter(logging.Filter):
    """为日志记录添加请求ID的过滤器"""
    
    def filter(self, record):
        # 尝试从上下文中获取请求ID（如果使用了contextvars）
        request_id = getattr(record, 'request_id', None)
        if not request_id:
            # 可以从其他地方获取请求ID，比如全局变量或上下文
            record.request_id = getattr(logging, '_current_request_id', 'N/A')
        return True

def setup_logger(
    name: str = __name__,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_dir: 日志文件目录，默认为项目根目录/logs
        max_file_size: 单个日志文件最大大小（字节）
        backup_count: 保留的日志文件备份数量
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
    
    Returns:
        配置好的日志记录器
    """
    
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 日志格式
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(RequestIdFilter())
        logger.addHandler(console_handler)
    
    # 文件处理器
    if enable_file:
        if log_dir is None:
            log_dir = Path.cwd() / "logs"
        
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True, parents=True)
        
        # 主日志文件 - 使用轮转
        main_log_file = log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(RequestIdFilter())
        logger.addHandler(file_handler)
        
        # 错误日志文件 - 只记录ERROR和CRITICAL级别
        error_log_file = log_dir / f"{name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        error_handler.addFilter(RequestIdFilter())
        logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return setup_logger(name)

def log_execution_time(func):
    """装饰器：记录函数执行时间"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行完成，耗时: {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.3f}s，错误: {str(e)}")
            raise
    
    return wrapper

def set_request_id(request_id: str):
    """设置当前请求的ID，用于日志追踪"""
    logging._current_request_id = request_id

def clear_request_id():
    """清除请求ID"""
    if hasattr(logging, '_current_request_id'):
        delattr(logging, '_current_request_id')

# 默认日志配置
def configure_root_logger():
    """配置根日志记录器"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")
    
    setup_logger(
        name="fastapi_app",
        log_level=log_level,
        log_dir=Path(log_dir),
        enable_console=True,
        enable_file=True
    )

# 初始化时配置
configure_root_logger()

# 导出主要的日志记录器
logger = get_logger("ms-clipforge")