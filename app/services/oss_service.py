import httpx
import asyncio
from typing import List, Dict, Any, Optional, Union
import aiofiles
from pathlib import Path
import json
from app.utils.logger import get_logger

logger = get_logger(__name__)

class OSSService:
    """OSS服务封装类 - 调用外部OSS上传服务"""
    
    def __init__(self, oss_service_url: str = "http://localhost:8889"):
        """
        初始化OSS服务
        
        Args:
            oss_service_url: OSS上传服务的URL地址
        """
        self.base_url = oss_service_url.rstrip('/')
        self.timeout = httpx.Timeout(30.0, read=120.0)  # 增加读取超时时间
        
    async def health_check(self) -> Dict[str, Any]:
        """
        检查OSS服务健康状态
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
                # print("检查状态点：",response.json())
                # {'status': 'healthy', 'service': 'OSS多文件上传服务', 'oss_client_status': '已初始化'}
        except Exception as e:
            logger.error(f"OSS服务健康检查失败: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def upload_single_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        上传单个文件到OSS
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {file_path}",
                "file_name": file_path.name
            }
        
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                file_content = await file.read()
            
            files = {
                'file': (file_path.name, file_content, 'application/octet-stream')
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/upload/single",  # 修正路径
                    files=files
                )
                response.raise_for_status()
                result = response.json()     # oss服务对返回数据的定义接口
                print("返回的内容",result)
                logger.info(f"单文件上传成功: {file_path.name}")
                return result
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误 {e.response.status_code}: {e.response.text}"
            logger.error(f"单文件上传失败: {file_path.name}, {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_name": file_path.name
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"单文件上传异常: {file_path.name}, {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_name": file_path.name
            }
    
    async def upload_multiple_files(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        批量上传多个文件到OSS
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            Dict[str, Any]: 批量上传结果
        """
        if not file_paths:
            return {
                "success": False,
                "error": "文件路径列表为空",
                "summary": {"total": 0, "successful": 0, "failed": 0}
            }
        
        try:
            # 准备文件数据
            files = []
            valid_files = []
            
            for file_path in file_paths:
                file_path = Path(file_path)
                if file_path.exists():
                    try:
                        async with aiofiles.open(file_path, 'rb') as file:
                            file_content = await file.read()
                        files.append(('files', (file_path.name, file_content, 'application/octet-stream')))
                        valid_files.append(file_path.name)
                    except Exception as e:
                        logger.warning(f"读取文件失败，跳过: {file_path.name}, 错误: {str(e)}")
                else:
                    logger.warning(f"文件不存在，跳过: {file_path}")
            
            if not files:
                return {
                    "success": False,
                    "error": "没有有效的文件可以上传",
                    "summary": {"total": 0, "successful": 0, "failed": len(file_paths)}
                }
            
            # 发送批量上传请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/upload/multiple",  # 修正路径
                    files=files
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"批量上传完成: {result['summary']}")
                print(result)
                return result
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误 {e.response.status_code}: {e.response.text}"
            logger.error(f"批量上传失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "summary": {"total": len(file_paths), "successful": 0, "failed": len(file_paths)}
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"批量上传异常: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "summary": {"total": len(file_paths), "successful": 0, "failed": len(file_paths)}
            }
    
    async def upload_text_content(self, text: str, filename: str = "text_file.txt") -> Dict[str, Any]:
        """
        上传文本内容到OSS
        
        Args:
            text: 文本内容
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        try:
            # 修正：使用表单数据而不是JSON
            data = {
                "text": text,
                "filename": filename
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/upload/text",  # 修正路径
                    data=data  # 使用data而不是json
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"文本上传成功: {filename}")
                return result
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误 {e.response.status_code}: {e.response.text}"
            logger.error(f"文本上传失败: {filename}, {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_name": filename
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"文本上传异常: {filename}, {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_name": filename
            }

# 全局OSS服务实例
oss_service = OSSService()