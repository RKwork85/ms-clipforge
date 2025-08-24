# app/apis/v1/oss_upload.py
"""
OSS文件上传客户端接口 - 用于请求已存在的OSS服务
"""

import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional

# 创建路由实例
router = APIRouter()

# OSS服务的基础URL（根据实际部署地址修改）
OSS_SERVICE_BASE_URL = "http://localhost:8890"  # 默认地址，请根据实际情况修改

async def make_oss_request(
    endpoint: str, 
    method: str = "POST", 
    files: Optional[dict] = None,
    data: Optional[dict] = None,
    params: Optional[dict] = None
):
    """
    向OSS服务发送请求的通用函数
    """
    url = f"{OSS_SERVICE_BASE_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 发送请求
            if method.upper() == "POST":
                if files:
                    # multipart/form-data 请求
                    response = await client.post(url, files=files, params=params)
                elif data:
                    # application/json 请求
                    response = await client.post(url, json=data, params=params)
                else:
                    response = await client.post(url, params=params)
            else:
                # GET请求
                response = await client.get(url, params=params)
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OSS服务请求失败: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"无法连接到OSS服务: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OSS请求处理错误: {str(e)}"
        )

@router.get("/health")
async def oss_health_check():
    """
    OSS服务健康检查
    """
    try:
        result = await make_oss_request("/health", "GET")
        return {
            "status": "success",
            "message": "OSS服务连接正常",
            "oss_service_status": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OSS服务健康检查失败: {str(e)}"
        )

@router.post("/single")
async def upload_single(
    file: UploadFile = File(...),
    upload_path: str = Query("", description="文件上传路径")
):
    """
    单文件上传接口 - 转发到OSS服务
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 准备文件数据
        files = {
            "file": (file.filename, file_content, file.content_type)
        }
        
        # 准备查询参数
        params = {}
        if upload_path:
            params["upload_path"] = upload_path
        
        # 转发到OSS服务
        result = await make_oss_request("/upload/single", "POST", files=files, params=params)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )
    finally:
        # 重置文件指针
        await file.seek(0)

@router.post("/multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    upload_path: str = Query("", description="文件上传路径")
):
    """
    多文件上传接口 - 转发到OSS服务
    """
    if not files:
        raise HTTPException(status_code=400, detail="未选择文件")
    
    try:
        # 准备查询参数
        params = {}
        if upload_path:
            params["upload_path"] = upload_path
        
        # 准备文件数据 - 使用列表而不是字典
        files_list = []
        for file in files:
            file_content = await file.read()
            files_list.append(("files", (file.filename, file_content, file.content_type)))
            # 重置文件指针
            await file.seek(0)
        
        # 转发到OSS服务 - 使用files参数传递列表
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OSS_SERVICE_BASE_URL}/upload/multiple",
                files=files_list,
                params=params
            )
            response.raise_for_status()
            return JSONResponse(content=response.json())
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"多文件上传失败: {str(e)}"
        )

@router.post("/text")
async def upload_text(
    text: str, 
    filename: str = "text_file.txt",
    upload_path: str = Query("", description="文件上传路径")
):
    """
    文本内容上传接口 - 转发到OSS服务
    """
    try:
        # 准备查询参数
        params = {}
        if upload_path:
            params["upload_path"] = upload_path
        
        # 转发到OSS服务
        result = await make_oss_request(
            "/upload/text", 
            "POST", 
            data={"text": text, "filename": filename},
            params=params
        )
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文本上传失败: {str(e)}"
        )

@router.get("/service_status")
async def get_oss_service_status():
    """
    获取OSS服务状态信息
    """
    try:
        # 获取健康状态
        health_status = await make_oss_request("/health", "GET")
        
        # 获取根路径状态
        root_status = await make_oss_request("/", "GET")
        
        return {
            "status": "success",
            "oss_service_health": health_status,
            "oss_service_root": root_status,
            "service_base_url": OSS_SERVICE_BASE_URL
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取OSS服务状态失败: {str(e)}"
        )