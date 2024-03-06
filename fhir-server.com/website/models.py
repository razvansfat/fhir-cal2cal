from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Users(db.Model, UserMixin):
    def get_id(self):
        return (self.id_users)

    id_users = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.VARCHAR(100))
    last_name = db.Column(db.VARCHAR(100))
    username = db.Column(db.VARCHAR(100), unique=True)
    password = db.Column(db.VARCHAR(100))

class Users_roles(db.Model, UserMixin):
    def get_id(self):
        return (self.roles_id)

    roles_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role = db.Column(db.Integer)
    parinte = db.Column(db.VARCHAR(100))

class Nom_roles(db.Model, UserMixin):
    def get_id(self):
        return (self.id_nom_roles)

    id_nom_roles = db.Column(db.Integer, primary_key=True)
    user_right = db.Column(db.VARCHAR(100))
    code = db.Column(db.Integer)
    role_name = db.Column(db.VARCHAR(100))

class Metatags(db.Model, UserMixin):
    def get_id(self):
        return (self.id_metatags)

    id_metatags = db.Column(db.Integer, primary_key=True)
    id_questionnaire = db.Column(db.Integer)
    metatags = db.Column(db.Text)

class Questionnaire(db.Model, UserMixin):
    def get_id(self):
        return (self.id_questionnaire)

    id_questionnaire = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    status = db.Column(db.Text)
    publisher = db.Column(db.Text)
    date_created = db.Column(db.Date)
    json_data = db.Column(db.Text)

class Answers(db.Model, UserMixin):
    def get_id(self):
        return (self.id_answers)
    
    id_answers = db.Column(db.Integer, primary_key=True)
    id_question = db.Column(db.Integer)
    status = db.Column(db.Text)
    author = db.Column(db.Text)
    source = db.Column(db.Text)
    subject = db.Column(db.Text)
    date_created = db.Column(db.Date)
    json_data = db.Column(db.Text)
    time_created = db.Column(db.Text)


class QuestionnaireResponse(db.Model, UserMixin):
    def get_id(self):
        return (self.id_questionnaireResponse)

    id_questionnaireResponse = db.Column(db.Integer, primary_key=True)
    id_questionnaire = db.Column(db.Integer)
    status = db.Column(db.Text)
    author = db.Column(db.Text)
    source = db.Column(db.Text)
    subject = db.Column(db.Text)
    date_created = db.Column(db.Date)
    json_data = db.Column(db.Text)

class Patients(db.Model, UserMixin):
    def get_id(self):
        return (self.id_patient)
    
    id_patient = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    gender = db.Column(db.Text)
    birthdate = db.Column(db.Date)
    city = db.Column(db.Text)
    country = db.Column(db.Text)
    json_data = db.Column(db.Text)
    surname = db.Column(db.Text)

class Practitioner(db.Model, UserMixin):
    def get_id(self):
        return (self.id_practitioner)
    
    id_practitioner = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    gender = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    telephone = db.Column(db.Date)
    fax = db.Column(db.Date)
    address = db.Column(db.Date)
    city = db.Column(db.Text)
    postal_code = db.Column(db.Text)
    country = db.Column(db.Text)
    json_data = db.Column(db.Text)
    id_user = db.Column(db.Integer)