from app.routes.users import users_route
from app.routes.auth import auth_route
from app.routes.services import services_route
from app.routes.admin import admin_route
from app.routes.logs import logs_route
from flask import Flask, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from functools import wraps
from flask_session import Session
from app.config.appConfig import ApplicationConfig
from app.database.models.model import create_roles, database

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app, allow_headers=True, supports_credentials=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
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


@app.after_request
def add_cors_headers(response):
    # Replace with your frontend domain
    frontend_domain = 'https://www.enetworksagencybanking.com.ng'
    response.headers['Access-Control-Allow-Origin'] = frontend_domain
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == "__main__":
    app.run(debug=True)
