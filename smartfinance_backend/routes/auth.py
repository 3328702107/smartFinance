# 认证路由（使用服务层）
from datetime import datetime, timedelta
import uuid

from flask import Blueprint, request, current_app
import jwt

from core.database import db
from models.user import User, AuthAccount
from models.data import LoginLog
from services.auth_service import AuthService
from utils.response import api_response

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _issue_token(user_id: str) -> str:
    """生成 token（兼容旧代码）"""
    return AuthService.generate_token(user_id)


@bp.post("/register")
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    phone = data.get("phone")
    email = data.get("email")

    if not username or not password:
        return api_response(code=400, message="username and password required")

    try:
        user, token = AuthService.register_user(username, password, phone, email)
        return api_response(
            data={
                "user_id": user.user_id,
                "username": username,
                "token": token,
            },
            message="注册成功",
        )
    except Exception as e:
        return api_response(code=409, message=str(e))


@bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    device_id = data.get("device_id")
    ip = data.get("ip_address")
    client_type = data.get("client_type", "WEB")
    login_location = data.get("login_location")

    if not username or not password:
        return api_response(code=400, message="username and password required")

    try:
        user = AuthService.authenticate_user(username, password)
        token = AuthService.create_login_log(user, device_id, ip, client_type, login_location)

        user_info = {
            "id": user.user_id,
            "username": user.username,
            "name": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "role": user.role or ("user" if user.account_level == "普通" else "vip_user"),
            "department": user.department,
            "employeeId": user.employee_id,
        }

        return api_response(
            data={
                "token": token,
                "refreshToken": token,
                "userInfo": user_info,
                "expiresIn": 43200,
            },
            message="登录成功",
        )
    except Exception as e:
        if "frozen" in str(e):
            return api_response(code=403, message=str(e))
        if "invalid" in str(e) or "not found" in str(e):
            return api_response(code=401, message=str(e))
        return api_response(code=400, message=str(e))


@bp.get("/me")
def me():
    token = request.headers.get("Authorization")
    if token and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    else:
        token = request.args.get("token")

    if not token:
        return api_response(code=401, message="token required")

    try:
        payload = AuthService.verify_token(token)
        user = User.query.get(payload.get("sub"))
        if not user:
            return api_response(code=404, message="user not found")
        return api_response(
            data={
                "user_id": user.user_id,
                "username": user.username,
                "phone": user.phone,
                "email": user.email,
                "status": user.status,
                "account_level": user.account_level,
            }
        )
    except Exception as e:
        return api_response(code=401, message=str(e))


@bp.post("/logout")
def logout():
    return api_response(message="登出成功")


@bp.post("/refresh")
def refresh_token():
    data = request.get_json() or {}
    _refresh = data.get("refreshToken")
    if not _refresh:
        return api_response(code=400, message="refreshToken required")

    try:
        payload = jwt.decode(_refresh, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload.get("sub")
        token = _issue_token(user_id)
        return api_response(data={"token": token, "expiresIn": 43200}, message="刷新成功")
    except Exception:
        return api_response(code=401, message="invalid refreshToken")


@bp.post("/change-password")
def change_password():
    data = request.get_json() or {}
    old_pwd = data.get("oldPassword")
    new_pwd = data.get("newPassword")
    if not old_pwd or not new_pwd:
        return api_response(code=400, message="oldPassword and newPassword required")

    token = request.headers.get("Authorization", "")
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        AuthService.change_password(payload.get("sub"), old_pwd, new_pwd)
        return api_response(message="密码修改成功")
    except Exception as e:
        return api_response(code=400, message=str(e))
