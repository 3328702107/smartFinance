# 认证服务
import uuid
from datetime import datetime, timedelta

from flask import current_app
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from core.database import db
from models.user import User, AuthAccount
from models.device import Device
from models.data import LoginLog
from core.exceptions import ValidationError, NotFoundError


class AuthService:
    """认证服务类"""

    @staticmethod
    def generate_token(user_id: str) -> str:
        """生成 JWT token"""
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=12),
        }
        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return token if isinstance(token, str) else token.decode("utf-8")

    @staticmethod
    def verify_token(token: str):
        """验证 JWT token"""
        try:
            return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValidationError("token expired")
        except jwt.InvalidTokenError:
            raise ValidationError("invalid token")

    @staticmethod
    def register_user(username: str, password: str, phone=None, email=None):
        """注册用户"""
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            raise ValidationError("username already exists")

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
        db.session.flush()

        acc = AuthAccount(user_id=user_id, password_hash=generate_password_hash(password))
        db.session.add(acc)
        db.session.commit()

        return user, AuthService.generate_token(user_id)

    @staticmethod
    def authenticate_user(username: str, password: str):
        """验证用户登录"""
        user = User.query.filter_by(username=username).first()
        if not user:
            raise NotFoundError("user not found")

        acc = AuthAccount.query.filter_by(user_id=user.user_id).first()
        if not acc or not check_password_hash(acc.password_hash, password):
            raise ValidationError("invalid credentials")

        if user.status == "冻结":
            raise ValidationError("account is frozen")

        return user

    @staticmethod
    def create_login_log(user, device_id=None, ip=None, client_type="WEB", location=None):
        """创建登录日志"""
        token = AuthService.generate_token(user.user_id)

        # 兼容新设备：如果传入的 device_id 在 devices 表中不存在，则自动创建一条设备记录；
        # 如果存在则更新其最近登录信息。这样可以避免 login_logs 的外键约束报错。
        now = datetime.utcnow()
        real_device_id = None

        if device_id:
            device = Device.query.get(device_id)
            if not device:
                device = Device(
                    device_id=device_id,
                    user_id=user.user_id,
                    ip_address=ip,
                    location=location,
                    last_login_time=now,
                    is_normal=True,
                )
                db.session.add(device)
                # 先将新设备写入数据库，避免后续 login_logs 插入时外键约束失败
                db.session.flush()
            else:
                device.user_id = user.user_id
                if ip:
                    device.ip_address = ip
                if location:
                    device.location = location
                device.last_login_time = now

            real_device_id = device.device_id

        log = LoginLog(
            user_id=user.user_id,
            device_id=real_device_id,
            ip_address=ip,
            login_time=now,
            login_status="成功",
            login_location=location,
            client_type=client_type,
            session_token=token,
            created_at=now,
        )
        db.session.add(log)
        db.session.commit()
        return token

    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str):
        """修改密码"""
        acc = AuthAccount.query.filter_by(user_id=user_id).first()
        if not acc or not check_password_hash(acc.password_hash, old_password):
            raise ValidationError("old password incorrect")

        acc.password_hash = generate_password_hash(new_password)
        db.session.commit()
