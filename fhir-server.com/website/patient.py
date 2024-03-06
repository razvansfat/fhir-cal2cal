from flask import Blueprint, render_template, request, json, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import requests
import time
from random import randrange

from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users, Users_roles, Nom_roles, Patients, Practitioner
from . import db 
from .controler import saveform, formsrulesupdate, createCSVid, save_raspuns

patients = Blueprint('patients', __name__)

@patients.route('/view_patients')
@login_required
def view_patients():
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    patientsAll = Patients.query.order_by(Patients.id_patient).all()

    return render_template("view_patients.html", user=current_user, roles=userRole, right=userRight, patients=patientsAll)

'''
    API_ENDPOINT = "http://localhost:8080/fhir/Patient?_sort=-_id&_pretty=true"
    try:
        r = requests.get(url=API_ENDPOINT)
        content = r.json()
        API_ENDPOINT2 = "http://localhost:8080/fhir/Patient?_sort=-_id&_count=" + str(content['total']) + "&_pretty=true"
        try:
            r2 = requests.get(url=API_ENDPOINT2)
            contentPatient = r2.json()

            return render_template("view_patients.html", user=current_user, roles=userRole, right=userRight, patients=patientsAll)
        
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
'''
@patients.route('/view_patient/<id>',  methods=['GET', 'POST'])
@login_required
def view_patient(id):
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    
    patientQ = Patients.query.filter_by(id_patient=id).first()
    patient = json.loads(patientQ.json_data)

    # API_ENDPOINT = "http://localhost:8080/fhir/Patient/"+ id
    # try:
    #     r = requests.get(url=API_ENDPOINT)
    #     contentPatient = r.json()
    # except requests.exceptions.HTTPError as err:
    #     raise SystemExit(err)

    return render_template("view_patient.html", user=current_user, roles=userRole, right=userRight, patient=patient)

@patients.route('/add_patient',  methods=['GET', 'POST'])
@login_required
def add_patient():
    contentPatient = ""
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    practitionerQ = Practitioner.query.filter_by(id_user=current_user.id_users).first()


    if request.method == 'POST':
        raspText = request.form

        patientResource = {}
        patientResource['resourceType'] = "Patient"

        # patientResource['id'] = current_user.username + str(randrange(10000))

        patientResource['name'] =[]
        name = {}
        name['use'] = 'official'
        name['family'] = request.form.get('surname')
        name['given'] = []
        name['given'].append(request.form.get('name'))
        patientResource['name'].append(name)

        # patientResource['generalPractitioner'] = []
        identifier = {}
        identifier['reference'] = "Practitioner/"+ str(practitionerQ.id_practitioner)
        patientResource['generalPractitioner'] = identifier
        
        patientResource['address'] = []
        address = {}
        address['line'] = []
        address['line'].append(request.form.get('address'))
        address['city'] = request.form.get('city')
        address['postalCode'] = request.form.get('postalcode')
        address['country'] = request.form.get('country')
        patientResource['address'].append(address)

        patientResource['telecom'] = []
        phone = {}
        phone['system'] = "phone"
        phone['value'] = request.form.get('phone')
        patientResource['telecom'].append(phone)
        email = {}
        email['system'] = "email"
        email['value'] = request.form.get('email')
        patientResource['telecom'].append(email)

        patientResource['gender'] = request.form.get('gender')
        patientResource['birthDate'] = request.form.get('birthdate')

        new_patient = Patients(name=request.form.get('name'), gender=request.form.get('gender'), birthdate=request.form.get('birthdate'), city=request.form.get('city'), country=request.form.get('country'), surname=request.form.get('surname'))
        db.session.add(new_patient)
        db.session.commit()

        patientResource['id'] = new_patient.id_patient
        json_data = json.dumps(patientResource, indent = 4)

        questionUpdate = Patients.query.filter(Patients.id_patient == new_patient.id_patient).update(dict(json_data=json_data))
        print(questionUpdate)
        db.session.commit()

        return redirect(url_for('patients.view_patients'))
    else:        
        return render_template("add_patient.html", user=current_user, roles=userRole, right=userRight)

@patients.route('/edit_patient/<id>',  methods=['GET', 'POST'])
@login_required
def edit_patient(id):

    patientQ = Patients.query.filter_by(id_patient=id).first()
    patient = json.loads(patientQ.json_data)
    
    # API_ENDPOINT = "http://localhost:8080/fhir/Patient/"+ id
    # try:
    #     r = requests.get(url=API_ENDPOINT)
    #     contentPatient = r.json()
    # except requests.exceptions.HTTPError as err:
    #         raise SystemExit(err)

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    return render_template("add_patient.html", user=current_user, roles=userRole, right=userRight, patient=patient)

