from flask import jsonify, Blueprint

users_route = Blueprint("users", __name__, url_prefix="/api/v1/tools")


@users_route.route("/users", methods=["GET"])
def get_users():
    # Your route logic here
    return jsonify({"message": "Get all users"})


@users_route.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # Your route logic here
    return jsonify({"message": f"Get user with ID {user_id}"})
