from flask import jsonify, Blueprint, render_template, request
import requests
from app.database.models.model import User, OTP, Transaction
import os
from app.database.models.model import database
from flask_mail import Message
from extensions import mail

from dotenv import load_dotenv
from flask_jwt_extended import get_jwt_identity, jwt_required
import random
import string
load_dotenv()

payment_route = Blueprint("payment", __name__, url_prefix="/api/v1/payment")


def generate_transaction_Ref():
    # Generate a random string of 6 characters (upper case letters and digits)
    letters_and_digits = string.ascii_uppercase + string.digits
    while True:
        Transaction_Ref = ''.join(random.choices(letters_and_digits, k=10))
        # Check if the referral code already exists in the database
        existing_user = Transaction.query.filter_by(
            transaction_reference=Transaction_Ref).first()
        if not existing_user:
            break
    return Transaction_Ref


@payment_route.route("/purchase-token", methods=["GET"])
@jwt_required()
def initialize_purchase():

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    api_endpoint = "https://sandbox-api-d.squadco.com/transaction/initiate"
    api_key = "sandbox_sk_155f0280a804a1a1541f08eaba7abd38f2912b8237b0"

    new_TX_REF = generate_transaction_Ref()
    print(new_TX_REF)

    payment_data = {
        "amount": 500000,
        "email": user.email,
        "currency": "NGN",
        "initiate_type": "inline",
        "transaction_ref": f"{new_TX_REF}",
        "customer_name": f"{user.first_name} {user.last_name}",
        "callback_url": "http://squadco.com",
        "pass_charge": True,
        "callback_url": "http://localhost:5000/api/v1/payment/verify_payment"
    }

    # Set up the headers with the API key
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Make a POST request to initiate the payment
        response = requests.post(
            api_endpoint, json=payment_data, headers=headers)

        # Check the response status code
        if response.status_code == 200:
            # Payment initiation successful, parse the response JSON
            response_data = response.json()

            merchant_info = response_data.get(
                "data", {}).get("merchant_info", {})
            merchant_id = merchant_info.get("merchant_id")
            currency = response_data.get("data", {}).get("currency")
            transaction_ref = response_data.get(
                "data", {}).get("transaction_ref")
            transaction_amount = response_data.get(
                "data", {}).get("transaction_amount")
            authorized_channels = response_data.get(
                "data", {}).get("authorized_channels")
            checkout_url = response_data.get("data", {}).get("checkout_url")

            # Create a structured response dictionary
            response_data = {
                "merchant_id": merchant_id,
                "currency": currency,
                "transaction_ref": transaction_ref,
                "transaction_amount": transaction_amount,
                "authorized_channels": authorized_channels,
                "checkout_url": checkout_url
            }

            return jsonify(response=response_data)

        else:
            response_data = response.json()
            return jsonify(response=response_data)

    except Exception as e:
        # Handle any exceptions that may occur during the request
        print("Payment initiation failed:", str(e))


@payment_route.route('/verify_payment', methods=['GET'])
def verify_payment():
    SQUAD_SECRET_KEY = "sandbox_sk_155f0280a804a1a1541f08eaba7abd38f2912b8237b0"
    transaction_ref = request.args.get('reference')

    if not transaction_ref:
        return jsonify({'message': 'Transaction reference is missing'}), 400

    # Define the Squad API endpoint for verifying a transaction
    squad_api_url = f'https://sandbox-api-d.squadco.com/transaction/verify/{transaction_ref}'

    # Set up the headers with the Authorization key
    headers = {'Authorization': f'Bearer {SQUAD_SECRET_KEY}'}

    # Send a GET request to Squad's API for transaction verification
    response = requests.get(squad_api_url, headers=headers)

    if response.status_code == 200:
        # Transaction is valid, process the response data
        response_data = response.json()

        transaction_data = response_data.get("data", {})

        # Check the email and amount in response_data and confirm the payment
        email = transaction_data.get("email")
        payment_amount = transaction_data.get("transaction_amount")

        # Check the email and amount to confirm the payment
        if email and payment_amount:
            # Find the user with the given email
            user = User.query.filter_by(email=email).first()

            if user:
                # Calculate the number of tokens based on the payment amount (e.g., multiplying by 10)
                tokens = payment_amount * 10

                # Update the user's token balance
                user.tokens += tokens

                # Create a new transaction record
                transaction = Transaction(
                    user_id=user.id,
                    user_first_name=user.first_name,
                    user_last_name=user.last_name,
                    payment_amount=payment_amount,
                    transaction_reference=transaction_ref,
                    status=True  # Set status to True to indicate a successful transaction
                )

                # Commit changes to the database
                database.session.add(transaction)
                database.session.commit()

                # Return a response confirming the payment
                response_message = {
                    'message': 'Payment confirmed',
                    'tokens_earned': tokens
                }
                return jsonify(response_message), 200
            else:
                return jsonify({'message': 'User not found'}), 400
        else:
            return jsonify({'message': 'Missing email or payment amount in response data'}), 400

    elif response.status_code == 400:
        # Invalid transaction reference
        return jsonify({'message': 'Invalid transaction reference'}), 400
    else:
        # Handle other status codes as needed
        return jsonify({'message': 'Transaction verification failed'}), 500

