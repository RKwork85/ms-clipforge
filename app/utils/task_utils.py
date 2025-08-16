import httpx
import asyncio
from typing import Dict, Any


class AsyncRedisAPIService:
    def __init__(self, base_url: str = "http://127.0.0.1:8889"):
        """
        初始化调用客户端
        :param base_url: app_v2 服务地址
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def submit_task(
        self, task_id: str, task_type: str, data: Dict[str, Any],
        video_type: str = "default", priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        提交任务
        """
        url = f"{self.base_url}/tasks"
        payload = {
            "task_id": task_id,
            "task_type": task_type,
            "video_type": video_type,
            "data": data,
            "priority": priority
        }
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def get_task_status(self, job_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        """
        url = f"{self.base_url}/tasks/{job_id}"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def list_tasks(self) -> Dict[str, Any]:
        """
        获取所有任务列表
        """
        url = f"{self.base_url}/tasks"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def get_queue_info(self) -> Dict[str, Any]:
        """
        获取队列信息
        """
        url = f"{self.base_url}/queue/info"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def cancel_task(self, job_id: str) -> Dict[str, Any]:
        """
        取消任务
        """
        url = f"{self.base_url}/tasks/{job_id}"
        resp = await self._client.delete(url)
        resp.raise_for_status()
        return resp.json()

    async def clear_queue(self) -> Dict[str, Any]:
        """
        清空队列
        """
        url = f"{self.base_url}/queue/clear"
        resp = await self._client.post(url)
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        """
        url = f"{self.base_url}/health"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        """
        关闭 httpx 客户端
        """
        await self._client.aclose()


# 示例用法
async def main():
    service = AsyncRedisAPIService("http://127.0.0.1:8889")

    try:
        # 提交任务
        task = await service.submit_task(
            task_id="task123",
            task_type="split_mixer",
            data={"input_folder": "./input", "output_folder": "./output"}
        )
        print("提交任务:", task)

        # 获取状态
        job_id = task.get("job_id")
        if job_id:
            status = await service.get_task_status(job_id)
            print("任务状态:", status)

        # 队列信息
        print("队列信息:", await service.get_queue_info())

    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
