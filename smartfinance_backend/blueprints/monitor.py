from datetime import datetime, timedelta

from flask import Blueprint, request

from extensions import db
from models import RiskEvent, User
from api_utils import api_response, paginated_response

bp = Blueprint("monitor", __name__, url_prefix="/api/monitor")


@bp.get("/risk-events")
def monitor_risk_events():
    """获取风险事件列表，对应文档 4.1。"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    type_ = request.args.get("type", "all")
    status = request.args.get("status", "all")
    keyword = request.args.get("keyword")

    query = RiskEvent.query

    if type_ != "all":
        mapping = {
            "fraud": ["账户盗用"],
            "fake": ["证件伪造"],
            "abnormal": ["异常交易", "设备异常"],
            "other": ["批量注册"],
        }
        if type_ in mapping:
            query = query.filter(RiskEvent.event_type.in_(mapping[type_]))

    if status != "all":
        status_map = {
            "pending": "待处理",
            "processing": "处理中",
            "resolved": "已解决",
            "ignored": "已忽略",
        }
        if status in status_map:
            query = query.filter(RiskEvent.status == status_map[status])

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(RiskEvent.description.like(like))

    query = query.order_by(db.func.isnull(RiskEvent.detection_time), RiskEvent.detection_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    def to_item(ev: RiskEvent):
        user = User.query.get(ev.user_id) if ev.user_id else None
        level_map = {"高": "high", "中": "medium", "低": "low"}
        status_rev = {
            "待处理": "pending",
            "处理中": "processing",
            "已解决": "resolved",
            "已忽略": "ignored",
        }
        return {
            "id": ev.event_id,
            "type": "account_theft" if ev.event_type == "账户盗用" else "transaction_abnormal",
            "typeName": ev.event_type,
            "level": level_map.get(ev.risk_level, "medium"),
            "levelName": ev.risk_level,
            "status": status_rev.get(ev.status, "pending"),
            "statusName": ev.status,
            "riskScore": ev.score,
            "detectTime": ev.detection_time.strftime("%Y-%m-%d %H:%M:%S") if ev.detection_time else None,
            "description": ev.description,
            "userId": ev.user_id,
            "username": user.username if user else None,
            "userName": user.username if user else None,
        }

    items = [to_item(ev) for ev in pagination.items]
    return paginated_response(items, pagination.total, page, page_size)


@bp.get("/risk-trend")
def monitor_risk_trend():
    """风险趋势数据，简单基于最近 24 小时统计。"""
    period = request.args.get("period", "today")
    now = datetime.utcnow()
    start_time = now - timedelta(hours=23)

    rows = (
        db.session.query(
            db.func.date_format(RiskEvent.detection_time, "%H:00").label("h"),
            RiskEvent.risk_level,
            db.func.count().label("cnt"),
        )
        .filter(RiskEvent.detection_time.isnot(None))
        .filter(RiskEvent.detection_time >= start_time)
        .group_by("h", RiskEvent.risk_level)
        .all()
    )

    labels = []
    high = []
    medium = []
    low = []

    bucket = {}
    for h, lvl, cnt in rows:
        bucket.setdefault(h, {"高": 0, "中": 0, "低": 0})
        bucket[h][lvl] = int(cnt)

    for i in range(8):  # 简化为 8 个时间点
        t = (start_time + timedelta(hours=3 * i)).strftime("%H:00")
        labels.append(t)
        data = bucket.get(t, {"高": 0, "中": 0, "低": 0})
        high.append(data.get("高", 0))
        medium.append(data.get("中", 0))
        low.append(data.get("低", 0))

    return api_response(
        data={
            "labels": labels,
            "datasets": [
                {"label": "高风险", "data": high},
                {"label": "中风险", "data": medium},
                {"label": "低风险", "data": low},
            ],
        }
    )


@bp.get("/system-status")
def monitor_system_status():
    from models import DataSource

    model_status = "normal"
    data_status = "normal"

    abnormal = DataSource.query.filter(DataSource.status != "正常").count()
    if abnormal > 0:
        data_status = "abnormal"

    return api_response(
        data={
            "modelStatus": model_status,
            "modelStatusName": "正常",
            "dataStatus": data_status,
            "dataStatusName": "正常" if data_status == "normal" else "异常",
        }
    )


@bp.get("/risk-events/<event_id>")
def monitor_risk_event_detail(event_id):
    from models import Device

    ev = RiskEvent.query.get_or_404(event_id)
    user = User.query.get(ev.user_id) if ev.user_id else None
    device = Device.query.get(ev.device_id) if ev.device_id else None

    level_map = {"高": "high", "中": "medium", "低": "low"}
    status_rev = {
        "待处理": "pending",
        "处理中": "processing",
        "已解决": "resolved",
        "已忽略": "ignored",
    }

    data = {
        "id": ev.event_id,
        "type": "account_theft" if ev.event_type == "账户盗用" else "transaction_abnormal",
        "typeName": ev.event_type,
        "level": level_map.get(ev.risk_level, "medium"),
        "levelName": ev.risk_level,
        "status": status_rev.get(ev.status, "pending"),
        "statusName": ev.status,
        "riskScore": ev.score,
        "detectTime": ev.detection_time.strftime("%Y-%m-%d %H:%M:%S") if ev.detection_time else None,
        "description": ev.description,
        "eventDetails": {},
        "userInfo": {},
        "riskAssessment": ev.description,
    }

    if user:
        data["userInfo"] = {
            "userId": user.user_id,
            "username": user.username,
            "name": user.username,
            "registerTime": user.registration_time.strftime("%Y-%m-%d") if user.registration_time else None,
            "level": f"{user.account_level}会员" if user.account_level else None,
            "lastLogin": None,
        }

    if device:
        data["eventDetails"] = {
            "loginIp": device.ip_address,
            "loginLocation": device.location,
            "commonLocation": device.location,
            "device": device.device_name,
            "commonDevice": device.device_name,
        }

    return api_response(data=data)