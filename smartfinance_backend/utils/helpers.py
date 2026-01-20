# 辅助函数
from datetime import datetime


def format_datetime(dt):
    """格式化日期时间"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def format_date(dt):
    """格式化日期"""
    return dt.strftime("%Y-%m-%d") if dt else None


def iso_format(dt):
    """ISO 格式化日期时间"""
    return dt.isoformat() if dt else None
