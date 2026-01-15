from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    registration_time = db.Column(db.DateTime)
    account_level = db.Column(db.Enum("普通", "VIP"))
    status = db.Column(db.Enum("正常", "冻结", "注销"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    devices = db.relationship("Device", backref="user", lazy="dynamic")
    transactions = db.relationship("FinancialTransaction", backref="user", lazy="dynamic")
    login_logs = db.relationship("LoginLog", backref="user", lazy="dynamic")


class Device(db.Model):
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


class RiskEvent(db.Model):
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

    timelines = db.relationship("EventTimeline", backref="event", lazy="dynamic")
    alerts = db.relationship("Alert", backref="event", lazy="dynamic")
    handling_records = db.relationship("HandlingRecord", backref="event", lazy="dynamic")
    related_users = db.relationship("RelatedUser", backref="event", lazy="dynamic")
    recommendations = db.relationship("RiskAnalysisRecommendation", backref="event", lazy="dynamic")


class Alert(db.Model):
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


class FinancialTransaction(db.Model):
    __tablename__ = "financial_transactions"
    tx_id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    amount = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(10), default="CNY")
    transaction_time = db.Column(db.DateTime)
    status = db.Column(db.Enum("成功", "失败", "处理中"))
    category = db.Column(db.String(50))
    ip_address = db.Column(db.String(39))
    device_id = db.Column(db.String(64), db.ForeignKey("devices.device_id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HandlingRecord(db.Model):
    __tablename__ = "handling_records"
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    operator = db.Column(db.String(50))
    action = db.Column(db.Enum("冻结账户", "发送验证码", "标记已处理", "忽略", "联系用户"))
    action_time = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LoginLog(db.Model):
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


class RelatedUser(db.Model):
    __tablename__ = "related_users"
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"))
    relationship_type = db.Column(db.Enum("关联账户", "同IP注册", "共用设备"))
    risk_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskAnalysisRecommendation(db.Model):
    __tablename__ = "risk_analysis_recommendations"
    rec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(32), db.ForeignKey("risk_events.event_id"))
    risk_assessment = db.Column(db.Text)
    recommendation_text = db.Column(db.Text)
    priority = db.Column(db.Enum("高", "中", "低"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataSource(db.Model):
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


class AuthAccount(db.Model):
    __tablename__ = "auth_accounts"
    auth_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(32), db.ForeignKey("users.user_id"), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)