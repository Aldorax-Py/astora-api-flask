from flask import jsonify, Blueprint, request
from app.database.models.model import User
from app.database.models.model import database
# from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


auth_route = Blueprint("auth", __name__, url_prefix="/api/v1/authentication")


@auth_route.route("/register", methods=["POST"])
def create_user():
    user_data = request.form.to_dict()

    if user_data is None:
        return jsonify(message="There is not data in the form submited. Please input data and try again.")

    first_name = user_data.get("first_name")
    last_name = user_data.get("last_name")
    email = user_data.get("email")
    phone_number = user_data.get("phone_number")
    password = user_data.get("password")
    state = user_data.get("state")
    address = user_data.get("address")

    if not all([first_name, last_name, email, phone_number, password, state, address]):
        return jsonify(message="Please fill all the required fields and try again.")

    user = User.query.filter_by(email=email).first()
    user_phone = User.query.filter_by(phone_number=phone_number).first()

    if user:
        return jsonify(message="User already exist. Please login.")

    if user_phone:
        return jsonify(message="Phone number already exist. Please login.")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        password=password,
        state=state,
        address=address,
    )

    database.session.add(new_user)
    database.session.commit()

    return jsonify(message="User created successfully.")


@auth_route.route("/login", methods=["POST"])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return jsonify(message="User does not exist. Please register.")

    access_token = create_access_token(identity=user.id)

    return jsonify(message="Login successful.", access_token=access_token)


# Dashboar route
@auth_route.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify(message="User does not exist. Please register.")

    data = user.to_dict()

    return jsonify(data)


@auth_route.route("/all", methods=["GET"])
def get_all_users():
    users = User.query.all()
    user_list = []

    for user in users:
        user_list.append(user.to_dict())

    return jsonify(user_list)


@auth_route.route("/logout", methods=["POST"])
def logout():
    return jsonify(message="Logout successful.")
