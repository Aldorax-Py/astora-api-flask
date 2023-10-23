
from sqlalchemy.exc import IntegrityError  # Import IntegrityError
from app.middleware.require_role import require_role
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from dotenv import load_dotenv
from app.crud.tools.upload_image import upload_image_to_cloudinary, allowed_file
from app.crud.tools.generate_otp import generate_otp
from extensions import mail
from flask_mail import Message
from app.database.models.model import database
import os
from app.database.models.model import GeneralLog, User, OTP, UserActivityLog, ErrorLog
from flask import jsonify, Blueprint, render_template, request
import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(
    cloud_name="di7dbnwa9",
    api_key="886223283645899",
    api_secret="mxPv-VTh8V4viM4nqmxJDQjzXvc"
)

load_dotenv()

auth_route = Blueprint("auth", __name__, url_prefix="/api/v1/authentication")


def upload_image_to_cloudinary(image, name):
    # Upload the image to Cloudinary
    result = cloudinary.uploader.upload(
        image, public_id=name
    )
    image_url = result['url']

    return image_url


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
    profile_image = request.files.get('profile_image', None)

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

    try:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=password,
            state=state,
            address=address
        )

        if profile_image:
            profile_image_url = upload_image_to_cloudinary(
                profile_image, new_user.last_name)
            new_user.profile_image = profile_image_url

        otp = generate_otp()
        new_otp = OTP(user=new_user, email=new_user.email, otp=otp)

        send_email(new_user.email, new_user.first_name, otp)

        database.session.add(new_user)
        database.session.add(new_otp)
        database.session.commit()

        try:
            new_register_Activity = UserActivityLog(
                user_id=new_user.id,
                activity_type="Registration",
                description=f"{new_user.first_name} {new_user.last_name} registered thier account successfully"
            )
            
            database.session.add(new_register_Activity)
            database.session.commit()

            return jsonify(message="User created successfully."), 200

        except:
            return jsonify(message="User created successfully."), 200

        # try:
        #     new_general_log = GeneralLog(
        #         user_id=new_user.id,
        #         message=f"{new_user.first_name} {new_user.last_name} created an account"
        #     )

        #     database.session.add(new_general_log)
        #     database.session.commit()

        # except:
        #     return jsonify(message="User created successfully."), 200

        # return jsonify(message="User created successfully."), 200
    except IntegrityError as e:
        return jsonify(message="Failed to create the account. Please try again.", error=str(e)), 500
    except Exception as e:
        return jsonify(message="Failed to create the account. Please try again.", error=str(e)), 500


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

    if not user.is_email_verified:
        return jsonify(message="You have not verified your account. Please verify your account to get access to your dashboard.")

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


@auth_route.route("/resend-otp", methods=["POST"])
@jwt_required()
def resend_otp():
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify(message='User not found'), 404

        if user.is_email_verified:
            return jsonify(message='Your email is already verified'), 200

        otp = generate_otp()  # Generate a new OTP

        # Update the OTP in the database
        otp_entry = OTP.query.filter_by(user_id=user_id, email=user.email).first()
        if not otp_entry:
            otp_entry = OTP(user=user, email=user.email, otp=otp)
            database.session.add(otp_entry)
        else:
            otp_entry.otp = otp

        # Commit the changes to the database
        database.session.commit()

        # Resend the OTP to the user's email
        send_email(user.email, user.first_name, otp)

        return jsonify(message='OTP resent successfully'), 200

    except KeyError:
        return jsonify(message='Invalid JWT token'), 401
    except Exception as e:
        database.session.rollback()
        print("Error during OTP resend:", str(e))
        return jsonify(message='Failed to resend OTP. Please try again later.'), 500


