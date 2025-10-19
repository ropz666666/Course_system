import uuid
from fastapi import APIRouter, File, UploadFile, Request
import os  # 新增导入os模块用于文件删除

from app.service.file_service import cos_upload_file
from common.exception.errors import RequestError
from pathlib import Path

from common.security.jwt import DependsJwtAuth
from core.path_conf import FILES_DIR

# 创建一个路由器
router = APIRouter()


@router.post("/upload", dependencies=[DependsJwtAuth])
async def upload_file(request: Request, file: UploadFile = File(...)):
    # 将 FILES_DIR 转换为 Path 对象
    upload_folder = Path(FILES_DIR)

    # 生成一个 UUID 用作新文件夹的名称
    unique_id = str(uuid.uuid4())
    folder_path = upload_folder / request.user.uuid / unique_id

    # 创建新的文件夹
    folder_path.mkdir(parents=True, exist_ok=True)

    # 保存文件到指定的 UUID 文件夹中
    file_location = folder_path / file.filename

    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # 上传到COS
        file_url = await cos_upload_file(file_location, file.filename)

        # 上传成功后删除本地文件
        if os.path.exists(file_location):
            os.remove(file_location)
            # 如果文件夹为空，也删除文件夹
            try:
                folder_path.rmdir()
            except OSError:
                pass

        return {"url": file_url}

    except Exception as e:
        # 如果发生错误，确保删除可能已创建的文件
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
        return RequestError(msg="文件上传失败", detail={"error": str(e)})