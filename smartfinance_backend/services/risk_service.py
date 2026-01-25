# 风险评估服务
from datetime import datetime, timedelta

from core.database import db
from models.risk import RiskEvent
from models.transaction import FinancialTransaction
from models.device import Device
from core.exceptions import ValidationError


class RiskService:
    """风险评估服务类"""

    # 风险规则配置
    RULES = {
        "large_amount_threshold": 10000,  # 大额交易阈值
        "large_amount_score": 50,
        "frequent_transaction_minutes": 10,  # 短时间内交易分钟数
        "frequent_transaction_count": 5,  # 短时间内交易笔数
        "frequent_transaction_score": 30,
        "abnormal_device_score": 20,
    }

    @classmethod
    def assess_transaction_risk(cls, user_id: str, amount: float, device_id=None, ip=None):
        """
        评估交易风险

        返回: (score: int, risk_level: str, reasons: list[str])
        """
        score = 0
        reasons = []

        # 规则1：金额阈值
        if amount >= cls.RULES["large_amount_threshold"]:
            score += cls.RULES["large_amount_score"]
            reasons.append("大额交易")

        # 规则2：短时间内多笔交易
        now = datetime.utcnow()
        last_period = now - timedelta(minutes=cls.RULES["frequent_transaction_minutes"])
        recent_count = FinancialTransaction.query.filter(
            FinancialTransaction.user_id == user_id,
            FinancialTransaction.transaction_time >= last_period
        ).count()
        if recent_count >= cls.RULES["frequent_transaction_count"]:
            score += cls.RULES["frequent_transaction_score"]
            reasons.append("短时间内多笔交易")

        # 规则3：设备是否异常
        if device_id:
            device = Device.query.get(device_id)
            if device and not device.is_normal:
                score += cls.RULES["abnormal_device_score"]
                reasons.append("异常设备")

        # 风险等级判定
        if score >= 80:
            risk_level = "高"
        elif score >= 40:
            risk_level = "中"
        else:
            risk_level = "低"

        return score, risk_level, reasons

    @staticmethod
    def create_risk_event(user_id, device_id, ip_address, risk_level, score, description, event_type="异常交易"):
        """创建风险事件"""
        import uuid
        now = datetime.utcnow()
        event_id = uuid.uuid4().hex[:32]

        event = RiskEvent(
            event_id=event_id,
            event_type=event_type,
            risk_level=risk_level,
            score=score,
            description=description,
            detection_time=now,
            status="待处理" if score > 0 else "已忽略",
            user_id=user_id,
            device_id=device_id,
            ip_address=ip_address,
            trigger_rule="规则引擎",
        )
        db.session.add(event)
        db.session.commit()

        return event_id

    @staticmethod
    def handle_risk_event(event_id: str, action: str, note: str = None):
        """处理风险事件"""
        from models.analysis import HandlingRecord

        event = RiskEvent.query.get(event_id)
        if not event:
            raise ValidationError("event not found")

        # 根据 action 更新状态
        action_status_map = {
            "freeze": ("已解决", "冻结账户"),
            "send_verification": ("处理中", "发送验证码"),
            "mark_resolved": ("已解决", "标记已处理"),
            "ignore": ("已忽略", "忽略"),
        }

        if action in action_status_map:
            new_status, action_name = action_status_map[action]
            event.status = new_status
        else:
            action_name = action or "处理"

        # 添加处理记录
        record = HandlingRecord(
            event_id=event_id,
            operator="系统",
            action=action_name,
            action_time=datetime.utcnow(),
            comment=note,
        )
        db.session.add(record)
        db.session.commit()

