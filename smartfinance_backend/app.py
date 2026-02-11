from flask import Flask, jsonify
from sqlalchemy import text

from config import config_map
from core.database import db
from routes import register_blueprints

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        """健康检查与简单运行状态汇总。"""

        db_status = "ok"
        try:
            # 简单探测数据库连通性
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_status = "error"

        # 数据运行状态：任一数据源异常/中断则视为异常
        data_status = "unknown"
        try:
            from models.data import DataSource  # 延迟导入避免循环引用

            abnormal = DataSource.query.filter(DataSource.status != "正常").count()
            data_status = "正常" if abnormal == 0 else "异常"
        except Exception:
            data_status = "unknown"

        from services.model_service import ModelService

        model_summary = ModelService.get_model_status_summary()
        model_overall = model_summary.get("overall_status", "degraded")
        model_status = "正常" if model_overall == "normal" else ("降级" if model_overall == "degraded" else "异常")

        from datetime import datetime

        return jsonify(
            {
                "status": "ok" if db_status == "ok" else "degraded",
                "db": db_status,
                "model_status": model_status,
                "model_status_code": model_overall,
                "model_details": model_summary.get("services", []),
                "data_status": data_status,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    return app

if __name__ == "__main__":
    app = create_app("dev")
    app.run(host="0.0.0.0", port=5000, debug=True)
