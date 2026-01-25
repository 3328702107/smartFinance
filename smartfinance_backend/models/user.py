# 用户相关模型
from datetime import datetime

from core.database import db


class User(db.Model):
    """���户模型"""
    __tablename__ = "users"

    user_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))  # 姓名
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    gender = db.Column(db.Enum("男", "女", "未知"))  # 性别
    birthday = db.Column(db.Date)  # 生日
    bio = db.Column(db.Text)  # 简介
    avatar = db.Column(db.String(255))
    department = db.Column(db.String(100))
    role = db.Column(db.String(50))
    employee_id = db.Column(db.String(50))
    registration_time = db.Column(db.DateTime)
    account_level = db.Column(db.Enum("普通", "VIP"))
    status = db.Column(db.Enum("正常", "冻结", "注销"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    devices = db.relationship("Device", backref="user", lazy="dynamic")
    transactions = db.relationship("FinancialTransaction", backref="user", lazy="dynamic")
    login_logs = db.relationship("LoginLog", backref="user", lazy="dynamic")


class AuthAccount(db.Model):
    """认证账户模型"""
    __tablename__ = "auth_accounts"

    auth_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
