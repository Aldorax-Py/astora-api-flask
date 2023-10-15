from flask import jsonify, Blueprint, render_template, request
from app.database.models.model import User, OTP, Logs
import os
from app.database.models.model import database
from flask_mail import Message
from extensions import mail
from app.crud.tools.generate_otp import generate_otp
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.middleware.require_role import require_role

load_dotenv()

auth_route = Blueprint("auth", __name__, url_prefix="/api/v1/authentication")


def send_email(user_email, user_name, otp, **kwargs):
    # Load the email template
    html_template = render_template(
        'test.html', user_name=user_name, user_email=user_email, otp=otp, **kwargs)

    subject = "Astora Email Verification"

    # Create the email message
    msg = Message(subject, sender='contact@astora.finance',
                  recipients=[user_email])
    msg.html = html_template   # Set the HTML content of the email

    try:
        mail.send(msg)
        return jsonify(message="Email sent!")
    except:
        return jsonify(message="Email not sent!")


@auth_route.route("/register", methods=["POST"])
def create_user():
    user_data = request.form.to_dict()

    if user_data is None:
        print("There is not data in the form submitted. Please input data and try again.")
        return jsonify(message="There is not data in the form submitted. Please input data and try again.")

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
        print("User already exists. Please login.")
        return jsonify(message="User already exists. Please login.")

    if user_phone:
        print("Phone number already exists. Please login.")
        return jsonify(message="Phone number already exists. Please login.")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        password=password,
        state=state,
        address=address,
    )

    otp = generate_otp()
    new_otp = OTP(user=new_user, email=new_user.email, otp=otp)

    send_email(new_user.email, new_user.first_name, otp)

    database.session.add(new_user)
    database.session.add(new_otp)
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
@auth_route.route("/verify-email", methods=["POST"])
@jwt_required()
def verify_email():
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify(message='User not found'), 404

        data = request.form
        email_verification_otp = data.get('otp')
        email = user.email

        if not email_verification_otp or not email:
            return jsonify(message='OTP and email fields are required'), 400

        # Get the OTP from the OTP table based on the user's email
        otp_entry = OTP.query.filter_by(user_id=user_id, email=email).first()

        if not otp_entry:
            return jsonify(message='OTP entry not found'), 404

        stored_otp = otp_entry.otp

        if stored_otp != email_verification_otp:
            return jsonify(message='Invalid OTP'), 401

        if user.is_email_verified:
            return jsonify(message="You have already verified your email"), 200

        # Mark the user's email as verified
        user.is_email_verified = True
        database.session.commit()

        # Remove the OTP entry from the OTP table after successful verification
        database.session.delete(otp_entry)
        database.session.commit()

        return jsonify(message='Email verified successfully'), 200

    except KeyError:
        return jsonify(message='Invalid JWT token'), 401
    except Exception as e:
        database.session.rollback()
        print("Error during email verification:", str(e))
        return jsonify(message='Failed to verify email. Please try again later.'), 500


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


@auth_route.route("/tokens", methods=["POST"])
@jwt_required()
@require_role(["User"])
def give_tokens():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify(message="User does not exist.")

    tokens = 10000

    user.tokens += tokens
    database.session.commit()

    return jsonify(message=f"{user.first_name} {user.last_name} has been given {tokens} tokens.", tokens=user.tokens)


#################
#################
#################

@auth_route.route('/send_email', methods=["POST"])
def send_email_email():
    # Load the email template
    html_template = render_template('test.html')

    subject = "Astora Email Verification"

    # Create the email message
    msg = Message(subject, sender='contact@astora.finance',
                  recipients=['legadax@outlook.com'])
    msg.html = html_template  # Set the HTML content of the email

    # Send the email
    mail.send(msg)

    return jsonify(message="Email sent!")
