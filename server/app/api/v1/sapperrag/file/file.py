import uuid
from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
from pathlib import Path

from common.response.response_schema import response_base
from common.security.jwt import DependsJwtAuth
from core.path_conf import FILES_DIR  # 假设 FILES_DIR 是字符串类型

# 创建一个路由器
router = APIRouter()


@router.post("/upload", dependencies=[DependsJwtAuth])
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # 将 FILES_DIR 转换为 Path 对象
        upload_folder = Path(FILES_DIR)

        # 生成一个 UUID 用作新文件夹的名称
        unique_id = str(uuid.uuid4())
        folder_path = upload_folder / request.user.uuid / unique_id

        # 创建新的文件夹
        folder_path.mkdir(parents=True, exist_ok=True)

        # 保存文件到指定的 UUID 文件夹中
        file_location = folder_path / file.filename
        with open(file_location, "wb") as f:
            f.write(await file.read())

        file_url = f"files/{request.user.uuid}/{unique_id}/{file.filename}"
        print(file_url)
        return response_base.success(data={"url": file_url})

    except Exception as e:
        return response_base.fail(data={"message": "文件上传失败", "error": str(e)})
