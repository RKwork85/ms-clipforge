import datetime
from fastapi import HTTPException, UploadFile
from app.models.file_record import FileRecord
from app.utils.logger import get_logger, log_execution_time
from app.config import UPLOAD_DIR, ALLOWED_USERS, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS
from app.services.redis_api_service import redisAPIService
from pathlib import Path
from typing import List
import uuid 

# 获取专用的日志记录器
logger = get_logger(__name__)

# 确保上传目录存在
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
@log_execution_time
async def upload_files(files: List[UploadFile], task_option: str, video_type: str, username: str, only_file_upload: bool):
    """
    处理文件上传的核心逻辑
    
    Args:
        files: 上传的文件列表
        class_name: 任务分类/名称
        upload_type: 任务类型
        username: 用户名
    
    Returns:
        dict: 包含上传结果的字典
    
    Raises:
        HTTPException: 当验证失败或上传出错时抛出
    """
    
    # 生成16位唯一task_id
    task_id = str(uuid.uuid4()).replace("-", "")[:16]
    
    logger.info(f"开始处理文件上传 | 用户: {username} | 分类: {task_option} | 类型: {video_type} | 文件数: {len(files)} | 任务ID: {task_id}")
    
    # 用户权限验证
    if username not in ALLOWED_USERS:
        logger.warning(f"用户权限验证失败 | 用户: {username} | 允许的用户: {ALLOWED_USERS}")
        raise HTTPException(status_code=403, detail="Access denied. Invalid credentials.")
    
    # 文件数量验证
    if not files:
        logger.error("没有接收到任何文件")
        raise HTTPException(status_code=422, detail="No files provided")
    
    if len(files) > 50:  # 限制单次最多上传50个文件
        logger.error(f"文件数量超限 | 当前: {len(files)} | 最大: 50")
        raise HTTPException(status_code=422, detail="Too many files. Maximum 50 files per request")

    saved_files = []
    failed_files = []
    current_time = datetime.datetime.now().isoformat()
    total_size = 0

    # 构造存储路径: UPLOAD_DIR/username/task_option/video_type/task_id/

    if only_file_upload:
        user_task_path  = UPLOAD_DIR / username / task_id  /  "_".join([username,"task", task_id])
    else:
        user_task_path = UPLOAD_DIR / username / task_option / video_type / "_".join([username,"task", task_id])

    user_task_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在

    for i, file in enumerate(files, 1):
        logger.info(f"处理文件 {i}/{len(files)}: {file.filename}")
        
        # 文件名验证
        if not file.filename or file.filename.strip() == "":
            error_msg = f"文件 #{i} 文件名为空"
            logger.error(error_msg)
            failed_files.append({"filename": f"file_{i}", "error": "Empty filename"})
            continue
        
        # 文件扩展名验证
        if ALLOWED_FILE_EXTENSIONS:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_FILE_EXTENSIONS:
                error_msg = f"文件类型不支持 | 文件: {file.filename} | 扩展名: {file_ext} | 支持的类型: {ALLOWED_FILE_EXTENSIONS}"
                logger.warning(error_msg)
                failed_files.append({"filename": file.filename, "error": f"Unsupported file type: {file_ext}"})
                continue

        try:
            # 读取文件内容
            contents = await file.read()
            file_size = len(contents)
            
            # 文件大小验证
            if file_size > MAX_FILE_SIZE:
                error_msg = f"文件过大 | 文件: {file.filename} | 大小: {file_size / 1024 / 1024:.2f}MB | 最大: {MAX_FILE_SIZE / 1024 / 1024:.2f}MB"
                logger.warning(error_msg)
                failed_files.append({"filename": file.filename, "error": f"File too large: {file_size / 1024 / 1024:.2f}MB"})
                continue
            
            # 检查文件是否已存在，如果存在则重命名
            save_path = user_task_path / file.filename
            original_filename = file.filename
            counter = 1
            
            while save_path.exists():
                name_part = Path(original_filename).stem
                ext_part = Path(original_filename).suffix
                new_filename = f"{name_part}_{counter}{ext_part}"
                save_path = user_task_path / new_filename
                counter += 1
                
                if counter > 100:  # 防止无限循环
                    raise Exception("Too many duplicate files")
            
            # 保存文件
            with open(save_path, "wb") as f:
                f.write(contents)
            
            # 验证文件是否成功写入
            if not save_path.exists() or save_path.stat().st_size != file_size:
                raise Exception("File write verification failed")
            
            total_size += file_size
            
            # 记录文件信息
            # file_record = FileRecord(
            #     filename=save_path.name,  # 使用实际保存的文件名 
            #     original_filename=original_filename,
            #     path=str(save_path),
            #     upload_time=current_time,
            #     class_name=task_option,
            #     upload_type=video_type,
            #     username=username,
            #     size=round(file_size / 1024 / 1024, 2)
            # )
            
            saved_files.append({
                "filename": original_filename,
                "saved_as": save_path.name,
                "size_mb": round(file_size / 1024 / 1024, 2)
            })

            logger.info(f"文件保存成功 | 原名: {original_filename} | 保存为: {save_path.name} | 大小: {file_size / 1024 / 1024:.2f}MB")

        except Exception as e:
            error_msg = f"文件保存失败 | 文件: {file.filename} | 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            failed_files.append({"filename": file.filename, "error": str(e)})

    # 生成结果报告
    success_count = len(saved_files)
    failed_count = len(failed_files)
    
    logger.info(
        f"文件上传完成 | 成功: {success_count} | 失败: {failed_count} | "
        f"总大小: {total_size / 1024 / 1024:.2f}MB | 用户: {username} | 任务ID: {task_id}"
    )
  
    print(task_option)
    # 提交异步任务
    task_result = None
    if only_file_upload:
        print("可以执行后续操作，oss服务器文件上传操作了! 上传的路径为：", user_task_path)
        result = {
            "task_id": task_id,  # 返回任务ID
            "status": "success" if failed_count == 0 else "partial_success" if success_count > 0 else "failed",
            "summary": {
                "total_files": len(files),
                "successful": success_count,
                "failed": failed_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            },
            "saved_files": saved_files,
            "failed_files": failed_files,
            "timestamp": current_time
        }
        return result

    else:
        try:
            task_result = await redisAPIService.submit_task(
                task_id=task_id,
                task_type=task_option,
                video_type="Baby素材处理混剪",
                # data={"input_folder": str(user_task_path), "output_folder": str(Path(user_task_result_path))}
                data={"input_folder": str(user_task_path), "output_folder": f".//{username}//{task_option}//{username}_{task_option}_{task_id}"}

            )
            logger.info(f"任务已提交到队列 | 任务ID: {task_id} | 队列返回: {task_result}")
        except Exception as e:
            logger.error(f"任务提交失败 | 任务ID: {task_id} | 错误: {str(e)}")
            task_result = {"error": str(e)}


        result = {
            "task_id": task_id,  # 返回任务ID
            "status": "success" if failed_count == 0 else "partial_success" if success_count > 0 else "failed",
            "summary": {
                "total_files": len(files),
                "successful": success_count,
                "failed": failed_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            },
            "saved_files": saved_files,
            "failed_files": failed_files,
            "timestamp": current_time
        }

        
        if failed_count > 0:
            logger.warning(f"部分文件上传失败 | 失败文件: {[f['filename'] for f in failed_files]}")

        return result