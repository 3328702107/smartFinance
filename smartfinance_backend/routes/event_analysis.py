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


def _event_type_code(event_type: Optional[str]) -> str:
    mapping = {
        "账户盗用": "account_theft",
        "异常交易": "transaction_abnormal",
        "证件伪造": "identity_fake",
        "设备异常": "device_abnormal",
        "批量注册": "batch_registration",
    }
    return mapping.get(event_type or "", "account_theft")


@bp.get("/events/<event_id>")
def event_basic(event_id):
    """7.1 获取事件详情，返回结构与文档示例对齐。"""
    event = RiskEvent.query.get_or_404(event_id)

    # 关联账户和设备数量
    related_accounts = RelatedUser.query.filter_by(event_id=event.event_id).count()
    related_devices = 1 if event.device_id else 0

    # 影响范围：直接映射到中/高
    impact_scope_name = event.severity_scope or "个人"
    impact_scope = "medium" if impact_scope_name == "个人" else "high"

    # 优先级：根据风险等级推导
    level_code = _level_code(event.risk_level)
    priority = level_code
    priority_name = {"high": "高", "medium": "中", "low": "低"}.get(priority, "中")

    # 持续时长：从检测时间到当前的简易计算
    if event.duration:
        duration = event.duration
    elif event.detection_time:
        delta = datetime.utcnow() - event.detection_time
        hours = delta.seconds // 3600 + delta.days * 24
        minutes = (delta.seconds % 3600) // 60
        duration = f"{hours}h {minutes}m"
    else:
        duration = None

    data = {
        "id": event.event_id,
        "title": f"疑似{event.event_type}事件分析",
        "type": _event_type_code(event.event_type),
        "typeName": event.event_type,
        "level": level_code,
        "levelName": f"{event.risk_level}风险" if event.risk_level else None,
        "status": _status_code(event.status),
        "statusName": event.status,
        "detectTime": _dt(event.detection_time),
        "riskScore": event.score,
        "relatedAccounts": int(related_accounts),
        "relatedDevices": int(related_devices),
        "impactScope": impact_scope,
        "impactScopeName": impact_scope_name,
        "priority": priority,
        "priorityName": priority_name,
        "duration": duration,
    }

    return api_response(data=data)


@bp.get("/events/<event_id>/timeline")
def event_timeline(event_id):
    """7.2 获取事件时间线。"""
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
            "id": i.timeline_id,
            "type": _type_code(i.type),
            "typeName": i.step_title or i.type,
            "time": _dt(i.timestamp),
            "description": i.step_description,
            "icon": "user" if "登录" in (i.type or "") else "exclamation-triangle",
        }
        for i in items
    ]

    return api_response(data={"timeline": data})


@bp.get("/events/<event_id>/trace-path")
def event_trace_path(event_id):
    """7.3 获取事件溯源路径。"""
    event = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(event.user_id) if event.user_id else None
    device = Device.query.get(event.device_id) if event.device_id else None

    nodes = []
    edges = []

    # 节点分组：1=事件,2=设备/IP,4=用户
    nodes.append(
        {
            "id": 1,
            "label": event.event_type,
            "group": 1,
            "type": "event",
            "time": _dt(event.detection_time),
            "location": None,
            "device": None,
        }
    )

    next_id = 2
    user_node_id = None

    if user:
        user_node_id = next_id
        nodes.append(
            {
                "id": user_node_id,
                "label": user.username,
                "group": 4,
                "type": "user",
                "userId": user.user_id,
            }
        )
        edges.append({"from": user_node_id, "to": 1, "type": "related"})
        next_id += 1

    if device:
        device_node_id = next_id
        nodes.append(
            {
                "id": device_node_id,
                "label": device.device_name or "设备",
                "group": 2,
                "type": "device",
                "time": _dt(device.last_login_time),
                "location": device.location,
                "device": device.device_name,
            }
        )
        if user_node_id is not None:
            edges.append({"from": user_node_id, "to": device_node_id, "type": "login"})
        next_id += 1

    if event.ip_address:
        ip_node_id = next_id
        nodes.append(
            {
                "id": ip_node_id,
                "label": event.ip_address,
                "group": 2,
                "type": "ip",
            }
        )
        if user_node_id is not None:
            edges.append({"from": user_node_id, "to": ip_node_id, "type": "login"})

    return api_response(data={"nodes": nodes, "edges": edges})


