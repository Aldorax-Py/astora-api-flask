from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.database.models.model import User


def require_role(role):
    def decorator(func):
        @wraps(func)  # Use wraps to preserve the original function's metadata
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user or user.role_name not in role:
                return jsonify(message='Insufficient permissions'), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
