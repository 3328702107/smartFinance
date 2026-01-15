from datetime import datetime, timedelta
import uuid

from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from extensions import db
from models import User, AuthAccount, LoginLog

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
        return jsonify({"message": "username and password required"}), 400

    # 唯一用户名
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "username already exists"}), 409

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
    return jsonify({"user_id": user_id, "username": username, "token": token})


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
        return jsonify({"message": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "invalid credentials"}), 401

    acc = AuthAccount.query.filter_by(user_id=user.user_id).first()
    if not acc or not check_password_hash(acc.password_hash, password):
        return jsonify({"message": "invalid credentials"}), 401

    if user.status == "冻结":
        return jsonify({"message": "account is frozen"}), 403

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

    return jsonify({"user_id": user.user_id, "username": user.username, "token": token})


@bp.get("/me")
def me():
    # 简易 token 读取（演示用），建议前端放在 Authorization: Bearer <token>
    token = request.headers.get("Authorization")
    if token and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    else:
        token = request.args.get("token")

    if not token:
        return jsonify({"message": "token required"}), 401

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"message": "user not found"}), 404
        return jsonify({
            "user_id": user.user_id,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "status": user.status,
            "account_level": user.account_level,
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "invalid token"}), 401
