from fastapi import APIRouter, UploadFile, File, Form
from app.core.file_upload.user_uploader import upload_files
from typing import List

router = APIRouter()

# 1. 文件上传接口: 使用 POST 方法创建新的文件资源
@router.post("/files/", status_code=201)  # 使用201表示资源已创建
async def create_upload_files(
    files: List[UploadFile] = File(...),
    task_option: str = Form(...),
    video_type: str = Form(...),
    username: str = Form(...),
    only_file_upload: bool = Form(...)

):
    """
    上传文件并创建文件资源
    """
    # 上传文件并返回上传成功的结果
    return await upload_files(files, task_option, video_type, username, only_file_upload)


# # 2. 获取文件记录: 使用 GET 方法获取所有文件资源
# @router.get("/files/")
# async def get_files():
#     """
#     获取所有文件记录
#     """
#     return await get_file_records()


# # 如果要根据文件 ID 获取单个文件的详细信息，使用 GET 方法
# @router.get("/files/{file_id}")
# async def get_file(file_id: str):
#     """
#     根据文件 ID 获取文件的详细信息
#     """
#     # 假设 get_file_by_id 是一个获取单个文件信息的函数
#     file_record = await get_file_by_id(file_id)  # 假设的函数
#     if file_record is None:
#         raise HTTPException(status_code=404, detail="File not found")
#     return file_record


# # 如果要删除文件，使用 DELETE 方法
# @router.delete("/files/{file_id}", status_code=204)
# async def delete_file(file_id: str):
#     """
#     根据文件 ID 删除文件资源
#     """
#     result = await delete_file_by_id(file_id)  # 假设的函数
#     if not result:
#         raise HTTPException(status_code=404, detail="File not found")
#     return {"message": "File deleted successfully"}
