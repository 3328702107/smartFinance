# 分析相关模型
from datetime import datetime

from core.database import db


class HandlingRecord(db.Model):
    """处理记录模型"""
    __tablename__ = "handling_records"

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    operator = db.Column(db.String(50))
    action = db.Column(db.Enum("冻结账户", "发送验证码", "标记已处理", "忽略", "联系用户"))
    action_time = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RelatedUser(db.Model):
    """关联用户模型"""
    __tablename__ = "related_users"

    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    relationship_type = db.Column(db.Enum("关联账户", "同IP注册", "共用设备"))
    risk_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskAnalysisRecommendation(db.Model):
    """风险分析建议模型"""
    __tablename__ = "risk_analysis_recommendations"

    rec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    risk_assessment = db.Column(db.Text)
    recommendation_text = db.Column(db.Text)
    priority = db.Column(db.Enum("高", "中", "低"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventResponsibility(db.Model):
    """事件责任追溯信息（节点/边/分析结构以 JSON 存储）"""
    __tablename__ = "event_responsibility"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    nodes = db.Column(db.JSON)
    edges = db.Column(db.JSON)
    analysis = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
