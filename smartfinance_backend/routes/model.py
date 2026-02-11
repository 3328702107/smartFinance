from flask import Blueprint, request

from services.model_service import ModelService, ModelServiceError
from services.risk_service import RiskService
from utils.response import api_response

bp = Blueprint("model", __name__, url_prefix="/api/model")


def _get_request_payload():
    payload = request.get_json(silent=True) or {}
    if request.form:
        payload.update(request.form.to_dict())
    return payload


def _to_optional_float(value):
    if value is None or value == "":
        return None
    return float(value)


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


@bp.get("/status")
def model_status():
    summary = ModelService.get_model_status_summary()
    return api_response(data=summary)


@bp.get("/image-detect/health")
def image_detector_health():
    return api_response(data=ModelService.get_image_detector_status())


@bp.post("/image-detect")
def image_detect():
    image_file = request.files.get("image") or request.files.get("file")
    if not image_file:
        return api_response(code=400, message="image file is required (field: image or file)")

    try:
        result = ModelService.detect_image(image_file)
        return api_response(data=result)
    except ModelServiceError as exc:
        return api_response(code=502, message=str(exc))


@bp.post("/qianfan-risk-judge")
def qianfan_risk_judge():
    payload = _get_request_payload()
    query = payload.get("query") or payload.get("case_text") or payload.get("description")
    if not query:
        return api_response(code=400, message="query is required")

    try:
        result = ModelService.ask_qianfan(
            query=query,
            user_id=payload.get("user_id"),
            conversation_id=payload.get("conversation_id"),
            inputs=payload.get("inputs") if isinstance(payload.get("inputs"), dict) else None,
        )
        return api_response(data=result)
    except ModelServiceError as exc:
        return api_response(code=502, message=str(exc))


@bp.post("/risk_score")
def risk_score():
    payload = _get_request_payload()

    warnings = []
    reasons = []

    # 1) Rule engine score
    try:
        amount = _to_optional_float(payload.get("amount"))
    except ValueError:
        return api_response(code=400, message="amount must be numeric")

    user_id = payload.get("user_id")
    device_id = payload.get("device_id")
    ip_address = payload.get("ip_address")

    rule_score = 0
    rule_level = "低"
    rule_reasons = []
    if user_id and amount is not None:
        try:
            rule_score, rule_level, rule_reasons = RiskService.assess_transaction_risk(
                user_id=user_id,
                amount=amount,
                device_id=device_id,
                ip=ip_address,
            )
            reasons.extend(rule_reasons)
        except Exception as exc:
            warnings.append(f"rule engine failed: {exc}")
    elif amount is not None and amount >= 10000:
        # 无 user_id 时给一个最小兜底规则，便于单接口联调
        rule_score = 50
        rule_level = "中"
        rule_reasons = ["大额交易"]
        reasons.extend(rule_reasons)

    # 2) Image detector
    image_score = 0
    image_result = {"available": False, "service": "image_detector", "message": "no image uploaded"}
    image_file = request.files.get("image") or request.files.get("file")
    if image_file:
        try:
            image_result = ModelService.detect_image(image_file)
            image_score = int(round(image_result.get("ai_probability", 0) * 40))
            image_result["score_delta"] = image_score
            if image_result.get("is_fake"):
                prob_text = round(image_result.get("ai_probability", 0) * 100, 2)
                reasons.append(f"图像疑似AI伪造（{prob_text}%）")
        except ModelServiceError as exc:
            image_result = {"available": False, "service": "image_detector", "message": str(exc)}
            warnings.append(str(exc))

    # 3) Qianfan judgement
    qianfan_score = 0
    qianfan_result = {"available": False, "service": "qianfan_appbuilder", "message": "skipped"}
    use_qianfan = _to_bool(payload.get("use_qianfan"), default=True)
    if use_qianfan:
        qianfan_query = payload.get("query") or payload.get("case_text") or payload.get("description")
        if not qianfan_query and _to_bool(payload.get("auto_prompt"), default=True):
            qianfan_query = ModelService.build_qianfan_prompt(payload, reasons)
        if qianfan_query:
            try:
                qianfan_result = ModelService.ask_qianfan(
                    query=qianfan_query,
                    user_id=user_id,
                    conversation_id=payload.get("conversation_id"),
                    inputs=payload.get("inputs") if isinstance(payload.get("inputs"), dict) else None,
                )
                if qianfan_result.get("available"):
                    qianfan_score = int(qianfan_result.get("score_delta", 0))
                    qianfan_result["score_delta"] = qianfan_score
                    inferred_level = qianfan_result.get("inferred_level")
                    if inferred_level in {"高", "中", "低"}:
                        reasons.append(f"千帆模型判断：{inferred_level}风险")
                else:
                    warnings.append(qianfan_result.get("message", "qianfan unavailable"))
            except ModelServiceError as exc:
                qianfan_result = {"available": False, "service": "qianfan_appbuilder", "message": str(exc)}
                warnings.append(str(exc))

    final_score = max(0, min(100, int(rule_score + image_score + qianfan_score)))
    final_level = ModelService.score_to_level(final_score)

    if not reasons:
        reasons.append("未触发明显风险特征")

    return api_response(
        data={
            # backward-compatible fields
            "score": final_score,
            "risk_level": final_level,
            "explanations": reasons,
            # detailed fields
            "components": {
                "rule_engine": {
                    "score": int(rule_score),
                    "risk_level": rule_level,
                    "reasons": rule_reasons,
                },
                "image_detector": image_result,
                "qianfan_appbuilder": qianfan_result,
            },
            "warnings": warnings,
        }
    )