@bp.get("/events/<event_id>/related-accounts")
def related_accounts(event_id):
    """7.4 获取关联账户信息，返回 data.list 结构。"""
    event = RiskEvent.query.get_or_404(event_id)
    related = RelatedUser.query.filter_by(event_id=event.event_id).all()

    result = []

    # 受害者账户（事件主用户）
    main_user = User.query.get(event.user_id) if event.user_id else None
    if main_user:
        result.append(
            {
                "id": main_user.user_id,
                "name": main_user.username,
                "username": main_user.username,
                "role": "victim",
                "roleName": "受害者",
                "registerTime": _dt(main_user.registration_time) if hasattr(main_user, "registration_time") else None,
                "level": main_user.account_level if hasattr(main_user, "account_level") else None,
                "phone": main_user.phone if hasattr(main_user, "phone") else None,
                "email": main_user.email if hasattr(main_user, "email") else None,
                "riskScore": None,
                "status": "normal",
            }
        )

    # 其它关联账户
    for r in related:
        user = User.query.get(r.user_id) if r.user_id else None
        if not user:
            continue
        result.append(
            {
                "id": user.user_id,
                "name": user.username,
                "username": user.username,
                "role": "suspicious",
                "roleName": r.relationship_type,
                "registerTime": _dt(user.registration_time) if hasattr(user, "registration_time") else None,
                "level": user.account_level if hasattr(user, "account_level") else None,
                "phone": user.phone if hasattr(user, "phone") else None,
                "email": user.email if hasattr(user, "email") else None,
                "riskScore": r.risk_score,
                "status": "normal",
            }
        )

    return api_response(data={"list": result})


@bp.get("/events/<event_id>/devices-ips")
def event_devices_ips(event_id):
    """7.5 获取关联设备和 IP 信息。"""
    event = RiskEvent.query.get_or_404(event_id)
    device = Device.query.get(event.device_id) if event.device_id else None

    common_devices = []
    abnormal_devices = []

    if device:
        dev_data = {
            "id": 1,
            "name": device.device_name or "设备",
            "os": device.os_type,
            "browser": None,
            "ip": device.ip_address,
            "location": device.location,
            "type": "mobile" if device.os_type and "ios" in device.os_type.lower() else "desktop",
            "isCommon": bool(getattr(device, "is_normal", True)),
            "loginTime": _dt(device.last_login_time),
        }
        if dev_data["isCommon"]:
            common_devices.append(dev_data)
        else:
            abnormal_devices.append(dev_data)

    ip_analysis = []
    if event.ip_address:
        risk_level = _level_code(event.risk_level)
        ip_analysis.append(
            {
                "ip": event.ip_address,
                "riskLevel": risk_level,
                "riskScore": event.score,
                "location": None,
                "historyCount": 1,
                "historyType": "相关登录",
                "description": f"风险等级: {risk_level}",
            }
        )

    return api_response(
        data={
            "commonDevices": common_devices,
            "abnormalDevices": abnormal_devices,
            "ipAnalysis": ip_analysis,
        }
    )


