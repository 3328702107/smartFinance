# 模型层初始化
# 导入所有模型以便 SQLAlchemy 能识别它们

from .user import User, AuthAccount
from .device import Device
from .risk import RiskEvent, Alert, EventTimeline
from .transaction import FinancialTransaction
from .analysis import HandlingRecord, RelatedUser, RiskAnalysisRecommendation
from .data import DataSource, DataQualityIssue, LoginLog

__all__ = [
    'User',
    'AuthAccount',
    'Device',
    'RiskEvent',
    'Alert',
    'EventTimeline',
    'FinancialTransaction',
    'HandlingRecord',
    'RelatedUser',
    'RiskAnalysisRecommendation',
    'DataSource',
    'DataQualityIssue',
    'LoginLog',
]
