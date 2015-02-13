from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from .utils import ListConverter

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.url_map.converters['list'] = ListConverter

import views, models

db.create_all()
