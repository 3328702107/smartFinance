from datetime import datetime
from typing import Optional

from flask import Blueprint, request, Response

from core.database import db
from models.risk import RiskEvent, EventTimeline, Alert
from models.analysis import RelatedUser, HandlingRecord, RiskAnalysisRecommendation
from models.device import Device
from models.transaction import FinancialTransaction
from models.user import User
from utils.response import api_response, paginated_response


bp = Blueprint("event_analysis", __name__, url_prefix="/event-analysis")


def _dt(v):
    return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


def _status_code(status: Optional[str]) -> str:
    if not status:
        return "pending"
    mapping = {
        "待处理": "pending",
        "处理中": "processing",
        "已解决": "resolved",
        "已忽略": "ignored",
    }
    return mapping.get(status, "pending")


def _level_code(level: Optional[str]) -> str:
    if not level:
        return "medium"
    return {"高": "high", "中": "medium", "低": "low"}.get(level, "medium")


@bp.get("/events/<event_id>")
def event_basic(event_id):
    """7.1 事件概览。"""
    event = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(event.user_id) if event.user_id else None

    data = {
        "id": event.event_id,
        "title": event.event_type,
        "level": _level_code(event.risk_level),
        "levelName": event.risk_level,
        "status": _status_code(event.status),
        "statusName": event.status,
        "score": event.score,
        "type": "account",
        "typeName": event.event_type,
        "createTime": _dt(event.detection_time),
        "updateTime": _dt(event.detection_time),
        "description": event.description,
    }

    if user:
        data["user"] = {
            "userId": user.user_id,
            "username": user.username,
            "name": user.username,
            "level": user.account_level,
        }

    return api_response(data=data)


@bp.get("/events/<event_id>/timeline")
def event_timeline(event_id):
    """7.2 事件时间线。"""
    event = RiskEvent.query.get_or_404(event_id)
    items = (
        EventTimeline.query.filter_by(event_id=event.event_id)
        .order_by(EventTimeline.timestamp.asc())
        .all()
    )

    def _type_code(t: Optional[str]) -> str:
        if not t:
            return "info"
        if "登录" in t:
            return "normal"
        if "验证" in t:
            return "warning"
        if "预警" in t or "告警" in t or "异常" in t:
            return "danger"
        if "处理" in t or "操作" in t:
            return "processing"
        return "info"

    data = [
        {
            "time": _dt(i.timestamp),
            "type": _type_code(i.type),
            "typeName": i.step_title or i.type,
            "description": i.step_description,
        }
        for i in items
    ]

    return api_response(data=data)


@bp.get("/events/<event_id>/trace-path")
def event_trace_path(event_id):
    """7.3 事件行为路径，基于事件时间线和存在的用户/设备信息给出简单关系图。"""
    event = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(event.user_id) if event.user_id else None
    device = Device.query.get(event.device_id) if event.device_id else None

    nodes = []
    edges = []

    if user:
        nodes.append(
            {
                "id": f"user-{user.user_id}",
                "type": "user",
                "label": user.username,
            }
        )

    if device:
        nodes.append(
            {
                "id": f"device-{device.device_id}",
                "type": "device",
                "label": device.device_name or "设备",
            }
        )
        if user:
            edges.append(
                {
                    "source": f"user-{user.user_id}",
                    "target": f"device-{device.device_id}",
                    "relation": "使用设备登录",
                }
            )

    if event.ip_address:
        ip_id = f"ip-{event.ip_address}"
        nodes.append({"id": ip_id, "type": "ip", "label": event.ip_address})
        if user:
            edges.append(
                {
                    "source": f"user-{user.user_id}",
                    "target": ip_id,
                    "relation": "登录 IP",
                }
            )

    return api_response(data={"nodes": nodes, "edges": edges})


@bp.get("/events/<event_id>/related-accounts")
def related_accounts(event_id):
    """7.4 关联账户列表，基于 RelatedUser。"""
    event = RiskEvent.query.get_or_404(event_id)
    related = RelatedUser.query.filter_by(event_id=event.event_id).all()

    data = []
    for r in related:
        user = User.query.get(r.user_id) if r.user_id else None
        data.append({
            "userId": r.user_id,
            "username": user.username if user else None,
            "relationType": r.relation_type,
            "riskScore": r.risk_score,
        })

    return api_response(data=data)


@bp.get("/events/<event_id>/devices-ips")
def event_devices_ips(event_id):
    """7.5 设备和 IP 列表。当前基于事件的设备和 IP 信息简单返回。"""
    event = RiskEvent.query.get_or_404(event_id)
    device = Device.query.get(event.device_id) if event.device_id else None

    devices = []
    if device:
        devices.append(
            {
                "deviceId": device.device_id,
                "deviceName": device.device_name,
                "deviceType": device.os_type,
                "location": device.location,
            }
        )

    ips = []
    if event.ip_address:
        ips.append(
            {
                "ip": event.ip_address,
                "location": None,
                "riskScore": event.score,
            }
        )

    return api_response(data={"devices": devices, "ips": ips})