users = [
    {
        "id": "1", 
        "name": "John Doe", 
        "role": "Engineer", 
        "status": "Active", 
        "transaction_id": "1001", 
        "date_of_payment": "2023-10-25", 
        "payment_status": "Paid", 
        "payment_plan": "Basic", 
        "expiring_date": "2024-10-25", 
        "download_receipt": "receipt001.pdf"
    },
    {"id": "2", "name": "Alice Smith", "role": "Manager", "status": "Paused", "transaction_id": "1002", "date_of_payment": "2023-09-15", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2024-09-15", "download_receipt": "receipt002.pdf"},
    {"id": "3", "name": "Bob Johnson", "role": "Developer", "status": "Active", "transaction_id": "1003", "date_of_payment": "2023-11-05", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2024-11-05", "download_receipt": "receipt003.pdf"},
    {"id": "4", "name": "Emily Brown", "role": "Manager", "status": "Active", "transaction_id": "1004", "date_of_payment": "2023-08-17", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2024-08-17", "download_receipt": "receipt004.pdf"},
    {"id": "5", "name": "Daniel Wilson", "role": "Engineer", "status": "Paused", "transaction_id": "1005", "date_of_payment": "2023-07-29", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2024-07-29", "download_receipt": "receipt005.pdf"},
    {"id": "6", "name": "Grace Davis", "role": "Developer", "status": "Active", "transaction_id": "1006", "date_of_payment": "2023-06-14", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2024-06-14", "download_receipt": "receipt006.pdf"},
    {"id": "7", "name": "Mia Hernandez", "role": "Engineer", "status": "Active", "transaction_id": "1007", "date_of_payment": "2023-05-19", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2024-05-19", "download_receipt": "receipt007.pdf"},
    {"id": "8", "name": "Sophia Nguyen", "role": "Manager", "status": "Active", "transaction_id": "1008", "date_of_payment": "2023-04-01", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2024-04-01", "download_receipt": "receipt008.pdf"},
    {"id": "9", "name": "Oliver Lee", "role": "Developer", "status": "Active", "transaction_id": "1009", "date_of_payment": "2023-12-10", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2024-12-10", "download_receipt": "receipt009.pdf"},
    {"id": "10", "name": "Liam Hall", "role": "Engineer", "status": "Paused", "transaction_id": "1010", "date_of_payment": "2023-03-07", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2024-03-07", "download_receipt": "receipt010.pdf"},
    {"id": "11", "name": "Ella Clark", "role": "Manager", "status": "Active", "transaction_id": "1011", "date_of_payment": "2023-02-28", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2024-02-28", "download_receipt": "receipt011.pdf"},
    {"id": "12", "name": "James King", "role": "Developer", "status": "Active", "transaction_id": "1012", "date_of_payment": "2023-01-15", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2024-01-15", "download_receipt": "receipt012.pdf"},
    {"id": "13", "name": "Ava Baker", "role": "Engineer", "status": "Active", "transaction_id": "1013", "date_of_payment": "2022-12-05", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2023-12-05", "download_receipt": "receipt013.pdf"},
    {"id": "14", "name": "Lucas Garcia", "role": "Manager", "status": "Active", "transaction_id": "1014", "date_of_payment": "2022-11-20", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2023-11-20", "download_receipt": "receipt014.pdf"},
    {"id": "15", "name": "Emma Smith", "role": "Developer", "status": "Active", "transaction_id": "1015", "date_of_payment": "2022-10-11", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2023-10-11", "download_receipt": "receipt015.pdf"},
    {"id": "16", "name": "Henry Turner", "role": "Engineer", "status": "Paused", "transaction_id": "1016", "date_of_payment": "2022-09-07", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2023-09-07", "download_receipt": "receipt016.pdf"},
    {"id": "17", "name": "Charlotte White", "role": "Manager", "status": "Active", "transaction_id": "1017", "date_of_payment": "2022-08-22", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2023-08-22", "download_receipt": "receipt017.pdf"},
    {"id": "18", "name": "Jackson Thomas", "role": "Developer", "status": "Active", "transaction_id": "1018", "date_of_payment": "2022-07-30", "payment_status": "Paid", "payment_plan": "Standard", "expiring_date": "2023-07-30", "download_receipt": "receipt018.pdf"},
    {"id": "19", "name": "Avery Davis", "role": "Engineer", "status": "Active", "transaction_id": "1019", "date_of_payment": "2022-06-14", "payment_status": "Paid", "payment_plan": "Basic", "expiring_date": "2023-06-14", "download_receipt": "receipt019.pdf"},
    {"id": "20", "name": "Evelyn Scott", "role": "Manager", "status": "Active", "transaction_id": "1020", "date_of_payment": "2022-05-29", "payment_status": "Paid", "payment_plan": "Premium", "expiring_date": "2023-05-29", "download_receipt": "receipt020.pdf"}
]


"""
1 - ID
2 - Transaction ID
3 - Date of payment
4 - Payment status
5 - Payment Plan
6 - Expiring date
7 - Download reciept
"""

@auth_route.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)