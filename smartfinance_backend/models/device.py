# 设备模型
from datetime import datetime

from core.database import db


class Device(db.Model):
    """设备模型"""
    __tablename__ = "devices"

    device_id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    device_name = db.Column(db.String(100))
    os_type = db.Column(db.String(50))
    ip_address = db.Column(db.String(39))
    location = db.Column(db.String(100))
    is_normal = db.Column(db.Boolean, default=True)
    last_login_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
