from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, request, Response
import jwt
from core.database import db
from models.risk import Alert, RiskEvent
from models.analysis import HandlingRecord
from models.user import User
from utils.response import api_response, paginated_response

bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


STATUS_MAP = {
    "pending": "待处理",
    "processing": "处理中",
    "resolved": "已解决",
    "ignored": "已忽略",
}


def _normalize_status(value: Optional[str]):
    if not value:
        return None
    return STATUS_MAP.get(value, value)


def _get_current_operator() -> str:
    """从 Authorization token 中获取当前操作人用户名，失败则返回 "系统"。"""
    from flask import current_app

    token = request.headers.get("Authorization", "")
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    if not token:
        return "系统"

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user = User.query.get(payload.get("sub")) if payload.get("sub") else None
        if not user:
            return "系统"
        # 优先用户名，其次姓名，再次 user_id
        return getattr(user, "username", None) or getattr(user, "name", None) or user.user_id
    except Exception:
        return "系统"


def _append_operation_log(alert: Alert, message: str):
    """在 alerts.operation_log 中追加一条带时间戳的留痕记录。"""
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    if alert.operation_log:
        alert.operation_log = alert.operation_log + "\n" + line
    else:
        alert.operation_log = line


def _add_status_handling_record(alert: Alert, message: str, operator: str):
    """为状态变更写一条 HandlingRecord 记录（如果有事件 ID）。"""
    if not alert.event_id:
        return
    rec = HandlingRecord(
        event_id=alert.event_id,
        operator=operator,
        action="标记已处理",
        action_time=datetime.utcnow(),
        comment=message,
    )
    db.session.add(rec)


def _compute_alert_stats():
    """内部使用的告警统计聚合，返回 dict 数据。"""
    total = Alert.query.count()

    status_counts = {}
    for s in ["待处理", "处理中", "已解决", "已忽略"]:
        status_counts[s] = Alert.query.filter(Alert.status == s).count()

    level_counts = {}
    for lvl in ["高", "中", "低"]:
        level_counts[lvl] = Alert.query.filter(Alert.alert_level == lvl).count()

    high_risk_count = level_counts.get("高", 0)

    # 告警类型趋势：按日期 + 业务类别统计最近 N 天（默认 7 天）
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)

    rows = (
        db.session.query(
            db.func.date(Alert.triggered_at).label("d"),
            Alert.alert_type,
            db.func.count().label("cnt"),
        )
        .filter(Alert.triggered_at.isnot(None))
        .filter(db.func.date(Alert.triggered_at) >= start_date)
        .group_by("d", Alert.alert_type)
        .all()
    )

    def _type_to_category(alert_type: str) -> str:
        if not alert_type:
            return "other"
        if "账户" in alert_type:
            return "account"
        if "交易" in alert_type:
            return "transaction"
        if "身份" in alert_type or "验证" in alert_type:
            return "identity"
        if "设备" in alert_type:
            return "device"
        if "行为" in alert_type:
            return "behavior"
        return "other"

    trend = {}
    for i in range(7):
        d = start_date + timedelta(days=i)
        trend[d.isoformat()] = {
            "account": 0,
            "transaction": 0,
            "identity": 0,
            "device": 0,
            "behavior": 0,
            "other": 0,
        }

    for d, alert_type, cnt in rows:
        key = d.isoformat()
        if key not in trend:
            continue
        cat = _type_to_category(alert_type)
        trend[key][cat] = trend[key].get(cat, 0) + int(cnt)

    trend_list = [{"date": day, **trend[day]} for day in sorted(trend.keys())]

    return {
        "total": total,
        "status_counts": status_counts,
        "level_counts": level_counts,
        "high_risk_count": high_risk_count,
        "recent_trend": trend_list,
    }

