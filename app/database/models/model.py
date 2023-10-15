from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger

database = SQLAlchemy()


class Role(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    role_name = database.Column(
        database.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Role {self.role_name}>"


class User(database.Model):
    id = database.Column(database.String(36), primary_key=True,
                         default=lambda: str(uuid.uuid4()), unique=True)
    first_name = database.Column(database.String(50), nullable=False)
    last_name = database.Column(database.String(50), nullable=False)
    email = database.Column(database.String(255), unique=True,
                            nullable=False, index=True)  # Add index=True here
    password = database.Column(database.String(255), nullable=False)
    phone_number = database.Column(database.String(20), index=True)
    state = database.Column(database.String(100), index=True)
    address = database.Column(database.String(255), index=True)
    otps = database.relationship('OTP', backref='user', lazy='dynamic')
    role_id = database.Column(database.Integer, database.ForeignKey(
        'role.id'), nullable=False, index=True, default=6)
    role_name = database.Column(
        database.String, nullable=False, index=True, default="User")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    modified_at = database.Column(database.DateTime, default=datetime.utcnow)
    tokens = database.Column(database.Float, default=0.0, index=True)
    profile_image = database.Column(database.TEXT, default=None, index=True)
    is_email_verified = database.Column(
        database.Boolean, default=False, index=True)
    role = database.relationship('Role', backref='users')

    @classmethod
    def get_total_users_per_state(cls, state_name):
        return cls.query.filter_by(state=state_name).count()

    @classmethod
    def get_total_registered_users(cls):
        return cls.query.count()

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role_id': self.role_id,
            'role': self.role.role_name,
            "created_at": self.created_at.strftime("%A, %d %B, %Y"),
            'modified_at': self.modified_at.strftime("%A, %d %B, %Y"),
            'is_email_verified': str(self.is_email_verified),
            'tokenBalance': self.tokens,
            'profile_image': str(self.profile_image),
        }

    def __repr__(self):
        return f"<User {self.first_name} + {self.last_name}>"


def create_roles():
    roles_data = [
        {'role_name': 'Super Admin'},
        {'role_name': 'Admin'},
        {'role_name': 'Patner'},
        {'role_name': 'Trial'},
        {'role_name': 'Developer'},
        {'role_name': 'User'},
    ]

    for role_data in roles_data:
        role_name = role_data['role_name']
        role = Role.query.filter_by(role_name=role_name).first()

        if not role:
            new_role = Role(**role_data)
            database.session.add(new_role)

    database.session.commit()


class OTP(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.String(36), database.ForeignKey(
        'user.id'), nullable=False)
    email = database.Column(database.String(255), nullable=False)
    otp = database.Column(database.String(6), nullable=False)
    timestamp = database.Column(database.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<OTP for {self.email}>"

# transactions of user


class Transaction(database.Model):
    id = database.Column(database.String(36), primary_key=True,
                         default=lambda: str(uuid.uuid4()), unique=True)
    user_id = database.Column(database.String(36), database.ForeignKey(
        'user.id'), nullable=False, index=True)
    # Modify this to match the type in User
    user_first_name = database.Column(database.String(50), nullable=False)
    # Modify this to match the type in User
    user_last_name = database.Column(database.String(50), nullable=False)
    timestamp = database.Column(
        database.DateTime, default=datetime.utcnow, index=True, nullable=False)
    payment_amount = database.Column(database.Float, nullable=False)
    transaction_reference = database.Column(
        database.String(36), nullable=False)
    status = database.Column(database.Boolean, default=False, index=True)


class Services(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String, unique=True,
                           index=True, nullable=False)
    description = database.Column(
        database.String, unique=True, index=True, nullable=False)
    price = database.Column(database.Float, nullable=False)
    image = database.Column(database.String, unique=True,
                            index=True, nullable=False, default="default.jpg")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image
        }


class ServiceLogs(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.String(36), database.ForeignKey(
        'user.id'), nullable=False,  index=True)
    service_name = database.Column(database.String(36), database.ForeignKey(
        'services.name'), nullable=False, index=True)
    timestamp = database.Column(
        database.DateTime, default=datetime.utcnow, index=True, nullable=False)
    message = database.Column(database.String,
                              index=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "service_name": self.service_name,
            "timestamp": self.timestamp.strftime("%A, %d %B, %Y"),
            "message": self.message
        }


class GeneralLogs(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.String(36), database.ForeignKey(
        'user.id'), nullable=False,  index=True)
    log_type = database.Column(database.String(36), database.ForeignKey(
        'logs.name'), nullable=False, index=True)
    timestamp = database.Column(
        database.DateTime, default=datetime.utcnow, index=True, nullable=False)
    message = database.Column(database.String,
                              index=True, nullable=False)


class Logs(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(
        database.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Logs: {self.role_name}>"
