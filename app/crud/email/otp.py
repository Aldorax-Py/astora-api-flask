from flask import render_template, jsonify
from extensions import mail
from flask_mail import Message


def send_email(user):
    # Load the email template
    html_template = render_template('test.html')

    subject = "Astora Email Verification"

    # Create the email message
    msg = Message(subject, sender='contact@astora.finance',
                  recipients=user)
    msg.html = html_template  # Set the HTML content of the email

    # Send the email
    mail.send(msg)

    return jsonify(message="Email sent!")
