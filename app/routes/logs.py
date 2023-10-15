from flask import jsonify, Blueprint, request
from app.database.models.model import ServiceLogs
from app.database.models.model import database
from app.middleware.require_role import require_role
# from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


logs_route = Blueprint("logs", __name__, url_prefix="/api/v1/logs")


@logs_route.route("/get/all", methods=["GET"])
@jwt_required()
# @require_role(["Admin"])
def get_all_logs():
    logs = ServiceLogs.query.all()
    logs_list = []

    for log in logs:
        logs_list.append(log.to_dict())

    return jsonify(logs_list)
