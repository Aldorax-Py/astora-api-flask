from flask import jsonify, Blueprint, request
from app.database.models.model import ServiceLog, GeneralLog, TransactionLog, ErrorLog, UserActivityLog
from app.database.models.model import database
from app.middleware.require_role import require_role
# from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


logs_route = Blueprint("log", __name__, url_prefix="/api/v1/log")


@logs_route.route("/get/service/all", methods=["GET"])
@jwt_required()
# @require_role(["Admin"])  # Uncomment this line if you want to require a specific role
def get_service_log():
    logs = ServiceLog.query.all()
    log_list = [log.to_dict() for log in logs]
    return jsonify(log_list)


@logs_route.route("/get/transactions/all", methods=["GET"])
@jwt_required()
# @require_role(["Admin"])  # Uncomment this line if you want to require a specific role
def get_transactions_log():
    logs = TransactionLog.query.all()
    log_list = [log.to_dict() for log in logs]
    return jsonify(log_list)


@logs_route.route("/get/general/all", methods=["GET"])
@jwt_required()
def get_general_log():
    logs = GeneralLog.query.all()
    log_list = [log.to_dict() for log in logs]

    print(log_list)  # Add this line for debugging

    return jsonify(log_list)


@logs_route.route("/get/useractivity/all", methods=["GET"])
@jwt_required()
def get_useractivity_log():
    logs = UserActivityLog.query.all()
    log_list = [log.to_dict() for log in logs]

    print(log_list)  # Add this line for debugging

    return jsonify(log_list)


@logs_route.route("/get/error/all", methods=["GET"])
@jwt_required()
# @require_role(["Admin"])  # Uncomment this line if you want to require a specific role
def get_error_log():
    logs = ErrorLog.query.all()
    log_list = [log.to_dict() for log in logs]
    return jsonify(log_list)
