from flask import Blueprint, request, jsonify
from extensions import db
from models import RiskEvent, EventTimeline, HandlingRecord, Alert, RelatedUser, User, Device, FinancialTransaction

bp = Blueprint("risk_events", __name__, url_prefix="/api/risk_events")

@bp.get("/")
def list_events():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    status = request.args.get("status")
    risk_level = request.args.get("risk_level")

    query = RiskEvent.query
    if status:
        query = query.filter(RiskEvent.status == status)
    if risk_level:
        query = query.filter(RiskEvent.risk_level == risk_level)

    # MySQL 不支持 NULLS LAST 语法，改用 isnull() + desc 以实现“NULL 在后”
    query = query.order_by(db.func.isnull(RiskEvent.detection_time), RiskEvent.detection_time.desc())
    pagination = query.paginate(page=page, per_page=size, error_out=False)

    def to_dict(ev: RiskEvent):
        return {
            "event_id": ev.event_id,
            "event_type": ev.event_type,
            "risk_level": ev.risk_level,
            "score": ev.score,
            "status": ev.status,
            "user_id": ev.user_id,
            "device_id": ev.device_id,
            "ip_address": ev.ip_address,
            "detection_time": ev.detection_time.isoformat() if ev.detection_time else None,
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
        }

    return jsonify({
        "items": [to_dict(ev) for ev in pagination.items],
        "page": page,
        "size": size,
        "total": pagination.total
    })


@bp.get("/stats")
def event_stats():
    """为实时监控等页面提供风险事件统计与趋势数据。"""

    total = RiskEvent.query.count()

    by_level = {}
    for lvl in ["高", "中", "低"]:
        by_level[lvl] = RiskEvent.query.filter(RiskEvent.risk_level == lvl).count()

    by_status = {}
    for s in ["待处理", "处理中", "已解决", "已忽略"]:
        by_status[s] = RiskEvent.query.filter(RiskEvent.status == s).count()

    # 最近 24 小时按小时统计趋势（总量与分级别）
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    start_time = now - timedelta(hours=23)

    # MySQL: 按小时聚合
    rows = (
        db.session.query(
            db.func.date_format(RiskEvent.detection_time, "%Y-%m-%d %H:00:00").label("h"),
            RiskEvent.risk_level,
            db.func.count().label("cnt"),
        )
        .filter(RiskEvent.detection_time.isnot(None))
        .filter(RiskEvent.detection_time >= start_time)
        .group_by("h", RiskEvent.risk_level)
        .all()
    )

    # 初始化 24 个时间段
    buckets = {}
    for i in range(24):
        t = start_time + timedelta(hours=i)
        key = t.replace(minute=0, second=0, microsecond=0).isoformat()
        buckets[key] = {"高": 0, "中": 0, "低": 0}

    for h, lvl, cnt in rows:
        # h 已是字符串时间
        if h not in buckets:
            buckets[h] = {"高": 0, "中": 0, "低": 0}
        buckets[h][lvl] = buckets[h].get(lvl, 0) + int(cnt)

    trend = []
    for key in sorted(buckets.keys()):
        item = buckets[key]
        trend.append(
            {
                "timestamp": key,
                "high": item.get("高", 0),
                "medium": item.get("中", 0),
                "low": item.get("低", 0),
                "total": item.get("高", 0) + item.get("中", 0) + item.get("低", 0),
            }
        )

    return jsonify(
        {
            "total": total,
            "by_level": by_level,
            "by_status": by_status,
            "trend_24h": trend,
        }
    )


