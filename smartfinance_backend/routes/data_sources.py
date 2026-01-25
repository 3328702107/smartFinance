# blueprints/data_sources.py
from flask import Blueprint
from models.data import DataSource, DataQualityIssue
from utils.response import api_response

bp = Blueprint("data_sources", __name__, url_prefix="/api/data_sources")

@bp.get("/")
def list_sources():
    sources = DataSource.query.all()
    return api_response(
        data={
            "list": [
                {
                    "id": s.source_id,
                    "name": s.source_name,
                    "type": s.source_type,
                    "status": s.status,
                    "lastSyncTime": s.last_sync_time.isoformat() if s.last_sync_time else None,
                    "progress": float(s.sync_progress) if s.sync_progress is not None else None,
                    "errorCount": s.error_count,
                    # 补充文档可能需要的字段
                    "connection": s.connection_url,
                    # 采集状态与采集数等增强字段
                    "collectionStatus": (s.collection_status or ("running" if s.status == "正常" else "stopped")),
                    "collectionStatusName": "采集进行中" if (s.collection_status or ("running" if s.status == "正常" else "stopped")) == "running" else "采集已停止",
                    "todayCollected": int(s.today_collected or 0),
                    "estimatedCompletion": s.estimated_completion,
                    "qualityIssuesCount": DataQualityIssue.query.filter_by(source_id=s.source_id).count(),
                    "errorMessage": s.last_error_message,
                }
                for s in sources
            ]
        }
    )


@bp.get("/quality_issues")
def list_quality_issues():
    issues = DataQualityIssue.query.order_by(DataQualityIssue.created_at.desc()).all()
    def _dt(v): return v.isoformat() if v else None
    return api_response(
        data=[
            {
                "issue_id": i.issue_id,
                "source_id": i.source_id,
                "issue_type": i.issue_type,
                "severity": i.severity,
                "status": i.status,
                "created_at": _dt(i.created_at),
            }
            for i in issues
        ]
    )


@bp.get("/stats")
def data_source_stats():
    """为数据采集监控页提供数据源与质量问题汇总。"""

    total = DataSource.query.count()
    normal = DataSource.query.filter(DataSource.status == "正常").count()
    abnormal = DataSource.query.filter(DataSource.status != "正常").count()

    # 未解决/处理中/状态为空的质量问题数量
    from sqlalchemy import or_

    quality_issues_count = DataQualityIssue.query.filter(
        or_(
            DataQualityIssue.status.is_(None),
            DataQualityIssue.status != "已解决",
        )
    ).count()
    return api_response(
        data={
            "total_sources": total,
            "normal_sources": normal,
            "abnormal_sources": abnormal,
            "open_quality_issues": quality_issues_count,
        }
    )