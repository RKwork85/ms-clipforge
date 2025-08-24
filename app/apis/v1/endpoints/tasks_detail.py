from fastapi import APIRouter, Depends, HTTPException
from app.services.redis_api_service import redisAPIService
from typing import Dict, Any

router = APIRouter()

@router.get("/tasks/{job_id}", response_model=Dict[str, Any])
async def get_task_status(job_id: str):
    """
    查询指定任务的状态
    :param job_id: 任务ID
    :return: 任务状态信息
    """
    try:
        task_status = await redisAPIService.get_task_status(job_id)
        return task_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=Dict[str, Any])
async def list_tasks():
    """
    查询所有任务的列表
    :return: 任务列表
    """
    try:
        tasks = await redisAPIService.list_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/info", response_model=Dict[str, Any])
async def get_queue_info():
    """
    查询队列信息
    :return: 队列信息
    """
    try:
        queue_info = await redisAPIService.get_queue_info()
        return queue_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{job_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(job_id: str):
    """
    取消指定的任务
    :param job_id: 任务ID
    :return: 取消的任务信息
    """
    try:
        result = await redisAPIService.cancel_task(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/clear", response_model=Dict[str, Any])
async def clear_queue():
    """
    清空任务队列
    :return: 清空后的队列状态
    """
    try:
        result = await redisAPIService.clear_queue()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    检查服务健康状态
    :return: 健康检查结果
    """
    try:
        health = await redisAPIService.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
