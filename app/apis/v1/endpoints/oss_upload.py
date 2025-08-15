from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.file_upload.oss_uploader import oss_uploader
from app.utils.logger import logger

router = APIRouter()

# 请求模型
class SingleFileUploadRequest(BaseModel):
    """单文件上传请求"""
    file_path: str = Field(..., description="文件路径")

class BatchFileUploadRequest(BaseModel):
    """批量文件上传请求"""
    file_paths: List[str] = Field(..., description="文件路径列表")

class TextUploadRequest(BaseModel):
    """文本上传请求"""
    content: str = Field(..., description="文本内容")
    filename: str = Field(default="text_content.txt", description="文件名")

class DirectoryUploadRequest(BaseModel):
    """目录上传请求"""
    directory_path: str = Field(..., description="目录路径")
    file_extensions: Optional[List[str]] = Field(default=None, description="允许的文件扩展名")

@router.get("/status")
async def check_oss_service_status():
    """检查OSS服务状态"""
    try:
        is_available = await oss_uploader.check_service_status()
        return {
            "oss_service_available": is_available,
            "status": "healthy" if is_available else "unhealthy",
            "service_name": "OSS Upload Service"
        }
    except Exception as e:
        logger.error(f"检查OSS服务状态异常: {str(e)}")
        return {
            "oss_service_available": False,
            "status": "error",
            "error": str(e)
        }

@router.post("/upload/single")
async def upload_single_file_to_oss(request: SingleFileUploadRequest):
    """上传单个文件到OSS"""
    try:
        logger.info(f"开始上传单个文件到OSS: {request.file_path}")
        result = await oss_uploader.upload_file(request.file_path)
        
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "文件上传到OSS成功",
                    "data": result
                }
            )
            
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "文件上传到OSS失败",
                    "error": result.get("error", "未知错误")
                }
            )
    except Exception as e:
        logger.error(f"OSS单文件上传异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OSS上传过程中发生错误: {str(e)}"
        )

@router.post("/upload/batch")
async def upload_batch_files_to_oss(request: BatchFileUploadRequest):
    """批量上传文件到OSS"""
    try:
        logger.info(f"开始批量上传文件到OSS，文件数量: {len(request.file_paths)}")
        result = await oss_uploader.upload_files_batch(request.file_paths)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "批量上传到OSS完成",
                "data": result
            }
        )
    except Exception as e:
        logger.error(f"OSS批量上传异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OSS批量上传过程中发生错误: {str(e)}"
        )

@router.post("/upload/text")
async def upload_text_to_oss(request: TextUploadRequest):
    """上传文本内容到OSS"""
    try:
        logger.info(f"开始上传文本内容到OSS: {request.filename}")
        result = await oss_uploader.upload_text(request.content, request.filename)
        
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "文本上传到OSS成功",
                    "data": result
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "文本上传到OSS失败",
                    "error": result.get("error", "未知错误")
                }
            )
    except Exception as e:
        logger.error(f"OSS文本上传异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OSS文本上传过程中发生错误: {str(e)}"
        )

@router.post("/upload/directory")
async def upload_directory_to_oss(request: DirectoryUploadRequest):
    """上传目录中的文件到OSS"""
    try:
        logger.info(f"开始上传目录到OSS: {request.directory_path}")
        result = await oss_uploader.upload_directory(
            request.directory_path, 
            request.file_extensions
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "目录上传到OSS完成",
                "data": result
            }
        )
    except Exception as e:
        logger.error(f"OSS目录上传异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OSS目录上传过程中发生错误: {str(e)}"
        )