@bp.get("/")
def list_alerts():
    # 对应新文档 5.1：GET /alerts
    page = int(request.args.get("page", 1))
    size = int(request.args.get("pageSize", 10))
    status_raw = request.args.get("status", "all")
    level = request.args.get("level", "all")
    event_type = request.args.get("eventType", "all")
    time_range = request.args.get("timeRange", "today")
    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")
    keyword = request.args.get("keyword")

    status = None if status_raw == "all" else _normalize_status(status_raw)

    query = Alert.query
    if status:
        query = query.filter(Alert.status == status)
    if level != "all":
        level_map = {"high": "高", "medium": "中", "low": "低"}
        if level in level_map:
            query = query.filter(Alert.alert_level == level_map[level])

    if event_type != "all":
        query = query.join(RiskEvent, Alert.event_id == RiskEvent.event_id)
        mapping = {
            "account": ["账户盗用", "批量注册"],
            "transaction": ["异常交易"],
            "identity": ["证件伪造"],
            "device": ["设备异常"],
        }
        if event_type in mapping:
            query = query.filter(RiskEvent.event_type.in_(mapping[event_type]))

    # 时间范围筛选
    if time_range != "all" or (start_time and end_time):
        if time_range != "custom":
            today = datetime.utcnow().date()
            if time_range == "today":
                st = datetime.combine(today, datetime.min.time())
                et = datetime.combine(today, datetime.max.time())
            elif time_range == "yesterday":
                y = today - timedelta(days=1)
                st = datetime.combine(y, datetime.min.time())
                et = datetime.combine(y, datetime.max.time())
            elif time_range == "7days":
                st = datetime.combine(today - timedelta(days=6), datetime.min.time())
                et = datetime.combine(today, datetime.max.time())
            elif time_range == "30days":
                st = datetime.combine(today - timedelta(days=29), datetime.min.time())
                et = datetime.combine(today, datetime.max.time())
            else:
                st = et = None
        else:
            st = datetime.fromisoformat(start_time) if start_time else None
            et = datetime.fromisoformat(end_time) if end_time else None

        if st:
            query = query.filter(Alert.triggered_at >= st)
        if et:
            query = query.filter(Alert.triggered_at <= et)

    # 关键字：在告警 ID、类型上模糊匹配
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Alert.alert_id.like(like),
                Alert.alert_type.like(like),
            )
        )

    pagination = query.order_by(db.func.isnull(Alert.triggered_at), Alert.triggered_at.desc()).paginate(
        page=page, per_page=size, error_out=False
    )

    def _dt(v):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None

    def to_item(a: Alert):
        level_code = {"高": "high", "中": "medium", "低": "low"}.get(a.alert_level, "medium")
        status_rev = {
            "待处理": "pending",
            "处理中": "processing",
            "已解决": "resolved",
            "已忽略": "ignored",
        }
        return {
            "id": a.alert_id,
            "eventType": "account",
            "eventTypeName": a.alert_type,
            "level": level_code,
            "levelName": a.alert_level,
            "status": status_rev.get(a.status, "pending"),
            "statusName": a.status,
            "triggerTime": _dt(a.triggered_at),
            "handler": a.handler,
            "handlerName": a.handler,
        }

    items = [to_item(a) for a in pagination.items]
    return paginated_response(items, pagination.total, page, size)


