from flask import jsonify, Blueprint, render_template, request
import requests
from app.database.models.model import User, OTP, Logs, Transaction
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


@payment_route.route("/purchase-token", methods=["POST"])
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


@payment_route.route('/verify_payment', methods=['POST'])
def verify_payment():
    squad_api_key = "sandbox_sk_155f0280a804a1a1541f08eaba7abd38f2912b8237b0"
    try:
        # Get the 'reference' parameter from the URL
        reference = request.args.get('reference')

        if not reference:
            return jsonify({'error': 'Reference parameter is missing'}), 400

        # Define the Squad API endpoint for transaction verification
        api_endpoint = f"https://sandbox-api-d.squadco.com/transaction/verify/{reference}"

        # Set up the headers with the API key for authentication
        headers = {
            'Authorization': f'Bearer {squad_api_key}'
        }

        # Make a GET request to verify the transaction
        response = requests.get(api_endpoint, headers=headers)

        response_data = response.json()
        amount = response_data.get('data', {}).get('transaction_amount')

        if response.status_code == 200:
            # Update the payment status in the database
            transaction = Transaction.query.filter_by(
                transaction_reference=reference).first()

            if transaction:
                user_id = transaction.user_id
                print(user_id)
                user = User.query.filter_by(id=user_id).first()
                transaction.status = True
                user.tokens = float(amount)
                database.session.commit()

                # Respond with a success message
                return jsonify({'message': 'Payment verified and status updated successfully'})
            else:
                return jsonify(message="No transaction like this")

        # Respond with an error message if verification fails
        return jsonify({'error': 'Transaction verification failed'}), 400

    except Exception as e:
        # Handle any exceptions that may occur during the verification process
        print("Transaction verification error:", str(e))
        return jsonify({'error': 'Transaction verification error'}), 500
