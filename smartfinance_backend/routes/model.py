# 模型路由
from flask import Blueprint, request, jsonify

bp = Blueprint("model", __name__, url_prefix="/api/model")

@bp.post("/risk_score")
def mock_risk_score():
    """
    模型接口占位：前端可以调用，但现在返回固定结果。
    """
    _ = request.get_json()  # 暂不使用
    return jsonify({
        "score": 65,
        "risk_level": "中",
        "explanations": ["占位：基于规则+模型的综合评分接口，当前未接入大模型"]
    })