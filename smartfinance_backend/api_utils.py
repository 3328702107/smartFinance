from time import time
from flask import jsonify


def api_response(data=None, code: int = 200, message: str = "success"):
    """统一响应包装：{code, message, data, timestamp}."""
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(time() * 1000),
        }
    )


def paginated_response(items, total: int, page: int, page_size: int, code: int = 200, message: str = "success"):
    return api_response(
        data={
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
        },
        code=code,
        message=message,
    )
