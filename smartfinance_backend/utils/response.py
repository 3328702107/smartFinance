# 响应工具函数（原 api_utils.py）
from time import time
from flask import jsonify


def api_response(data=None, code: int = 200, message: str = "success"):
    """
    统一响应包装

    Args:
        data: 响应数据
        code: 状态码，默认 200
        message: ���应消息，默认 "success"

    Returns:
        JSON 响应
    """
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(time() * 1000),
        }
    )


def paginated_response(items, total: int, page: int, page_size: int, code: int = 200, message: str = "success"):
    """
    分页响应包装

    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        code: 状态码，默认 200
        message: 响应消息，默认 "success"

    Returns:
        JSON 响应
    """
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
