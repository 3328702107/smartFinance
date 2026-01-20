# 风险相关模型
from datetime import datetime

from core.database import db


class RiskEvent(db.Model):
    """风险事件模型"""
    __tablename__ = "risk_events"

    event_id = db.Column(db.String(32), primary_key=True)
    event_type = db.Column(db.Enum("账户盗用", "异常交易", "证件伪造", "批量注册", "设备异常"), nullable=False)
    risk_level = db.Column(db.Enum("高", "中", "低"), nullable=False)
    score = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    detection_time = db.Column(db.DateTime)
    status = db.Column(db.Enum("待处理", "处理中", "已解决", "已忽略"), default="待处理")
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    device_id = db.Column(db.String(64), db.ForeignKey("devices.device_id"))
    ip_address = db.Column(db.String(39))
    trigger_rule = db.Column(db.String(100))
    severity_scope = db.Column(db.Enum("个人", "机构", "平台"), default="个人")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    timelines = db.relationship("EventTimeline", backref="event", lazy="dynamic")
    alerts = db.relationship("Alert", backref="event", lazy="dynamic")
    handling_records = db.relationship("HandlingRecord", backref="event", lazy="dynamic")
    related_users = db.relationship("RelatedUser", backref="event", lazy="dynamic")
    recommendations = db.relationship("RiskAnalysisRecommendation", backref="event", lazy="dynamic")


class Alert(db.Model):
    """告警模型"""
    __tablename__ = "alerts"

    alert_id = db.Column(db.String(32), primary_key=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    alert_type = db.Column(db.String(50))
    alert_level = db.Column(db.Enum("高", "中", "低"))
    triggered_at = db.Column(db.DateTime)
    status = db.Column(db.Enum("待处理", "处理中", "已解决", "已忽略"), default="待处理")
    handler = db.Column(db.String(50))
    operation_log = db.Column(db.Text)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventTimeline(db.Model):
    """事件时间线模型"""
    __tablename__ = "event_timeline"

    timeline_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    step_no = db.Column(db.Integer)
    step_title = db.Column(db.String(100))
    step_description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    type = db.Column(db.Enum("登录", "验证", "交易", "异常", "处理"))
    related_entity = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