@bp.patch("/<alert_id>/status")
def update_alert_status(alert_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    normalized = _normalize_status(new_status)
    if normalized not in ["待处理", "处理中", "已解决", "已忽略"]:
        return api_response(code=400, message="invalid status")

    alert = Alert.query.get_or_404(alert_id)
    old_status = alert.status or ""  # 可能为 None
    operator = _get_current_operator()
    alert.status = normalized
    alert.handler = operator

    # 留痕：状态变更写入 operation_log 和 HandlingRecord
    msg = f"告警状态变更：{operator} 将状态 {old_status or '未知'} -> {normalized}"
    _append_operation_log(alert, msg)
    _add_status_handling_record(alert, msg, operator)

    db.session.commit()
    return api_response(message="状态更新成功")


@bp.get("/stats")
def alert_stats():
    """为告警管理页提供聚合统计数据。"""
    stats = _compute_alert_stats()
    return api_response(data=stats)


@bp.get("/statistics")
def alert_statistics_view():
    """文档 5.2：总览统计包装。"""
    base = _compute_alert_stats()
    level_counts = base.get("level_counts", {})
    return api_response(
        data={
            "total": base.get("total", 0),
            "pending": base.get("status_counts", {}).get("待处理", 0),
            "resolved": base.get("status_counts", {}).get("已解决", 0),
            "highRisk": level_counts.get("高", 0),
            "mediumRisk": level_counts.get("中", 0),
            "lowRisk": level_counts.get("低", 0),
        }
    )


@bp.get("/level-distribution")
def alert_level_distribution():
    """文档 5.3：按级别分布。"""
    stats = _compute_alert_stats()
    level_counts = stats.get("level_counts", {})
    return api_response(
        data={
            "high": level_counts.get("高", 0),
            "medium": level_counts.get("中", 0),
            "low": level_counts.get("低", 0),
        }
    )


@bp.get("/type-trend")
def alert_type_trend():
    """文档 5.4：告警类型趋势。"""
    days = int(request.args.get("days", 6))
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days - 1)

    rows = (
        db.session.query(
            db.func.date(Alert.triggered_at).label("d"),
            Alert.alert_type,
            db.func.count().label("cnt"),
        )
        .filter(Alert.triggered_at.isnot(None))
        .filter(db.func.date(Alert.triggered_at) >= start_date)
        .group_by("d", Alert.alert_type)
        .all()
    )

    def _date_label(d):
        return d.strftime("%m/%d")

    labels = []
    date_index = {}
    for i in range(days):
        d = start_date + timedelta(days=i)
        labels.append(_date_label(d))
        date_index[d] = i

    series_names = ["账户风险", "交易风险", "身份验证", "设备异常", "行为异常"]
    data_map = {name: [0] * days for name in series_names}

    for d, alert_type, cnt in rows:
        idx = date_index.get(d)
        if idx is None:
            continue
        name = "其他"
        if alert_type and "账户" in alert_type:
            name = "账户风险"
        elif alert_type and "交易" in alert_type:
            name = "交易风险"
        elif alert_type and ("身份" in alert_type or "验证" in alert_type):
            name = "身份验证"
        elif alert_type and "设备" in alert_type:
            name = "设备异常"
        elif alert_type and "行为" in alert_type:
            name = "行为异常"

        if name not in data_map:
            continue
        data_map[name][idx] += int(cnt)

    datasets = [{"label": name, "data": data_map[name]} for name in series_names]

    return api_response(data={"labels": labels, "datasets": datasets})


@bp.get("/<alert_id>")
def alert_detail(alert_id):
    """文档 5.5：告警详情。"""
    alert = Alert.query.get_or_404(alert_id)
    event = RiskEvent.query.get(alert.event_id) if alert.event_id else None
    user = User.query.get(event.user_id) if event and event.user_id else None

    def _dt(v):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None

    level_code = {"高": "high", "中": "medium", "低": "low"}.get(alert.alert_level, "medium")
    status_rev = {
        "待处理": "pending",
        "处理中": "processing",
        "已解决": "resolved",
        "已忽略": "ignored",
    }

    data = {
        "id": alert.alert_id,
        "eventType": "account",
        "eventTypeName": alert.alert_type,
        "level": level_code,
        "levelName": alert.alert_level,
        "status": status_rev.get(alert.status, "pending"),
        "statusName": alert.status,
        "triggerTime": _dt(alert.triggered_at),
        "rule": event.trigger_rule if event else None,
        "riskScore": event.score if event else None,
    }

    data["basicInfo"] = {
        "alertId": alert.alert_id,
        "eventType": alert.alert_type,
        "level": alert.alert_level,
        "triggerTime": _dt(alert.triggered_at),
        "status": alert.status,
        "rule": event.trigger_rule if event else None,
        "riskScore": event.score if event else None,
    }

    if user:
        data["userInfo"] = {
            "userId": user.user_id,
            "username": user.username,
            "name": user.username,
            "registerTime": user.registration_time.strftime("%Y-%m-%d") if user.registration_time else None,
            "level": f"{user.account_level}会员" if user.account_level else None,
            "phone": user.phone,
            "lastLogin": None,
        }

    # 事件详情部分目前基于 RiskEvent.description 占位
    if event:
        data["eventDetails"] = {
            "description": event.description,
            "abnormalLogin": {
                "ip": event.ip_address,
                "location": None,
                "device": None,
                "loginMethod": None,
            },
            "normalPattern": {
                "commonIp": None,
                "commonLocation": None,
                "commonDevice": None,
                "commonTime": None,
            },
        }
        data["riskAssessment"] = event.description

    # 处理记录列表基于 HandlingRecord
    records = HandlingRecord.query.filter_by(event_id=alert.event_id).order_by(
        db.func.isnull(HandlingRecord.action_time), HandlingRecord.action_time.desc()
    ).all()

    def _record_type(rec: HandlingRecord) -> str:
        return "system" if rec.operator == "系统" else "manual"

    data["processingRecords"] = [
        {
            "type": _record_type(r),
            "typeName": "系统创建" if _record_type(r) == "system" else "人工处理",
            "handler": r.operator,
            "handlerName": r.operator,
            "time": _dt(r.action_time),
            "note": r.comment,
        }
        for r in records
    ]

    # 返回操作日志原文，便于前端展示留痕记录
    data["operationLog"] = alert.operation_log or ""

    return api_response(data=data)


