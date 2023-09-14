###########################
###########################
# Developer: Aldorax
# Lead developer.
###########################
###########################
import os
import redis
from sqlalchemy import create_engine


class ApplicationConfig:

    # Initialize the redis client for in memory storage on the local machine
    redis_client = redis.Redis()

    # We need to define the redis url to for the storage. Can be local Machine or 3rd party solution
    # In this case we will use both. Local for testing and Hosted for prodcution deployment

    # For the Local
    SESSION_REDIS = redis_client

    # For the Hosted server
    # REDIS_URL = ""
    # SESSION_REDIS = redis.from_url(REDIS_URL)

    # We need to set the redis as the session type so we can actually use it in our application
    SESSION_TYPE = "redis"

    SECRET_KEY = os.environ.get("SECRET_KEY")
    # We need to configure some settings for our session
    SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX")
    SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT")
    SESSION_USE_SIGNER = os.environ.get("SESSION_USE_SIGNER")
    PERMANENT_SESSION_LIFETIME = 86400

    # We need to initialize our database
    # For development, we will use sqlite and for Production, we will use postgresSql

    # For development
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    # For Production
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:oXMY8Lu55hbeyGFDYI2w@containers-us-west-168.railway.app:6965/railway"

    # We need to configure our sqlalchemy to function better
    # We want to get the logs from our changes and whatever sqlalchemy does when interacting with out db and models
    # We also want to optimize database pooling
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS")
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_TIMEOUT = 3000
    SQLALCHEMY_POOL_RECYCLE = 36000

    # Now we initialize the database
    DATABASE_ENGINE = create_engine(SQLALCHEMY_DATABASE_URI)

    # Lets work on our email settings
    MAIL_SERVER = 'smtp.elasticemail.com'
    MAIL_PORT = 2525
    MAIL_USERNAME = 'support@enetworksagencybanking.com.ng'
    MAIL_PASSWORD = "A2CDE2AB8EEE085BBF14DFF4D75315C7BF75"
    MAIL_USE_TLS = True

    # We need to also customize our Jwt Expiration time for our access tokens.
    JWT_ACCESS_TOKEN_EXPIRES = 43200
