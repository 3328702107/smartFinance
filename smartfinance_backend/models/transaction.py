# 交易模型
from datetime import datetime

from core.database import db


class FinancialTransaction(db.Model):
    """金融交易模型"""
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
