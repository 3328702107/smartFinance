# 路由层初始化
# 用于注册所有蓝图

from .auth import bp as auth_bp
from .users import bp as users_bp
from .transactions import bp as transactions_bp
from .alerts import bp as alerts_bp
from .risk_events import bp as risk_events_bp
from .monitor import bp as monitor_bp
from .data_sources import bp as data_sources_bp
from .data_collection import bp as data_collection_bp
from .event_analysis import bp as event_analysis_bp
from .model import bp as model_bp


def register_blueprints(app):
    """注册所有蓝图到 Flask 应用"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(risk_events_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(data_sources_bp)
    app.register_blueprint(data_collection_bp)
    app.register_blueprint(event_analysis_bp)
    app.register_blueprint(model_bp)
