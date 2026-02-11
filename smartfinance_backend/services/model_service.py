from __future__ import annotations

import base64
import json
import time
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import requests
from flask import current_app


class ModelServiceError(Exception):
    """Model service invocation error."""


class ModelService:
    """Model aggregation service for Qianfan + image detector."""

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def score_to_level(score: int) -> str:
        if score >= 80:
            return "高"
        if score >= 40:
            return "中"
        return "低"

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                return str(payload.get("error") or payload.get("message") or payload)
            return str(payload)
        except Exception:
            return response.text[:200] if response.text else f"HTTP {response.status_code}"

    @staticmethod
    def _join_url(base_url: str, path: str) -> str:
        base = (base_url or "").rstrip("/")
        suffix = path if str(path).startswith("/") else f"/{path}"
        return f"{base}{suffix}"

    @classmethod
    def _normalize_image_detector_payload(cls, payload: Dict[str, Any], transport: str) -> Dict[str, Any]:
        ai_probability = cls._safe_float(
            payload.get("ai_probability", payload.get("probability", payload.get("score", 0.0))), 0.0
        )
        ai_probability = max(0.0, min(1.0, ai_probability))

        result_raw = str(payload.get("result", payload.get("prediction", payload.get("label", ""))) or "").lower()
        is_fake_raw = payload.get("is_fake")
        if is_fake_raw is None:
            if result_raw:
                is_fake = "fake" in result_raw
            else:
                is_fake = ai_probability >= 0.5
        else:
            is_fake = bool(is_fake_raw)

        if result_raw not in {"fake", "real"}:
            result_raw = "fake" if is_fake else "real"

        probabilities = payload.get("probabilities")
        if not isinstance(probabilities, dict):
            probabilities = {}
            model_name = payload.get("model") or payload.get("detector")
            if model_name:
                probabilities[str(model_name)] = ai_probability

        return {
            "available": True,
            "service": "image_detector",
            "transport": transport,
            "ai_probability": ai_probability,
            "is_fake": is_fake,
            "result": result_raw,
            "probabilities": probabilities,
            "raw": payload,
        }

    @classmethod
    def detect_image(cls, file_storage) -> Dict[str, Any]:
        base_url = (current_app.config.get("IMAGE_DETECTOR_BASE_URL") or "").rstrip("/")
        if not base_url:
            raise ModelServiceError("IMAGE_DETECTOR_BASE_URL is not configured")

        timeout = int(current_app.config.get("IMAGE_DETECTOR_TIMEOUT_SECONDS", 15))
        predict_path = current_app.config.get("IMAGE_DETECTOR_PREDICT_PATH", "/predict")
        request_mode = str(current_app.config.get("IMAGE_DETECTOR_REQUEST_MODE", "auto")).lower()
        if request_mode not in {"auto", "multipart", "json_base64"}:
            request_mode = "auto"
        url = cls._join_url(base_url, predict_path)

        file_storage.stream.seek(0)
        content = file_storage.stream.read()
        file_storage.stream.seek(0)
        if not content:
            raise ModelServiceError("uploaded image is empty")

        last_error: Optional[str] = None

        # 1) multipart mode (default first)
        if request_mode in {"auto", "multipart"}:
            files = {
                "image": (
                    file_storage.filename or "upload.jpg",
                    BytesIO(content),
                    file_storage.mimetype or "application/octet-stream",
                )
            }

            try:
                response = requests.post(url, files=files, timeout=timeout)
            except requests.RequestException as exc:
                last_error = f"image detector multipart request failed: {exc}"
            else:
                if response.status_code == 200:
                    try:
                        payload = response.json()
                    except Exception as exc:
                        raise ModelServiceError("image detector response is not valid JSON") from exc

                    if not isinstance(payload, dict):
                        raise ModelServiceError("image detector response format is invalid")
                    return cls._normalize_image_detector_payload(payload, transport="multipart")

                if response.status_code in {400, 415} and request_mode == "auto":
                    # fallback to json base64 mode
                    last_error = f"multipart rejected with HTTP {response.status_code}"
                else:
                    msg = cls._extract_error_message(response)
                    raise ModelServiceError(f"image detector returned {response.status_code}: {msg}")

        # 2) json base64 mode (auto fallback or explicit)
        if request_mode in {"auto", "json_base64"}:
            image_b64 = base64.b64encode(content).decode("utf-8")
            body = {"image": image_b64}
            try:
                response = requests.post(url, json=body, timeout=timeout)
            except requests.RequestException as exc:
                prefix = f"{last_error}; " if last_error else ""
                raise ModelServiceError(f"{prefix}image detector json request failed: {exc}") from exc

            if response.status_code != 200:
                msg = cls._extract_error_message(response)
                raise ModelServiceError(f"image detector returned {response.status_code}: {msg}")

            try:
                payload = response.json()
            except Exception as exc:
                raise ModelServiceError("image detector response is not valid JSON") from exc

            if not isinstance(payload, dict):
                raise ModelServiceError("image detector response format is invalid")
            return cls._normalize_image_detector_payload(payload, transport="json_base64")

        if last_error:
            raise ModelServiceError(last_error)
        raise ModelServiceError("unsupported IMAGE_DETECTOR_REQUEST_MODE")

    @staticmethod
    def get_image_detector_status() -> Dict[str, Any]:
        base_url = (current_app.config.get("IMAGE_DETECTOR_BASE_URL") or "").rstrip("/")
        timeout = int(current_app.config.get("IMAGE_DETECTOR_TIMEOUT_SECONDS", 5))
        health_path = current_app.config.get("IMAGE_DETECTOR_HEALTH_PATH", "/health")

        if not base_url:
            return {
                "service": "image_detector",
                "status": "not_configured",
                "message": "IMAGE_DETECTOR_BASE_URL is empty",
            }

        try:
            response = requests.get(ModelService._join_url(base_url, health_path), timeout=timeout)
            if response.status_code == 200:
                payload = {}
                content_type = response.headers.get("Content-Type", "").lower()
                if "application/json" in content_type and response.content:
                    payload = response.json()
                if isinstance(payload, dict) and payload.get("status") == "ok":
                    return {"service": "image_detector", "status": "normal", "message": "ok"}
                if payload == {}:
                    return {
                        "service": "image_detector",
                        "status": "normal",
                        "message": "reachable (no standard health payload)",
                    }
                return {
                    "service": "image_detector",
                    "status": "abnormal",
                    "message": f"unexpected payload: {payload}",
                }

            if response.status_code == 404:
                # some legacy services don't expose /health, fallback to root reachability
                fallback = requests.get(ModelService._join_url(base_url, "/"), timeout=timeout)
                if fallback.status_code in {200, 302}:
                    return {
                        "service": "image_detector",
                        "status": "normal",
                        "message": "root reachable (/health not implemented)",
                    }

            return {
                "service": "image_detector",
                "status": "abnormal",
                "message": f"HTTP {response.status_code}",
            }
        except requests.RequestException as exc:
            return {"service": "image_detector", "status": "abnormal", "message": str(exc)}

    @staticmethod
    def _extract_qianfan_answer(payload: Dict[str, Any]) -> str:
        direct_candidates = ["answer", "result", "output", "content", "message"]
        for key in direct_candidates:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        data = payload.get("data")
        if isinstance(data, dict):
            for key in direct_candidates:
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        content = payload.get("content")
        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            if chunks:
                return "\n".join(chunks).strip()

        return ""

    @staticmethod
    def infer_risk_from_text(text: str) -> Tuple[str, int]:
        normalized = (text or "").lower()
        if any(flag in normalized for flag in ["高风险", "high risk"]):
            return "高", 20
        if any(flag in normalized for flag in ["中风险", "medium risk"]):
            return "中", 10
        if any(flag in normalized for flag in ["低风险", "low risk"]):
            return "低", 0
        return "未知", 0

    @staticmethod
    def _is_retryable_qianfan_failure(status_code: int, message: str) -> bool:
        if status_code in {408, 409, 424, 425, 429, 500, 502, 503, 504}:
            return True

        normalized = (message or "").lower()
        retry_keywords = [
            "qps",
            "rate limit",
            "too many requests",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "限流",
            "超出限额",
            "超时",
        ]
        return any(keyword in normalized for keyword in retry_keywords)

    @classmethod
    def ask_qianfan(
        cls,
        query: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        api_url = current_app.config.get("QIANFAN_APPBUILDER_API_URL")
        app_id = current_app.config.get("QIANFAN_APPBUILDER_APP_ID")
        token = current_app.config.get("QIANFAN_APPBUILDER_TOKEN")
        share_url = current_app.config.get("QIANFAN_APPBUILDER_SHARE_URL")

        if not api_url or not app_id or not token:
            return {
                "available": False,
                "service": "qianfan_appbuilder",
                "message": "QIANFAN_APPBUILDER_API_URL / QIANFAN_APPBUILDER_APP_ID / QIANFAN_APPBUILDER_TOKEN not configured",
                "share_url": share_url,
            }

        timeout = int(current_app.config.get("QIANFAN_TIMEOUT_SECONDS", 20))
        response_mode = current_app.config.get("QIANFAN_RESPONSE_MODE", "blocking")
        max_retries = max(0, int(current_app.config.get("QIANFAN_MAX_RETRIES", 2)))
        retry_backoff = max(0.1, float(current_app.config.get("QIANFAN_RETRY_BACKOFF_SECONDS", 1.0)))

        payload: Dict[str, Any] = {
            "app_id": app_id,
            "query": query,
            "response_mode": response_mode,
        }
        if user_id:
            payload["user_id"] = user_id
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if isinstance(inputs, dict) and inputs:
            payload["inputs"] = inputs

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        last_error: Optional[str] = None
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
            except requests.RequestException as exc:
                last_error = f"qianfan request failed: {exc}"
                if attempt < max_retries:
                    time.sleep(retry_backoff * (2**attempt))
                    continue
                raise ModelServiceError(f"{last_error} (after {attempt + 1} attempts)") from exc

            if response.status_code >= 400:
                message = cls._extract_error_message(response)
                error_text = f"qianfan returned {response.status_code}: {message}"
                last_error = error_text
                if attempt < max_retries and cls._is_retryable_qianfan_failure(response.status_code, message):
                    time.sleep(retry_backoff * (2**attempt))
                    continue
                raise ModelServiceError(f"{error_text} (after {attempt + 1} attempts)")

            try:
                data = response.json()
            except Exception as exc:
                raise ModelServiceError("qianfan response is not valid JSON") from exc

            if not isinstance(data, dict):
                raise ModelServiceError("qianfan response format is invalid")

            answer = cls._extract_qianfan_answer(data)
            inferred_level, score_delta = cls.infer_risk_from_text(answer)

            return {
                "available": True,
                "service": "qianfan_appbuilder",
                "share_url": share_url,
                "answer": answer,
                "inferred_level": inferred_level,
                "score_delta": score_delta,
                "attempts": attempt + 1,
                "raw": data,
            }

        raise ModelServiceError((last_error or "qianfan request failed") + f" (after {max_retries + 1} attempts)")

    @staticmethod
    def get_qianfan_status() -> Dict[str, Any]:
        api_url = current_app.config.get("QIANFAN_APPBUILDER_API_URL")
        app_id = current_app.config.get("QIANFAN_APPBUILDER_APP_ID")
        token = current_app.config.get("QIANFAN_APPBUILDER_TOKEN")
        share_url = current_app.config.get("QIANFAN_APPBUILDER_SHARE_URL")

        if api_url and app_id and token:
            return {
                "service": "qianfan_appbuilder",
                "status": "normal",
                "message": "configured",
                "share_url": share_url,
            }

        return {
            "service": "qianfan_appbuilder",
            "status": "not_configured",
            "message": "missing API url/app_id/token",
            "share_url": share_url,
        }

    @classmethod
    def get_model_status_summary(cls) -> Dict[str, Any]:
        image_status = cls.get_image_detector_status()
        qianfan_status = cls.get_qianfan_status()

        services = [image_status, qianfan_status]
        if any(s.get("status") == "abnormal" for s in services):
            overall = "abnormal"
        elif all(s.get("status") == "normal" for s in services):
            overall = "normal"
        else:
            overall = "degraded"

        return {"overall_status": overall, "services": services}

    @classmethod
    def build_qianfan_prompt(cls, payload: Dict[str, Any], reasons: list[str]) -> str:
        cleaned = {
            "user_id": payload.get("user_id"),
            "amount": payload.get("amount"),
            "category": payload.get("category"),
            "ip_address": payload.get("ip_address"),
            "device_id": payload.get("device_id"),
            "rule_reasons": reasons,
            "extra_description": payload.get("description") or payload.get("case_text"),
        }
        return (
            "请作为风控分析助手，基于以下信息给出风险判断（高/中/低）和简要理由：\n"
            + json.dumps(cleaned, ensure_ascii=False)
        )
