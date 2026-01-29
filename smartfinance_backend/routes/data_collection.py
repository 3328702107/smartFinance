from datetime import datetime, timedelta
from io import StringIO
from typing import Optional

from flask import Blueprint, request, Response
from sqlalchemy import or_

from core.database import db
from models.data import DataSource, DataQualityIssue, LoginLog
from models.transaction import FinancialTransaction
from models.device import Device
from utils.response import api_response, paginated_response

bp = Blueprint("data_collection", __name__, url_prefix="/data-collection")


# 6.1 获取数据源列表
@bp.get("/data-sources")
def list_data_sources():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    status = request.args.get("status", "all")
    keyword = request.args.get("keyword")

    query = DataSource.query

    # 状态映射：normal/warning/error/stopped -> 数据源 status
    if status != "all":
        status_map = {
            "normal": ["正常"],
            "warning": ["异常"],
            "error": ["异常"],
            "stopped": ["中断"],
        }
        if status in status_map:
            query = query.filter(DataSource.status.in_(status_map[status]))

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(DataSource.source_name.like(like))

    query = query.order_by(DataSource.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    def to_item(s: DataSource):
        # 采集状态优先使用表中的 collection_status，没有则根据运行状态推导
        collection_status = s.collection_status or ("running" if s.status == "正常" else "stopped")
        quality_issues_count = DataQualityIssue.query.filter_by(source_id=s.source_id).count()
        return {
            "id": s.source_id,
            "name": s.source_name,
            "type": _map_source_type_code(s.source_type),
            "connection": s.connection_url,
            "status": _map_source_status_code(s.status),
            "statusName": s.status,
            "collectionStatus": collection_status,
            "collectionStatusName": "采集进行中" if collection_status == "running" else "已停止",
            "lastSyncTime": s.last_sync_time.strftime("%Y-%m-%d %H:%M:%S") if s.last_sync_time else None,
            "progress": int(s.sync_progress or 0),
            "todayCollected": int(s.today_collected or 0),
            "estimatedCompletion": s.estimated_completion,
            "qualityIssuesCount": quality_issues_count,
            "errorMessage": s.last_error_message,
        }

    items = [to_item(s) for s in pagination.items]
    return paginated_response(items, pagination.total, page, page_size)


# 6.2 获取数据源统计
@bp.get("/statistics")
def data_collection_statistics():
    total = DataSource.query.count()
    normal = DataSource.query.filter(DataSource.status == "正常").count()
    abnormal = DataSource.query.filter(DataSource.status != "正常").count()
    quality_issues = DataQualityIssue.query.filter(
        or_(
            DataQualityIssue.status.is_(None),
            DataQualityIssue.status != "已解决",
        )
    ).count()

    return api_response(
        data={
            "total": total,
            "normal": normal,
            "abnormal": abnormal,
            "qualityIssues": quality_issues,
        }
    )


# 6.3 获取数据源状态分布
@bp.get("/status-distribution")
def data_source_status_distribution():
    def c(cond):
        return DataSource.query.filter(cond).count()

    normal = c(DataSource.status == "正常")
    warning = c(DataSource.status == "异常")
    error = c(DataSource.status == "异常")
    stopped = c(DataSource.status == "中断")

    return api_response(
        data={
            "normal": normal,
            "warning": warning,
            "error": error,
            "stopped": stopped,
        }
    )


# 6.4 获取数据采集趋势
@bp.get("/collection-trend")
def data_collection_trend():
    # period 参数目前保留以兼容文档；这里统一按「最近 8 个整点」聚合
    _ = request.args.get("period", "today")

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_base = now - timedelta(hours=7)

    labels = []
    trade_data = []
    behavior_data = []
    device_data = []

    for i in range(8):
        slot_start = start_base + timedelta(hours=i)
        slot_end = slot_start + timedelta(hours=1)
        labels.append(slot_start.strftime("%H:00"))

        # 交易数据：按交易时间统计条数
        trade_count = FinancialTransaction.query.filter(
            FinancialTransaction.transaction_time >= slot_start,
            FinancialTransaction.transaction_time < slot_end,
        ).count()

        # 用户行为：按登录日志统计条数
        behavior_count = LoginLog.query.filter(
            LoginLog.login_time >= slot_start,
            LoginLog.login_time < slot_end,
        ).count()

        # 设备数据：按设备最近登录时间统计条数
        device_count = Device.query.filter(
            Device.last_login_time >= slot_start,
            Device.last_login_time < slot_end,
        ).count()

        trade_data.append(trade_count)
        behavior_data.append(behavior_count)
        device_data.append(device_count)

    return api_response(
        data={
            "labels": labels,
            "datasets": [
                {"label": "交易数据", "data": trade_data},
                {"label": "用户行为", "data": behavior_data},
                {"label": "设备数据", "data": device_data},
            ],
        }
    )


# 6.5 获取数据质量问题
@bp.get("/data-sources/<source_id>/quality-issues")
def quality_issues_by_source(source_id):
    # 先检查数据源是否存在
    if DataSource.query.get(source_id) is None:
        return api_response(code=404, message="数据源不存在")

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    issue_type = request.args.get("type", "all")

    query = DataQualityIssue.query.filter_by(source_id=source_id)

    type_map = {
        "missing": "缺失字段",
        "format": "格式错误",
        "abnormal": "值异常",
        "inconsistent": "数据不一致",
    }
    if issue_type != "all" and issue_type in type_map:
        query = query.filter(DataQualityIssue.issue_type == type_map[issue_type])

    query = query.order_by(DataQualityIssue.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    def _dt(v):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None

    def to_item(i: DataQualityIssue):
        code = _map_issue_type_code(i.issue_type)
        return {
            "id": f"ISSUE-{i.issue_id}",
            "type": code,
            "typeName": _map_issue_type_name(code),
            "field": None,
            "description": i.description,
            "time": _dt(i.created_at),
        }

    items = [to_item(i) for i in pagination.items]

    # 统计分布（当前数据源）
    statistics = _calculate_quality_issue_statistics(source_id)

    return api_response(
        data={
            "list": items,
            "statistics": statistics,
            "total": pagination.total,
            "page": page,
            "pageSize": page_size,
        }
    )


@bp.get("/quality-issues/summary")
def quality_issues_summary():
    """数据质量问题汇总（所有数据源维度）。"""

    statistics = _calculate_quality_issue_statistics()
    total = sum(statistics.values())

    return api_response(
        data={
            "statistics": statistics,
            "total": total,
        }
    )


# 6.6 获取数据预览（占位实现）
@bp.get("/data-sources/<source_id>/preview")
def data_preview(source_id):
    # 不存在的数据源直接返回 404
    ds = DataSource.query.get(source_id)
    if ds is None:
        return api_response(code=404, message="数据源不存在")

    _type = request.args.get("type", "trade")
    limit = int(request.args.get("limit", 10))

    # 当前数据库未存储原始业务数据，这里返回结构化占位示例
    if _type == "trade":
        sample = [
            {
                "transactionId": "TX2023061500123",
                "userId": "USER789456",
                "amount": 2560.00,
                "time": "14:32:15",
                "status": "success",
            }
        ]
    elif _type == "user":
        sample = [
            {
                "userId": "USER789456",
                "username": "demo_user",
                "level": "VIP",
            }
        ]
    elif _type == "image":
        sample = [
            {
                "imageId": "IMG20230615001",
                "url": "https://example.com/image/IMG20230615001.jpg",
                "size": 204800,
                "time": "14:32:15",
                "status": "stored",
            }
        ]
    elif _type == "device":
        sample = [
            {
                "deviceId": "DEV123",
                "os": "iOS",
                "location": "上海",
            }
        ]
    else:
        sample = []

    # total 更贴近文档语义：优先使用数据源 today_collected 字段
    total = int(ds.today_collected or len(sample))

    return api_response(data={"list": sample[:limit], "total": total})


# 6.7 获取数据质量评分（简单基于问题严重程度估算）
@bp.get("/data-sources/<source_id>/quality-score")
def data_quality_score(source_id):
    # 先检查数据源是否存在
    if DataSource.query.get(source_id) is None:
        return api_response(code=404, message="数据源不存在")

    issues = DataQualityIssue.query.filter_by(source_id=source_id).all()
    score = 100
    for i in issues:
        if i.severity == "高":
            score -= 5
        elif i.severity == "中":
            score -= 3
        elif i.severity == "低":
            score -= 1
    score = max(0, min(100, score))

    return api_response(
        data={
            "score": score,
            "maxScore": 100,
            "dimensions": {
                "completeness": score,
                "accuracy": score,
                "consistency": score,
                "timeliness": score,
            },
        }
    )


# 6.8 重新连接数据源
@bp.post("/data-sources/<source_id>/reconnect")
def reconnect_data_source(source_id):
    ds = DataSource.query.get_or_404(source_id)
    ds.status = "正常"
    ds.last_error_message = None
    ds.last_sync_time = datetime.utcnow()
    ds.updated_at = datetime.utcnow()
    db.session.commit()
    return api_response(message="重新连接成功")


# 6.9 导出数据质量问题列表（CSV）
@bp.get("/data-sources/<source_id>/quality-issues/export")
def export_quality_issues(source_id):
    # 不存在的数据源直接返回 404
    if DataSource.query.get(source_id) is None:
        return api_response(code=404, message="数据源不存在")

    fmt = request.args.get("format", "csv")
    if fmt != "csv":
        return api_response(code=400, message="only csv export is supported currently")

    # 支持按文档中的 type 参数过滤导出的质量问题类型
    issue_type = request.args.get("type", "all")
    type_map = {
        "missing": "缺失字段",
        "format": "格式错误",
        "abnormal": "值异常",
        "inconsistent": "数据不一致",
    }

    query = DataQualityIssue.query.filter_by(source_id=source_id)
    if issue_type != "all" and issue_type in type_map:
        query = query.filter(DataQualityIssue.issue_type == type_map[issue_type])

    issues = query.order_by(DataQualityIssue.created_at.desc()).all()

    def _dt(v):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    output = StringIO()
    output.write("id,type,description,time\n")
    for i in issues:
        output.write(
            f"ISSUE-{i.issue_id},{_map_issue_type_code(i.issue_type)},{(i.description or '').replace(',', ' ')},{_dt(i.created_at)}\n"
        )

    csv_data = output.getvalue()
    output.close()

    filename = f"quality_issues_{source_id}.csv"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "text/csv; charset=utf-8",
    }
    return Response(csv_data, headers=headers)


# 辅助映射函数

def _map_source_type_code(source_type: Optional[str]) -> str:
    mapping = {
        "数据库": "database",
        "API": "api",
        "文件": "file",
        "消息队列": "stream",
    }
    return mapping.get(source_type or "", "database")


def _map_source_status_code(status: Optional[str]) -> str:
    mapping = {
        "正常": "normal",
        "异常": "error",
        "中断": "stopped",
    }
    return mapping.get(status or "", "normal")


def _map_issue_type_code(issue_type: Optional[str]) -> str:
    mapping = {
        "缺失字段": "missing",
        "格式错误": "format",
        "值异常": "abnormal",
        "数据不一致": "inconsistent",
    }
    return mapping.get(issue_type or "", "missing")


def _map_issue_type_name(code: str) -> str:
    mapping = {
        "missing": "缺失值",
        "format": "格式错误",
        "abnormal": "值异常",
        "inconsistent": "数据不一致",
    }
    return mapping.get(code, code)


def _calculate_quality_issue_statistics(source_id: Optional[str] = None) -> dict:
    """按照问题类型统计数量。

    :param source_id: 如果传入，则仅统计该数据源；不传则统计所有数据源。
    :return: {"missing": int, "formatError": int, "abnormal": int, "inconsistent": int}
    """

    query = db.session.query(DataQualityIssue.issue_type, db.func.count().label("cnt"))
    if source_id is not None:
        query = query.filter(DataQualityIssue.source_id == source_id)

    stats_rows = query.group_by(DataQualityIssue.issue_type).all()

    statistics = {"missing": 0, "formatError": 0, "abnormal": 0, "inconsistent": 0}
    for t, cnt in stats_rows:
        code = _map_issue_type_code(t)
        if code == "missing":
            statistics["missing"] += int(cnt)
        elif code == "format":
            statistics["formatError"] += int(cnt)
        elif code == "abnormal":
            statistics["abnormal"] += int(cnt)
        elif code == "inconsistent":
            statistics["inconsistent"] += int(cnt)

    return statistics


    # 采集指标现在完全来源于数据库字段，不再在路由层做演示计算
