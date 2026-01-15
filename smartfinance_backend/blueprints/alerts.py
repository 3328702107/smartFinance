from flask import Blueprint, request, jsonify
from extensions import db
from models import Alert, RiskEvent

bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


STATUS_MAP = {
    "pending": "待处理",
    "processing": "处理中",
    "resolved": "已解决",
    "ignored": "已忽略",
}


def _normalize_status(value: str | None):
    if not value:
        return None
    return STATUS_MAP.get(value, value)

@bp.get("/")
def list_alerts():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    status = _normalize_status(request.args.get("status"))

    # 通过事件类型进行分类筛选（account/transaction/identity/device/behavior）
    category = request.args.get("category")

    query = Alert.query
    if status:
        query = query.filter(Alert.status == status)

    if category:
        # 只有在需要按事件类别筛选时才 join 风险事件表
        query = query.join(RiskEvent, Alert.event_id == RiskEvent.event_id)

        # 将前端的业务类别映射到具体的事件类型枚举
        mapping = {
            "account": ["账户盗用", "批量注册"],
            "transaction": ["异常交易"],
            "identity": ["证件伪造"],
            "device": ["设备异常"],
            # 行为异常目前尚未单独建枚举，可在将来扩展
        }
        if category in mapping:
            query = query.filter(RiskEvent.event_type.in_(mapping[category]))

    # MySQL 不支持 NULLS LAST，改为 isnull() + desc，实现触发时间为空的记录排后
    pagination = query.order_by(db.func.isnull(Alert.triggered_at), Alert.triggered_at.desc()).paginate(page=page, per_page=size, error_out=False)

    def _dt(v):
        return v.isoformat() if v else None

    return jsonify({
        "items": [
            {
                "alert_id": a.alert_id,
                "event_id": a.event_id,
                "alert_type": a.alert_type,
                "alert_level": a.alert_level,
                "status": a.status,
                "handler": a.handler,
                "triggered_at": _dt(a.triggered_at)
            } for a in pagination.items
        ],
        "page": page,
        "size": size,
        "total": pagination.total
    })


@bp.patch("/<alert_id>/status")
def update_alert_status(alert_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    normalized = _normalize_status(new_status)
    if normalized not in ["待处理", "处理中", "已解决", "已忽略"]:
        return jsonify({"message": "invalid status"}), 400

    alert = Alert.query.get_or_404(alert_id)
    alert.status = normalized
    db.session.commit()
    return jsonify({"message": "ok"})


@bp.get("/stats")
def alert_stats():
    """为告警管理页提供聚合统计数据。"""

    total = Alert.query.count()

    # 按处理状态统计
    status_counts = {}
    for s in ["待处理", "处理中", "已解决", "已忽略"]:
        status_counts[s] = Alert.query.filter(Alert.status == s).count()

    # 按告警级别统计
    level_counts = {}
    for lvl in ["高", "中", "低"]:
        level_counts[lvl] = Alert.query.filter(Alert.alert_level == lvl).count()

    high_risk_count = level_counts.get("高", 0)

    # 告警类型趋势：按日期 + 业务类别统计最近 7 天
    from datetime import datetime, timedelta

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

    # 初始化最近 7 天的日期字典
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

    trend_list = [
        {"date": day, **trend[day]} for day in sorted(trend.keys())
    ]

    return jsonify(
        {
            "total": total,
            "status_counts": status_counts,
            "level_counts": level_counts,
            "high_risk_count": high_risk_count,
            "recent_trend": trend_list,
        }
    )