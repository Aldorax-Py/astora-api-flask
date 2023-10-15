import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, Flask

app = Flask(__name__)


def send():
    # Set up your SMTP server connection details
    smtp_server = "smtp.elasticemail.com"
    smtp_port = 2525  # or 465 for SSL
    smtp_username = "contact@astora.finance"
    smtp_password = "6116F3C70A2DF75A7FC08B351B07D519730B"

    # Set up your email details
    from_address = "contact@astora.finance"
    to_address = "climaxating@gmail.com"
    subject = "Hello from Python"

    # HTML body of the email
    html_body = render_template('test.html')

    # Create a MIME multipart message
    msg = MIMEMultipart("alternative")
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Attach the HTML body to the message
    msg.attach(MIMEText(html_body, 'html'))

    # Connect to the server, login, and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()


send

if __name__ == "__main__":
    app.run()
