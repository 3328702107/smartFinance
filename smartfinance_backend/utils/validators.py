# 数据验证器
from core.exceptions import ValidationError


def validate_required(data, *fields):
    """验证必填字段"""
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_email(email):
    """验证邮箱格式"""
    import re
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValidationError("Invalid email format")


def validate_phone(phone):
    """验证手机号格式"""
    import re
    if phone and not re.match(r'^1[3-9]\d{9}$', phone):
        raise ValidationError("Invalid phone format")
