# Routes to create, edit, delete and use services
# Refrence to the service table in the app.database.models.model.py

from flask import jsonify, Blueprint, request
from app.database.models.model import Services
from app.database.models.model import database
from flask_jwt_extended import jwt_required


# Only admins can make the services, edit and delete them.
# The other users can only view the services

services_route = Blueprint("services", __name__, url_prefix="/api/v1/services")


@services_route.route("/create", methods=["POST"])
@jwt_required()
def create_service():
    service_data = request.form.to_dict()

    if service_data is None:
        return jsonify(message="There is not data in the form submited. Please input data and try again.")

    name = service_data.get("name")
    description = service_data.get("description")
    price = service_data.get("price")
    image = service_data.get("image")

    if not all([name, description, price, image]):
        return jsonify(message="Please fill all the required fields and try again.")

    service = Services.query.filter_by(name=name).first()

    if service:
        return jsonify(message="Service already exist. Please edit or create a new service.")

    new_service = Services(
        name=name,
        description=description,
        price=price,
        image=image
    )

    database.session.add(new_service)
    database.session.commit()

    return jsonify(message="Service created successfully.")


# Get all services
@services_route.route("/all", methods=["GET"])
def get_all_services():
    services = Services.query.all()
    services_list = []

    for service in services:
        services_list.append(service.to_dict())

    return jsonify(services_list)


# Get a particualr service
@services_route.route("details/<service_id>", methods=["GET"])
def get_service(service_id):
    service = Services.query.filter_by(id=service_id).first()

    if not service:
        return jsonify(message="Service does not exist.")

    return jsonify(service.to_dict())
