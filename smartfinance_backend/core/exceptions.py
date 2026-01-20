# 自定义异常


class AppError(Exception):
    """应用基础异常"""
    pass


class ValidationError(AppError):
    """数据验证异常"""
    pass


class NotFoundError(AppError):
    """资源不存在异常"""
    pass


class BusinessError(AppError):
    """业务逻辑异常"""
    pass
