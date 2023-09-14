# This middleware will require a role to access all pages using the jwt_Extended
from main import jsonify
from main import wraps
# from flask_jwt_extended import get_jwt_identity
from main import get_jwt_identity
from app.database.models.model import User


def require_role(role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            user_role = User.query.filter_by(id=user).first()
            if not user or user.role.role_name not in role:
                return jsonify(message='Insufficient permissions'), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
