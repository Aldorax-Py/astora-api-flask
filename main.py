# import bugsnag
# from bugsnag.flask import handle_exceptions
# import rollbar
# import rollbar.contrib.flask
import logging
import os
from app.routes.users import users_route
from app.routes.payments import payment_route
from app.routes.auth import auth_route
from app.routes.services import services_route
from app.routes.admin import admin_route
from app.routes.logs import logs_route
from flask import Flask, jsonify, render_template, send_from_directory, session, got_request_exception
from flask_cors import CORS
from flask_migrate import Migrate
# from flask_mail import Mail, Message
from extensions import mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from functools import wraps
from flask_session import Session
from app.config.appConfig import ApplicationConfig
from app.database.models.model import create_roles, database
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init(
#     dsn="https://8eae96c2db96407cb930292e127e8016@app.glitchtip.com/4661",
#     integrations=[FlaskIntegration()]
# )

# bugsnag.configure(
#     api_key="fffa9b0062e8730783f89e0182bb1593",
#     project_root="./astora-api-flask",
# )

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.elasticemail.com',
    MAIL_PORT=2525,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='contact@astora.finance',
    MAIL_PASSWORD='6116F3C70A2DF75A7FC08B351B07D519730B'
)
app.config.from_object(ApplicationConfig)
# handle_exceptions(app)
CORS(app, allow_headers=True, supports_credentials=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail.init_app(app)
migrate = Migrate(app, database)
server_session = Session(app)
database.init_app(app)
# with app.app_context():
#     database.drop_all()
#     database.create_all()
#     create_roles()

# Import and register the blueprint without circular import
app.register_blueprint(users_route)
app.register_blueprint(auth_route)
app.register_blueprint(services_route)
app.register_blueprint(admin_route)
app.register_blueprint(logs_route)
app.register_blueprint(payment_route)


# with app.app_context():
#     rollbar.init('7002fa8f3a9948f7bd53ba11bca07fdb', environment='development')
#     # send exceptions from `app` to rollbar, using flask's signal system.
#     got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.after_request
def add_cors_headers(response):
    # Replace with your frontend domain
    # frontend_domain = 'http://localhost:3000'
    frontend_domain = 'https://www.astorafinance.com'
    response.headers['Access-Control-Allow-Origin'] = frontend_domain
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


@app.route('/debug-glitchtip')
def trigger_error():
    division_by_zero = 1 / 0


@app.route('/notify')
def notify():
    return jsonify(message="Notified")


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, threaded=True)
