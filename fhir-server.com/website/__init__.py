#from sqlite3 import connect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
import psycopg2
from psycopg2 import Error

#import mysql.connector

db = SQLAlchemy()
# DB_NAME = "database.db"
DB_NAME = "fhir"
DB_USERNAME = "postgres"
# DB_PASS = os.environ.get('DB_PASSWORD')

DB_PASS = "1123581321"

def create_app():
    app = Flask(__name__)

    #UPLOAD_FOLDER = '/var/www/fhir-server.com/files'
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'asdasdwdqwqdqfqdqwdq'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USERNAME}:{DB_PASS}@localhost:5432/{DB_NAME}'
    db.init_app(app)

#import blueprint from views, auth, patients
    from .views import views 
    from .auth import auth
    from .patient import patients
    from .graphs import graphs
    from .practitioner import practitioner

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(patients, url_prefix='/')
    app.register_blueprint(graphs, url_prefix='/')
    app.register_blueprint(practitioner, url_prefix='/')

    # from .models import User, Note
    from .models import Users, Users_roles

    # create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id_users):
        return Users.query.get(int(id_users))


    return app
