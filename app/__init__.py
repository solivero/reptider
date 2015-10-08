from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from .utils import ListConverter
from sys import stdout
import logging

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.url_map.converters['list'] = ListConverter

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
out = logging.StreamHandler(stdout)
out.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
out.setFormatter(formatter)
log.addHandler(out)

import views, models

db.create_all()
