from typing import List, Union, Dict, Any
from pathlib import Path
from app.services.oss_service import oss_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class OSSUploader:
    """OSS上传器 - 业务逻辑封装"""
    
    def __init__(self):
        self.oss_service = oss_service
    
    async def check_service_status(self) -> bool:
        """检查OSS服务是否可用"""
        try:
            health_status = await self.oss_service.health_check()
            return health_status.get("status") == "healthy"
        except Exception as e:
            logger.error(f"检查OSS服务状态失败: {str(e)}")
            return False
    
    async def upload_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        上传单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        if not await self.check_service_status():  # bool
            return {
                "success": False,
                "error": "OSS服务不可用",
                "file_name": Path(file_path).name
            }
        # {'status': 'healthy', 'service': 'OSS多文件上传服务', 'oss_client_status': '已初始化'}
        return await self.oss_service.upload_single_file(file_path)
    
    async def upload_files_batch(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        批量上传文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            Dict[str, Any]: 批量上传结果
        """
        if not await self.check_service_status():
            return {
                "success": False,
                "error": "OSS服务不可用",
                "summary": {"total": len(file_paths), "successful": 0, "failed": len(file_paths)}
            }
        
        return await self.oss_service.upload_multiple_files(file_paths)
    
    async def upload_text(self, content: str, filename: str = "text_content.txt") -> Dict[str, Any]:
        """
        上传文本内容
        
        Args:
            content: 文本内容
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        if not await self.check_service_status():
            return {
                "success": False,
                "error": "OSS服务不可用",
                "file_name": filename
            }
        
        return await self.oss_service.upload_text_content(content, filename)
    
    async def upload_directory(self, directory_path: Union[str, Path], 
                             file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        上传整个目录的文件
        
        Args:
            directory_path: 目录路径
            file_extensions: 允许的文件扩展名列表，如 ['.jpg', '.png', '.pdf']
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            return {
                "success": False,
                "error": f"目录不存在或不是有效目录: {directory_path}",
                "summary": {"total": 0, "successful": 0, "failed": 0}
            }
        
        # 收集目录中的文件
        file_paths = []
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                if file_extensions:
                    if file_path.suffix.lower() in file_extensions:
                        file_paths.append(file_path)
                else:
                    file_paths.append(file_path)
        
        logger.info(f"目录 {directory_path} 中找到 {len(file_paths)} 个文件")
        
        if not file_paths:
            return {
                "success": True,
                "message": "目录中没有找到匹配的文件",
                "summary": {"total": 0, "successful": 0, "failed": 0}
            }
        
        return await self.upload_files_batch(file_paths)

# 全局上传器实例
oss_uploader = OSSUploader()