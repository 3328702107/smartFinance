from datetime import datetime, timedelta
import uuid

from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from extensions import db
from models import User, AuthAccount, LoginLog
from api_utils import api_response

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _issue_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    # PyJWT>=2 返回 str，兼容旧版本 bytes
    return token if isinstance(token, str) else token.decode("utf-8")


@bp.post("/register")
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    phone = data.get("phone")
    email = data.get("email")

    if not username or not password:
        return api_response(code=400, message="username and password required")

    # 唯一用户名
    if User.query.filter_by(username=username).first():
        return api_response(code=409, message="username already exists")

    user_id = uuid.uuid4().hex[:32]
    user = User(
        user_id=user_id,
        username=username,
        phone=phone,
        email=email,
        registration_time=datetime.utcnow(),
        account_level="普通",
        status="正常",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.session.add(user)
    db.session.flush()  # 确保先插入用户，再插入账号，避免外键约束

    acc = AuthAccount(user_id=user_id, password_hash=generate_password_hash(password))
    db.session.add(acc)

    db.session.commit()

    token = _issue_token(user_id)
    return api_response(
        data={
            "user_id": user_id,
            "username": username,
            "token": token,
        },
        message="注册成功",
    )


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

    user = User.query.filter_by(username=username).first()
    if not user:
        return api_response(code=401, message="invalid credentials")

    acc = AuthAccount.query.filter_by(user_id=user.user_id).first()
    if not acc or not check_password_hash(acc.password_hash, password):
        return api_response(code=401, message="invalid credentials")

    if user.status == "冻结":
        return api_response(code=403, message="account is frozen")

    token = _issue_token(user.user_id)

    # 写登录日志（简化）
    log = LoginLog(
        user_id=user.user_id,
        device_id=device_id,
        ip_address=ip,
        login_time=datetime.utcnow(),
        login_status="成功",
        login_location=login_location,
        client_type=client_type,
        session_token=token,
        created_at=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    # 按新文档返回结构包装（基于当前用户动态生成，字段来自 users 表）
    user_info = {
        "id": user.user_id,
        "username": user.username,
        "name": user.username,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        # 优先使用数据库中的 role 字段，否则根据账户等级给个默认值
        "role": user.role or ("user" if user.account_level == "普通" else "vip_user"),
        "department": user.department,
        "employeeId": user.employee_id,
    }

    return api_response(
        data={
            "token": token,
            "refreshToken": token,
            "userInfo": user_info,
            "expiresIn": 12 * 60 * 60,
        },
        message="登录成功",
    )


@bp.get("/me")
def me():
    # 简易 token 读取（演示用），建议前端放在 Authorization: Bearer <token>
    token = request.headers.get("Authorization")
    if token and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    else:
        token = request.args.get("token")

    if not token:
        return api_response(code=401, message="token required")

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
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
    except jwt.ExpiredSignatureError:
        return api_response(code=401, message="token expired")
    except jwt.InvalidTokenError:
        return api_response(code=401, message="invalid token")


@bp.post("/logout")
def logout():
    # 当前未做服务端 token 注销，直接返回成功
    return api_response(message="登出成功")


@bp.post("/refresh")
def refresh_token():
    data = request.get_json() or {}
    _refresh = data.get("refreshToken")
    if not _refresh:
        return api_response(code=400, message="refreshToken required")

    # 简化处理：不校验旧 token，直接签发新 token
    # 真实环境应解析 refreshToken 获取用户信息
    try:
        payload = jwt.decode(_refresh, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload.get("sub")
    except Exception:
        return api_response(code=401, message="invalid refreshToken")

    token = _issue_token(user_id)
    return api_response(data={"token": token, "expiresIn": 12 * 60 * 60}, message="刷新成功")


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
    except Exception:
        return api_response(code=401, message="invalid token")

    user = User.query.get(payload.get("sub"))
    if not user:
        return api_response(code=404, message="user not found")

    acc = AuthAccount.query.filter_by(user_id=user.user_id).first()
    if not acc or not check_password_hash(acc.password_hash, old_pwd):
        return api_response(code=400, message="old password incorrect")

    acc.password_hash = generate_password_hash(new_pwd)
    db.session.commit()
    return api_response(message="密码修改成功")
