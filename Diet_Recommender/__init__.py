import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import babel
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '12345sjndfjsndinc@#$%'
basedir = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(basedir, 'static/images')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = 'http://localhost:5000/login'
login_manager.init_app(app)

from Diet_Recommender.Information.views import Information
from Diet_Recommender.Recommender.views import Recommender
from Diet_Recommender.Authentication.views import Authentication

app.register_blueprint(Authentication, url_prefix='/')
app.register_blueprint(Recommender, url_prefix='/')
app.register_blueprint(Information, url_prefix='/')
