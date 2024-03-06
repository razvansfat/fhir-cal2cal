from flask import Blueprint, render_template, request, json, redirect, url_for
from flask_login import login_required, current_user
import requests

from .models import Practitioner, Users, Users_roles, Nom_roles
from . import db 



practitioner = Blueprint('practitioner', __name__)


@practitioner.route('/save_practitioner/', methods = ['POST'])
@login_required
def save_practitioner() -> str:
    
    practitionerResource = {}
    practitionerResource['resourceType'] = "Practitioner"
    practitionerResource['id'] = current_user.id_users
    
    practitionerResource['name'] = []
    name = {}
    name['family'] = request.form.get('lastName')
    name['given'] = []
    name['given'].append(request.form.get('firstName'))
    practitionerResource['name'].append(name)

    practitionerResource['address'] = []
    address = {}
    address['line'] = []
    address['line'].append(request.form.get('address'))
    address['city'] = request.form.get('city')
    address['state'] = request.form.get('country')
    address['postalCode'] = request.form.get('postalcode')
    practitionerResource['address'].append(address)

    practitionerResource['telecom'] = []
    phone = {}
    phone['system'] = "phone"
    phone['value'] = request.form.get('telephone')
    practitionerResource['telecom'].append(phone)

    email = {}
    email['system'] = "email"
    email['value'] = current_user.username
    practitionerResource['telecom'].append(email)

    fax = {}
    fax['system'] = "fax"
    fax['value'] = request.form.get('fax')
    practitionerResource['telecom'].append(fax)
    
    practitionerResource['gender'] = request.form.get('gender')
    practitionerResource['birthDate'] = request.form.get('birthdate')
    json_data = json.dumps(practitionerResource, indent = 4) 


    # salveaza datele in BD
    new_practitioner = Practitioner(first_name=request.form.get('firstName'), last_name=request.form.get('lastName'), gender=request.form.get('gender'), birth_date=request.form.get('birthdate'), address=request.form.get('address'), city=request.form.get('city'), postal_code=request.form.get('postalcode'), country=request.form.get('country'), telephone=request.form.get('telephone'), fax=request.form.get('fax'), json_data=json_data, id_user = current_user.id_users)
    db.session.add(new_practitioner)
    db.session.commit()
    
    return redirect(url_for('practitioner.edit_practitioner'))

@practitioner.route('/edit_practitioner', methods=['GET', 'POST'])
@login_required
def edit_practitioner():

    practitionerQ = Practitioner.query.filter_by(id_user = current_user.id_users).first()
    try:
        content = json.loads(practitionerQ.json_data)
    except:
        content = ''

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    users = Users.query.filter_by(id_users=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    return render_template('edit_practitioner.html', user=current_user, roles=userRole, userInfo=users, allDetails=content, right=userRight)   

@practitioner.route('/view_practitioner/')
@login_required
def view_practitioner():
    
    allUsers = Users.query.all()
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    userInfo = Users.query\
      .join(Users_roles, Users.id_users == Users_roles.user_id)\
      .join(Nom_roles, Nom_roles.code == Users_roles.role)\
      .add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role, Nom_roles.role_name)\
      .order_by(Nom_roles.role_name)\
      .all()
    

    print(userInfo)
    return render_template("view_practitioners.html", user=current_user, roles=userRole, right=userRight, users=allUsers, userInfo=userInfo)