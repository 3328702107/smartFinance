# blueprints/users.py
from flask import Blueprint, request, jsonify
from models import User, LoginLog
bp = Blueprint("users", __name__, url_prefix="/api/users")

@bp.get("/")
def list_users():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    q = request.args.get("q")

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(User.username.like(like))
    pagination = query.paginate(page=page, per_page=size, error_out=False)

    return jsonify({
        "items": [
            {"user_id": u.user_id, "username": u.username, "status": u.status, "account_level": u.account_level}
            for u in pagination.items
        ],
        "page": page,
        "size": size,
        "total": pagination.total
    })


@bp.get("/<user_id>/login_logs")
def user_login_logs(user_id):
    logs = LoginLog.query.filter_by(user_id=user_id).order_by(LoginLog.login_time.desc()).limit(50).all()
    def _dt(v): return v.isoformat() if v else None
    return jsonify([
        {
            "log_id": l.log_id,
            "login_time": _dt(l.login_time),
            "ip_address": l.ip_address,
            "login_status": l.login_status,
            "login_location": l.login_location,
            "client_type": l.client_type
        } for l in logs
    ])