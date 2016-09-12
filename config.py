import os

SRF_ENABLED = True
SECRET_KEY = "bladiblah"
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
DEBUG = True
