import uuid
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from extensions import db
from models import FinancialTransaction, RiskEvent, EventTimeline, Alert, User, Device

bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")

@bp.post("/")
def ingest_transaction():
    """
    前端提交一笔交易：
    {
      "tx_id": "可选，不传则后端生成",
      "user_id": "...",
      "device_id": "...",
      "amount": 1200.5,
      "currency": "CNY",
      "category": "转账",
      "ip_address": "1.2.3.4",
      "status": "成功"
    }
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    amount = data.get("amount")
    device_id = data.get("device_id")
    ip = data.get("ip_address")

    if not user_id or amount is None:
        return jsonify({"message": "user_id and amount required"}), 400

    tx_id = data.get("tx_id") or uuid.uuid4().hex[:32]
    now = datetime.utcnow()

    tx = FinancialTransaction(
        tx_id=tx_id,
        user_id=user_id,
        device_id=device_id,
        amount=amount,
        currency=data.get("currency", "CNY"),
        transaction_time=now,
        status=data.get("status", "成功"),
        category=data.get("category"),
        ip_address=ip
    )
    db.session.add(tx)

    # 简单规则打分：只是示例，可根据前端界面需要调整
    score = 0
    reasons = []

    # 规则1：金额阈值
    if amount >= 10000:
        score += 50
        reasons.append("大额交易")

    # 规则2：短时间内多笔交易
    last_10min = now - timedelta(minutes=10)
    recent_count = FinancialTransaction.query.filter(
        FinancialTransaction.user_id == user_id,
        FinancialTransaction.transaction_time >= last_10min
    ).count()
    if recent_count >= 5:
        score += 30
        reasons.append("短时间内多笔交易")

    # 规则3：设备是否异常
    if device_id:
        device = Device.query.get(device_id)
        if device and not device.is_normal:
            score += 20
            reasons.append("异常设备")

    # 规则4：IP 异地（这里只示意，真实场景需要地理库）
    # if ip: ...

    risk_level = "低"
    if score >= 80:
        risk_level = "高"
    elif score >= 40:
        risk_level = "中"

    event_id = uuid.uuid4().hex[:32]
    ev = RiskEvent(
        event_id=event_id,
        event_type="异常交易",
        risk_level=risk_level,
        score=score,
        description=";".join(reasons) if reasons else "规则检测通过",
        detection_time=now,
        status="待处理" if score > 0 else "已忽略",
        user_id=user_id,
        device_id=device_id,
        ip_address=ip,
        trigger_rule="规则引擎",
    )
    db.session.add(ev)

    tl = EventTimeline(
        event_id=event_id,
        step_no=1,
        step_title="交易检测",
        step_description="规则引擎完成检测",
        timestamp=now,
        type="交易",
        related_entity=tx_id
    )
    db.session.add(tl)

    if score > 0:
        alert = Alert(
            alert_id=uuid.uuid4().hex[:32],
            event_id=event_id,
            alert_type="异常交易告警",
            alert_level=risk_level,
            triggered_at=now,
            status="待处理"
        )
        db.session.add(alert)

    db.session.commit()

    return jsonify({
        "tx_id": tx_id,
        "event_id": event_id,
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    })