@bp.get("/events/<event_id>/transactions")
def event_transactions(event_id):
    """7.6 事件关联交易列表。"""
    event = RiskEvent.query.get_or_404(event_id)

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))

    query = FinancialTransaction.query
    if event.user_id:
        query = query.filter(FinancialTransaction.user_id == event.user_id)

    query = query.order_by(FinancialTransaction.transaction_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = [
        {
            "transactionId": t.tx_id,
            "time": _dt(t.transaction_time),
            "amount": float(t.amount) if t.amount is not None else None,
            "type": t.category,
            "status": t.status,
        }
        for t in pagination.items
    ]

    return paginated_response(items, pagination.total, page, page_size)


@bp.get("/events/<event_id>/responsibility")
def event_responsibility(event_id):
    """7.7 责任追溯，当前返回简化的责任主体和结论。"""
    event = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(event.user_id) if event.user_id else None

    main_party = {
        "type": "user",
        "id": user.user_id if user else None,
        "name": user.username if user else None,
        "responsibility": "待确认",
    }

    return api_response(
        data={
            "mainParty": main_party,
            "conclusion": "基于当前证据，责任仍在调查中。",
        }
    )


@bp.get("/events/<event_id>/risk-analysis")
def event_risk_analysis(event_id):
    """7.8 风险分析与建议。"""
    event = RiskEvent.query.get_or_404(event_id)
    rec = (
        RiskAnalysisRecommendation.query.filter_by(event_id=event.event_id)
        .order_by(RiskAnalysisRecommendation.rec_id.desc())
        .first()
    )

    if rec:
        assessment = rec.risk_assessment
        # 将 recommendation_text 按行分割成建议列表
        suggestions_text = rec.recommendation_text or ""
        suggestions = [line.strip() for line in suggestions_text.split("\n") if line.strip()] if suggestions_text else []
    else:
        assessment = event.description or "该事件存在一定风险，请结合业务规则进一步分析。"
        suggestions = [
            "建议核实用户身份信息，确认是否为本人操作。",
            "建议评估近期相关交易，排查异常大额或频繁交易。",
        ]

    data = {
        "assessment": assessment,
        "suggestions": suggestions,
    }

    return api_response(data=data)


@bp.get("/events/<event_id>/processing-records")
def event_processing_records(event_id):
    """7.9 事件处理记录列表。"""
    event = RiskEvent.query.get_or_404(event_id)
    records = (
        HandlingRecord.query.filter_by(event_id=event.event_id)
        .order_by(db.func.isnull(HandlingRecord.action_time), HandlingRecord.action_time.desc())
        .all()
    )

    data = [
        {
            "id": r.record_id,
            "operator": r.operator,
            "action": r.action,
            "time": _dt(r.action_time),
            "note": r.comment,
        }
        for r in records
    ]

    return api_response(data=data)


@bp.post("/events/<event_id>/processing-records")
def add_event_processing_record(event_id):
    """7.10 添加事件处理记录。"""
    event = RiskEvent.query.get_or_404(event_id)
    data = request.get_json() or {}

    note = data.get("note")
    action = data.get("action") or "标记已处理"
    operator = data.get("operator") or "系统"

    if not note:
        return api_response(code=400, message="note required")

    rec = HandlingRecord(
        event_id=event.event_id,
        operator=operator,
        action=action,
        action_time=datetime.utcnow(),
        comment=note,
    )
    db.session.add(rec)
    db.session.commit()

    return api_response(message="处理记录添加成功")


@bp.put("/events/<event_id>/status")
def update_event_status(event_id):
    """7.11 更新事件状态。"""
    event = RiskEvent.query.get_or_404(event_id)
    data = request.get_json() or {}
    status = data.get("status")

    mapping = {
        "pending": "待处理",
        "processing": "处理中",
        "resolved": "已解决",
        "ignored": "已忽略",
    }
    new_status = mapping.get(status, status)

    if new_status not in ["待处理", "处理中", "已解决", "已忽略"]:
        return api_response(code=400, message="invalid status")

    event.status = new_status
    db.session.commit()

    return api_response(message="事件状态更新成功")


@bp.put("/events/<event_id>")
def update_event(event_id):
    """7.12 编辑事件信息，目前支持修改风险等级与描述。"""
    event = RiskEvent.query.get_or_404(event_id)
    data = request.get_json() or {}

    level = data.get("level")
    description = data.get("description")

    if level:
        rev = {"high": "高", "medium": "中", "low": "低"}
        event.risk_level = rev.get(level, event.risk_level)

    if description is not None:
        event.description = description

    db.session.commit()

    return api_response(message="事件信息更新成功")


@bp.get("/events/<event_id>/export")
def export_event_report(event_id):
    """7.13 导出事件分析报告，这里返回简单文本报告。"""
    event = RiskEvent.query.get_or_404(event_id)

    lines = [
        "事件分析报告",
        f"事件 ID: {event.event_id}",
        f"事件类型: {event.event_type}",
        f"风险等级: {event.risk_level}",
        f"风险评分: {event.score}",
        f"状态: {event.status}",
        f"检测时间: {_dt(event.detection_time)}",
        "",
        "描述:",
        event.description or "(无)",
    ]

    content = "\n".join(lines)
    filename = f"event_{event.event_id}_report.txt"

    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