@bp.get("/<event_id>")
def get_event_detail(event_id):
    ev = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(ev.user_id) if ev.user_id else None
    device = Device.query.get(ev.device_id) if ev.device_id else None
    tx = FinancialTransaction.query.filter_by(user_id=ev.user_id).order_by(
        FinancialTransaction.transaction_time.desc()
    ).limit(10).all()

    timelines = ev.timelines.order_by(EventTimeline.step_no.asc()).all()
    alerts = ev.alerts.order_by(db.func.isnull(Alert.triggered_at), Alert.triggered_at.desc()).all()
    records = ev.handling_records.order_by(db.func.isnull(HandlingRecord.action_time), HandlingRecord.action_time.desc()).all()
    related_users = ev.related_users.all()

    def _dt(v):
        return v.isoformat() if v else None

    return jsonify({
        "event": {
            "event_id": ev.event_id,
            "event_type": ev.event_type,
            "risk_level": ev.risk_level,
            "score": ev.score,
            "description": ev.description,
            "status": ev.status,
            "user_id": ev.user_id,
            "device_id": ev.device_id,
            "ip_address": ev.ip_address,
            "trigger_rule": ev.trigger_rule,
            "severity_scope": ev.severity_scope,
            "detection_time": _dt(ev.detection_time),
        },
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "status": user.status,
            "account_level": user.account_level
        } if user else None,
        "device": {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "os_type": device.os_type,
            "ip_address": device.ip_address,
            "location": device.location,
            "is_normal": device.is_normal
        } if device else None,
        "recent_transactions": [
            {
                "tx_id": t.tx_id,
                "amount": float(t.amount) if t.amount is not None else None,
                "status": t.status,
                "category": t.category,
                "transaction_time": _dt(t.transaction_time)
            } for t in tx
        ],
        "timelines": [
            {
                "step_no": tl.step_no,
                "step_title": tl.step_title,
                "type": tl.type,
                "timestamp": _dt(tl.timestamp),
                "step_description": tl.step_description
            } for tl in timelines
        ],
        "alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "alert_level": a.alert_level,
                "status": a.status,
                "triggered_at": _dt(a.triggered_at)
            } for a in alerts
        ],
        "handling_records": [
            {
                "record_id": r.record_id,
                "operator": r.operator,
                "action": r.action,
                "action_time": _dt(r.action_time),
                "comment": r.comment
            } for r in records
        ],
        "related_users": [
            {
                "relation_id": ru.relation_id,
                "user_id": ru.user_id,
                "relationship_type": ru.relationship_type,
                "risk_score": ru.risk_score
            } for ru in related_users
        ]
    })


@bp.patch("/<event_id>/status")
def update_event_status(event_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ["待处理", "处理中", "已解决", "已忽略"]:
        return jsonify({"message": "invalid status"}), 400

    ev = RiskEvent.query.get_or_404(event_id)
    ev.status = new_status
    db.session.commit()
    return jsonify({"message": "ok"})


@bp.get("/<event_id>/graph")
def get_event_graph(event_id):
    """为前端关系图提供节点/边数据：事件-用户-设备-关联用户"""
    ev = RiskEvent.query.get_or_404(event_id)
    nodes = []
    edges = []

    def add_node(node_id, node_type, label):
        nodes.append({"id": node_id, "type": node_type, "label": label})

    def add_edge(src, dst, etype):
        edges.append({"source": src, "target": dst, "type": etype})

    add_node(ev.event_id, "event", f"{ev.event_type}-{ev.risk_level}")

    if ev.user_id:
        user = User.query.get(ev.user_id)
        if user:
            add_node(user.user_id, "user", user.username)
            add_edge(ev.event_id, user.user_id, "belongs_to")

    if ev.device_id:
        device = Device.query.get(ev.device_id)
        if device:
            add_node(device.device_id, "device", device.device_name or device.device_id)
            add_edge(ev.event_id, device.device_id, "from_device")

    related_users = RelatedUser.query.filter_by(event_id=ev.event_id).all()
    for ru in related_users:
        ru_user = User.query.get(ru.user_id)
        if ru_user:
            add_node(ru_user.user_id, "user", ru_user.username)
            add_edge(ev.event_id, ru_user.user_id, ru.relationship_type)

    return jsonify({"nodes": nodes, "edges": edges})