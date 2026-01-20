# 数据源相关模型
from datetime import datetime

from core.database import db


class DataSource(db.Model):
    """数据源模型"""
    __tablename__ = "data_sources"

    source_id = db.Column(db.String(32), primary_key=True)
    source_name = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.Enum("数据库", "API", "文件", "消息队列"))
    connection_url = db.Column(db.String(255))
    status = db.Column(db.Enum("正常", "异常", "中断"))
    last_sync_time = db.Column(db.DateTime)
    sync_progress = db.Column(db.Numeric(5, 2))
    error_count = db.Column(db.Integer, default=0)
    last_error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataQualityIssue(db.Model):
    """数据质量问题模型"""
    __tablename__ = "data_quality_issues"

    issue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_id = db.Column(db.String(32), db.ForeignKey("data_sources.source_id"))
    issue_type = db.Column(db.Enum("缺失字段", "格式错误", "值异常", "数据不一致"))
    description = db.Column(db.Text)
    affected_records_count = db.Column(db.Integer)
    example_record = db.Column(db.JSON)
    severity = db.Column(db.Enum("高", "中", "低"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(50))
    status = db.Column(db.Enum("未处理", "处理中", "已解决"))


class LoginLog(db.Model):
    """登录日志模型"""
    __tablename__ = "login_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    device_id = db.Column(db.String(64), db.ForeignKey("devices.device_id"))
    ip_address = db.Column(db.String(39))
    login_time = db.Column(db.DateTime)
    login_status = db.Column(db.Enum("成功", "失败"))
    login_location = db.Column(db.String(100))
    client_type = db.Column(db.String(50))
    session_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
