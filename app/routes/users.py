from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.require_role import require_role
from app.database.models.model import User, Services, database, ServiceLogs, Transaction
import random


def create_random_TRX_REF():
    return ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))


users_route = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_route.route("/<service_id>/use", methods=["GET"])
@jwt_required()
@require_role(["User"])
def get_users(service_id):
    user_id = get_jwt_identity()
    service = Services.query.filter_by(id=service_id).first()
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify(message="User does not exist.")

    if service is None:
        return jsonify(message="Service does not exist.")

    if service:
        if user.tokens < service.price:
            return jsonify(message="You do not have enough tokens to use this services. Please purchase tokens to be able to.", tokens=user.tokens, price=service.price)

        user.tokens -= service.price
        database.session.commit()

        # If transaction is successful, create the tansaction and then update the services logs.
        new_transaction = Transaction(
            user_id=user.id,
            user_first_name=user.first_name,
            user_last_name=user.last_name,
            payment_amount=service.price,
            transaction_reference="1234567890",
            status=True
        )

        new_service_log = ServiceLogs(
            user_id=user.id,
            service_name=service.name,
            message=log_messgae
        )

        database.session.add(new_transaction)
        database.session.commit()
        database.session.add(new_service_log)
        database.session.commit()

        log_messgae = f"User {user.first_name} {user.last_name} used the service: {service.name}. User paid {service.price} successfully."

        return jsonify(message=f"{user.first_name} {user.last_name} has used {service.name}")
    else:
        return jsonify(message=f"{user.first_name} {user.last_name} is logged in")


@users_route.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@require_role(["User"])
def get_user(user_id):
    # Your route logic here
    return jsonify({"message": f"Get user with ID {user_id}"})


@users_route.route("/tokens", methods=["POST"])
@jwt_required()
@require_role(["User"])
def give_tokens():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify(message="User does not exist.")

    user.tokens += 10000
    database.session.commit()

    return jsonify(message=f"{user.first_name} {user.last_name} has been given 10 tokens.", tokens=user.tokens)