@bp.put("/<alert_id>/status")
def put_alert_status(alert_id):
    """兼容文档 5.6 的 PUT 方法。"""
    return update_alert_status(alert_id)


@bp.post("/batch-operation")
def batch_operation():
    """文档 5.7：批量操作告警。"""
    data = request.get_json() or {}
    ids = data.get("alertIds") or []
    action = data.get("action")

    if not isinstance(ids, list) or not action:
        return api_response(code=400, message="alertIds and action required")

    success = 0
    fail = 0

    operator = _get_current_operator()

    for aid in ids:
        alert = Alert.query.get(aid)
        if not alert:
            fail += 1
            continue
        try:
            if action == "delete":
                db.session.delete(alert)
            else:
                mapping = {
                    "resolve": "已解决",
                    "ignore": "已忽略",
                    "process": "处理中",
                }
                new_status = mapping.get(action)
                if not new_status:
                    fail += 1
                    continue
                old_status = alert.status or ""
                alert.status = new_status
                alert.handler = operator
                msg = f"批量操作({action})：{operator} 将状态 {old_status or '未知'} -> {new_status}"
                _append_operation_log(alert, msg)
                _add_status_handling_record(alert, msg, operator)
            success += 1
        except Exception:
            fail += 1

    db.session.commit()

    return api_response(
        message="批量操作成功",
        data={"successCount": success, "failCount": fail},
    )


@bp.post("/<alert_id>/processing-record")
def add_alert_processing_record(alert_id):
    """文档 5.8：为告警添加处理记录，写入对应事件的 HandlingRecord。"""
    data = request.get_json() or {}
    note = data.get("note")
    action_code = data.get("action")

    if not note:
        return api_response(code=400, message="note required")

    alert = Alert.query.get_or_404(alert_id)
    action_map = {
        "freeze": "冻结账户",
        "send_verification": "发送验证码",
        "mark_resolved": "标记已处理",
        "ignore": "忽略",
        "contact_user": "联系用户",
    }
    action_name = action_map.get(action_code, "标记已处理") if action_code else "标记已处理"

    operator = data.get("operator") or _get_current_operator()
    alert.handler = operator

    rec = HandlingRecord(
        event_id=alert.event_id,
        operator=operator,
        action=action_name,
        action_time=datetime.utcnow(),
        comment=note,
    )
    db.session.add(rec)

    # 留痕：处理记录也写入 alerts.operation_log
    log_msg = f"处理记录：{operator} 执行 {action_name}，备注：{note}"
    _append_operation_log(alert, log_msg)
    db.session.commit()

    return api_response(message="处理记录添加成功")