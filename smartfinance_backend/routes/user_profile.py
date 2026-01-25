# 用户个人信息路由
import os
from datetime import datetime

from flask import Blueprint, request
import jwt

from core.database import db
from models.user import User
from utils.response import api_response

bp = Blueprint("user_profile", __name__, url_prefix="/api/user")


def _get_current_user():
    """从 token 获取当前用户"""
    from flask import current_app

    token = request.headers.get("Authorization", "")
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    if not token:
        return None

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return User.query.get(payload.get("sub"))
    except Exception:
        return None


@bp.get("/profile")
def get_profile():
    """获取当前用户信息"""
    user = _get_current_user()
    if not user:
        return api_response(code=401, message="unauthorized")

    def _format_date(d):
        return d.strftime("%Y-%m-%d") if d else None

    return api_response(data={
        "id": user.user_id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "gender": user.gender,
        "birthday": _format_date(user.birthday),
        "bio": user.bio,
        "role": user.role,
        "department": user.department,
        "employeeId": user.employee_id,
        "joinDate": _format_date(user.registration_time),
    })


@bp.put("/profile")
def update_profile():
    """更新用户信息"""
    user = _get_current_user()
    if not user:
        return api_response(code=401, message="unauthorized")

    data = request.get_json() or {}

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        user.email = data["email"]
    if "phone" in data:
        user.phone = data["phone"]
    if "gender" in data:
        user.gender = data["gender"]
    if "birthday" in data:
        try:
            user.birthday = datetime.strptime(data["birthday"], "%Y-%m-%d").date() if data["birthday"] else None
        except ValueError:
            pass
    if "bio" in data:
        user.bio = data["bio"]

    db.session.commit()

    return api_response(message="更新成功", data={
        "id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "birthday": user.birthday.strftime("%Y-%m-%d") if user.birthday else None,
        "bio": user.bio,
    })


@bp.post("/avatar")
def upload_avatar():
    """上传头像"""
    user = _get_current_user()
    if not user:
        return api_response(code=401, message="unauthorized")

    if "file" not in request.files:
        return api_response(code=400, message="file required")

    file = request.files["file"]
    if file.filename == "":
        return api_response(code=400, message="no file selected")

    # 简单保存到静态目录（实际生产应使用云存储）
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "static", "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"{user.user_id}{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # 更新用户头像URL
    avatar_url = f"/static/avatars/{filename}"
    user.avatar = avatar_url
    db.session.commit()

    return api_response(message="上传成功", data={"avatar": avatar_url})