@bp.get("/events/<event_id>/transactions")
def event_transactions(event_id):
    """7.6 获取事件关联交易记录。"""
    event = RiskEvent.query.get_or_404(event_id)

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))

    query = FinancialTransaction.query
    if event.user_id:
        query = query.filter(FinancialTransaction.user_id == event.user_id)

    query = query.order_by(FinancialTransaction.transaction_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    def _tx_type(category: Optional[str]) -> str:
        if not category:
            return "all"
        if "转入" in category or "收入" in category:
            return "in"
        if "转账" in category or "转出" in category:
            return "out"
        if "退款" in category:
            return "refund"
        return "consume"

    def _status_code_tx(status: Optional[str]) -> str:
        mapping = {"成功": "success", "处理中": "processing", "失败": "failed", "已取消": "cancelled"}
        return mapping.get(status or "", "success")

    items = []
    for t in pagination.items:
        tx_type = _tx_type(t.category)
        status_code = _status_code_tx(t.status)
        amount = float(t.amount) if t.amount is not None else None
        is_abnormal = bool(amount and amount >= 20000)
        items.append(
            {
                "id": t.tx_id,
                "type": tx_type,
                "typeName": t.category,
                "amount": amount,
                "currency": t.currency,
                "fromAccount": None,
                "fromAccountName": None,
                "toAccount": None,
                "toAccountName": None,
                "status": status_code,
                "statusName": t.status,
                "time": _dt(t.transaction_time),
                "isAbnormal": is_abnormal,
                "abnormalReason": "大额交易" if is_abnormal else None,
            }
        )

    return paginated_response(items, pagination.total, page, page_size)


@bp.get("/events/<event_id>/responsibility")
def event_responsibility(event_id):
    """7.7 获取责任追溯信息。"""
    event = RiskEvent.query.get_or_404(event_id)

    nodes = [
        {"id": 1, "label": "黑客攻击", "type": "attacker", "level": "high"},
        {"id": 2, "label": "用户操作", "type": "user", "level": "medium"},
        {"id": 3, "label": "系统防护", "type": "system", "level": "low"},
    ]

    edges = [
        {"from": 1, "to": 2, "value": 5, "label": "导致"},
    ]

    analysis = [
        {
            "type": "attacker",
            "typeName": "主要责任主体",
            "description": "疑似恶意攻击者利用账户信息尝试进行异常操作。",
        },
        {
            "type": "user",
            "typeName": "用户责任",
            "description": "可能存在密码泄露或安全意识不足的情况。",
        },
        {
            "type": "system",
            "typeName": "系统防护",
            "description": "风控系统已拦截部分风险，仍可进一步优化策略。",
        },
    ]

    return api_response(data={"nodes": nodes, "edges": edges, "analysis": analysis})


@bp.get("/events/<event_id>/risk-analysis")
def event_risk_analysis(event_id):
    """7.8 获取风险分析和处理建议。"""
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
            "立即冻结账户，防止进一步损失。",
            "联系用户核实登录及交易行为。",
            "评估相关交易并上报可疑记录。",
        ]

    # 评分维度简单基于事件整体得分拆分
    base = event.score or 80
    risk_scores = {
        "accountSecurity": min(100, base + 10),
        "accountSecurityLevel": "极高" if base >= 80 else "高",
        "fundLoss": max(0, base - 5),
        "fundLossLevel": "高" if base >= 70 else "中",
        "infoLeak": max(0, base - 20),
        "infoLeakLevel": "中" if base >= 60 else "低",
    }

    suggestion_objs = [
        {"order": idx + 1, "title": s.split("，")[0], "description": s}
        for idx, s in enumerate(suggestions)
    ]

    data = {
        "riskAssessment": assessment,
        "riskScores": risk_scores,
        "suggestions": suggestion_objs,
    }

    return api_response(data=data)


@bp.get("/events/<event_id>/processing-records")
def event_processing_records(event_id):
    """7.9 获取处理记录列表。"""
    event = RiskEvent.query.get_or_404(event_id)
    records = (
        HandlingRecord.query.filter_by(event_id=event.event_id)
        .order_by(db.func.isnull(HandlingRecord.action_time), HandlingRecord.action_time.desc())
        .all()
    )

    def _record_to_dict(r: HandlingRecord):
        r_type = "system" if r.operator == "系统" else "manual"
        return {
            "id": r.record_id,
            "type": r_type,
            "typeName": "系统自动处理" if r_type == "system" else "人工处理",
            "handler": r.operator,
            "handlerName": r.operator,
            "handlerAvatar": None,
            "time": _dt(r.action_time),
            "note": r.comment,
        }

    data = [
        _record_to_dict(r)
        for r in records
    ]

    return api_response(data={"list": data})


@bp.post("/events/<event_id>/processing-records")
def add_event_processing_record(event_id):
    """7.10 添加处理记录。"""
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

    r_type = "system" if operator == "系统" else "manual"
    record_data = {
        "id": rec.record_id,
        "type": r_type,
        "typeName": "系统自动处理" if r_type == "system" else "人工处理",
        "handler": operator,
        "handlerName": operator,
        "handlerAvatar": None,
        "time": _dt(rec.action_time),
        "note": note,
    }

    return api_response(message="处理记录添加成功", data=record_data)


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

    return api_response(message="状态更新成功")


@bp.put("/events/<event_id>")
def update_event(event_id):
    """7.12 编辑事件信息。"""
    event = RiskEvent.query.get_or_404(event_id)
    data = request.get_json() or {}

    level = data.get("level")
    note = data.get("note")
    description = data.get("description")

    if level:
        rev = {"high": "高", "medium": "中", "low": "低"}
        event.risk_level = rev.get(level, event.risk_level)

    # note 优先，其次 description
    if note is not None:
        event.description = note
    elif description is not None:
        event.description = description

    db.session.commit()

    return api_response(message="更新成功")


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
