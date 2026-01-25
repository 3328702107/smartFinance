# 通用接口
import os
import uuid
from datetime import datetime

from flask import Blueprint, request, current_app, send_from_directory
from werkzeug.utils import secure_filename

from utils.response import api_response

bp = Blueprint("common", __name__, url_prefix="/api/common")

# 允许的文件类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'}


def allowed_file(filename: str, file_type: str = "image") -> bool:
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == "image":
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == "document":
        return ext in ALLOWED_DOC_EXTENSIONS
    else:
        return ext in (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOC_EXTENSIONS)


def get_upload_folder() -> str:
    """获取上传目录，不存在则创建"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(current_app.root_path, upload_folder)
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


@bp.post("/upload")
def upload_file():
    """
    文件上传接口
    请求参数:
      - file: 文件 (multipart/form-data)
      - type: 文件类型 (image/document/other)
    """
    if 'file' not in request.files:
        return api_response(code=400, message="未找到上传文件")

    file = request.files['file']
    if file.filename == '':
        return api_response(code=400, message="文件名为空")

    file_type = request.form.get('type', 'image')

    if not allowed_file(file.filename, file_type):
        return api_response(code=400, message="不支持的文件类型")

    # 生成安全文件名
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

    upload_folder = get_upload_folder()
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 构造访问 URL
    base_url = request.host_url.rstrip('/')
    file_url = f"{base_url}/api/common/files/{unique_name}"

    return api_response(
        message="上传成功",
        data={
            "url": file_url,
            "filename": unique_name,
            "originalName": original_name,
            "size": file_size
        }
    )


@bp.get("/files/<filename>")
def serve_file(filename):
    """提供已上传文件的访问"""
    upload_folder = get_upload_folder()
    return send_from_directory(upload_folder, filename)


@bp.get("/config")
def get_config():
    """
    获取系统配置
    """
    return api_response(
        data={
            "systemName": "风控管理系统",
            "version": "1.0.0",
            "maxUploadSize": 10 * 1024 * 1024,  # 10MB
            "supportedImageFormats": list(ALLOWED_IMAGE_EXTENSIONS),
            "supportedDocFormats": list(ALLOWED_DOC_EXTENSIONS),
            "refreshIntervals": [5, 10, 30, 60]
        }
    )
