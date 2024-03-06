from distutils.errors import DistutilsFileError
from flask import Blueprint, render_template, request, json, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import requests
import time
import csv
import pathlib
import os 

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import Users, Users_roles, Nom_roles, Metatags, Questionnaire, Answers, Patients
from . import db 
from .controler import saveform, formsrulesupdate, createCSVid, save_raspuns, insert_db_from_import
from .file_to_fhir import createFHIR
from .import_questionaire import import_questionaire

from datetime import datetime

from sqlalchemy import desc

from pydoc import doc

views = Blueprint('views', __name__)

@views.route('/refreshforms')
@login_required
def refreshforms():
    time.sleep(5)
    return redirect(url_for('views.home'))

@views.route('/')
# @login_required
def public_page():
    return render_template("public_page/public_page.html")

@views.route('/home')
@login_required
def home():
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    metatagsRez = Metatags.query.all()
    answersParinte = Users.query.join(Users_roles, Users.id_users == Users_roles.user_id).add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role).filter(Users_roles.parinte == current_user.id_users).all()

    questParinte = "publisher=" + current_user.username

    questionnaireAll = Questionnaire.query.order_by(Questionnaire.id_questionnaire.desc()).all()
    path = os.getcwd() + 'files'

    return render_template("home.html", user=current_user, formulare=questionnaireAll, metatags=metatagsRez, roles=userRole, right=userRight, cale=path)

    
@views.route('/create_form/')
@login_required
def create_form():
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    if '12' in userRight.user_right:
        return render_template("create_form.html", user=current_user, roles=userRole, right=userRight)
    else:
        return redirect(url_for('views.home'))


@views.route('/createform/', methods=['POST'])
@login_required
def createform():
    if request.method == 'POST':
        asd = request.json

        x = saveform(asd, 0)

    return {'rez': x}

@views.route('/create_form_edit/<id>')
@login_required
def create_form_edit(id):
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    
    questionnaire = Questionnaire.query.filter_by(id_questionnaire=id).first()
    rezQuestion = json.loads(questionnaire.json_data)

    rez = []

    rez.append({
        "type": "header",
        "label": rezQuestion['title']
    })

    for x in rezQuestion['item']:
        elem = {}
        
        if x['type'] == 'choice':
            val = []
            if 'extension' in x:
                elem['type'] = 'select'
            else:
                elem['type'] = 'checkbox-group'

            for y in x['answerOption']:
                elemVal = {}
                elemVal['label'] = y['valueString']
                val.append(elemVal)
            elem['values'] = val 
        elif x['type'] == 'boolean':
            elem['type'] = 'radio-group'
            elem['values'] = [{"label": "Yes","value": "yes","selected": 'false'},{"label": "No","value": "no","selected": 'false'}]
        elif x['type'] == 'integer':
            elem['type'] = 'number'
            elem['min'] = x['extension'][1]['valueInteger']
            elem['max'] = x['extension'][2]['valueInteger']
            elem['step'] = x['extension'][3]['valueInteger']

        else:
            elem['type'] = x['type']
            elem['className'] = 'form-control'

        elem['label'] = x['text']

        rez.append(elem)

    metatagsRez = Metatags.query.filter_by(id_questionnaire=rezQuestion['id']).first()

    if metatagsRez != None:
        rez.append(
            {
                "type": "text",
                "label": "Metatags",
                "className": "form-control",
                "name": "Metatags",
                "value": metatagsRez.metatags
            })

    idStr = str(rezQuestion['id'])
    rez.append({
            "type": "hidden",
            "name": "id",
            "value": idStr,
        })

    return render_template("create_form_edit.html", user=current_user, id = rezQuestion['id'], continut = rez, roles=userRole, right=userRight)

@views.route('/createformedit/', methods=['POST'])
@login_required
def createformedit():
    if request.method == 'POST':
        asd = request.json

        for elem in asd:
            if elem['type'] == 'hidden':
                id = elem['value']

        x = saveform(asd, id)

    return {'rez': x}

@views.route('/createrules/<id>')
@login_required
def createrules(id):
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    questionnaire = Questionnaire.query\
        .filter_by(id_questionnaire=id)\
        .first()
    
    rezQuestion = json.loads(questionnaire.json_data)

    key = 'enableWhen'
    i = 0
    for x in rezQuestion['item']:
        
        if key in x:
            for y in x['enableWhen']:
                if y['answerBoolean']:
                    rez = int(y['answerBoolean'] == True)
                    rezQuestion['item'][i]['enableWhen'][0]['answerBoolean'] = rez
                else:
                    rez = int(y['answerBoolean'] == False)
                    rezQuestion['item'][i]['enableWhen'][0]['answerBoolean'] = rez
        i = i + 1

    rules = []

    return render_template("question_rules.html", user=current_user, continut = rezQuestion, roles=userRole, right=userRight)

@views.route('/formsrulessave/', methods=['POST'])
@login_required
def formsrulessave():
    if request.method == 'POST':
        
        rezRules = request.form['data']
        id_new = formsrulesupdate(rezRules)

    return redirect(url_for('views.home'))

@views.route('/form/<id>')
@login_required
def form(id):

    questionnaire = Questionnaire.query\
            .filter_by(id_questionnaire=id)\
            .first()
    
    rezQuestion = json.loads(questionnaire.json_data)
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    patientsAll = Patients.query.order_by(Patients.id_patient).all()
    getPateints = []
    for elem in patientsAll:
        getPateints.append(json.loads(elem.json_data))

    return render_template("form.html", user=current_user, question = rezQuestion, patients = getPateints, id = id, roles=userRole, right=userRight)

@views.route('/saveRaspuns/', methods = ['POST'])
@login_required
def saveRaspuns():
    
    raspText = request.form
    save_raspuns(raspText)
    
    return redirect(url_for('views.show_answers'))

@views.route('/show_answers')
@login_required
def show_answers():

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    questionnaireResponse = Answers.query.order_by(Answers.id_answers.desc()).all()

    return render_template("answers.html", user=current_user, formulare = questionnaireResponse, roles=userRole, right=userRight)

@views.route('/answer/<id>')
@login_required
def answer(id):

    answer = Answers.query\
        .filter_by(id_answers=id)\
        .first()
    rezAnswer = json.loads(answer.json_data)

    question = Questionnaire.query\
        .filter_by(id_questionnaire=answer.id_question)\
        .first()
    questionTitle = question.title

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    
    return render_template('answer.html', user=current_user, answer = rezAnswer, id = id, qTitle = questionTitle, roles=userRole, right=userRight)   

@views.route('/sterge/<id>/<tip>')
@login_required
def sterge(id, tip):

    if tip == 'Questionnaire':
        question = Questionnaire.query\
            .filter_by(id_questionnaire=id)\
            .delete();
        db.session.commit()
        # return render_template("home.html", user=current_user, formulare=content, roles=userRole, right=userRight)
        return redirect(url_for('views.home'))
    if tip == 'QuestionnaireResponse':
        answer = Answers.query\
            .filter_by(id_answers=id)\
            .delete();
        db.session.commit()
        # return render_template("answers.html", user=current_user, formulare = content, roles=userRole, right=userRight)
        return redirect(url_for('views.show_answers'))



    # API_ENDPOINT = "http://localhost:8080/fhir/"+ tip +"/" + id + "?_pretty=true"
    # r = requests.delete(url = API_ENDPOINT) 

    # if r.status_code == 200:
    #     API_ENDPOINT = "http://localhost:8080/fhir/"+ tip +"?_sort=-_id&_pretty=true"
    #     r = requests.get(url=API_ENDPOINT)
    #     content = r.json()
    #     userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    #     userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    #     if tip == 'Questionnaire':
    #         return render_template("home.html", user=current_user, formulare=content, roles=userRole, right=userRight)
    #     if tip == 'QuestionnaireResponse':
    #         return render_template("answers.html", user=current_user, formulare = content, roles=userRole, right=userRight)
    # else:
    #     raise Exception(r.json())

# user admin

@views.route('/sign-up/', defaults={'id': None}, methods=['GET', 'POST'])
@views.route('/sign-up/<int:id>', methods=['GET', 'POST'])
@login_required
def sign_up(id):

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        roles = request.form.get('userRoles')
        
        user = Users.query.filter_by(username=email).first()

        if user:
            flash('Email exists', category='error')
        elif len(email) < 4:
            flash('Email must be grater than 4 char', category='error')
        elif len(firstName) < 2:
            flash('First name must be grater than 2 char', category='error')
        elif password1 != password2:
            flash('Passwords dont match', category='error')
        elif len(password1) < 4:
            flash('Password must be greater than 4 char', category='error')
        else:
            
            new_user = Users(username=email, first_name=firstName, last_name=lastName, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            # login_user(new_user)

            if userRole.role == 1:
                userRoles = Users_roles(user_id=new_user.id_users, role=roles)
            else :
                userRoles = Users_roles(user_id=new_user.id_users, role=roles, parinte=userRole.user_id)

            db.session.add(userRoles)
            db.session.commit()

            flash('Account created', category='success')
            # return redirect(url_for('views.home'))
    

    userRight = Nom_roles.query.filter_by(code=userRole.role).first()
    nomRoles = Nom_roles.query.all()

    if request.method == 'GET':
        userEdit = Users.query.join(Users_roles, Users.id_users == Users_roles.user_id).add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role).filter(Users.id_users == id).first()

        return render_template("sign-up.html", user=current_user, roles=userRole, nomRoles=nomRoles, right=userRight, userEdit=userEdit)

    # userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    # userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    results = [
            {
                "right": role.user_right,
                "code": role.code
            } for role in nomRoles]

    return render_template("sign-up.html", user=current_user, roles=userRole, nomRoles=nomRoles, right=userRight)

@views.route('/create_roles/', defaults={'id': None}, methods=['GET', 'POST'])
@views.route('/create_roles/<int:id>', methods=['GET', 'POST'])
@login_required
def create_roles(id):
    if request.method == 'POST':
        idRole = request.form['idRole']

        if idRole == 0 or idRole == '':
            role_name = request.form['roleName'] 
            role_code = request.form['roleCode'] 
            role_right = ''

            if 'readform' in request.form:
                role_right = role_right + request.form['readform'] + '~'
            if 'createform' in request.form:
                role_right = role_right + request.form['createform'] + '~'
            if 'deleteform' in request.form:
                role_right = role_right + request.form['deleteform'] + '~'

            if 'readanswer' in request.form:
                role_right = role_right + request.form['readanswer'] + '~'
            if 'createanswer' in request.form:
                role_right = role_right + request.form['createanswer'] + '~'
            if 'deleteanswer' in request.form:
                role_right = role_right + request.form['deleteanswer'] + '~'

            if 'createrole' in request.form:
                role_right = role_right + request.form['createrole'] + '~'
            if 'createpractitioner' in request.form:
                role_right = role_right + request.form['createpractitioner'] + '~'
            if 'viewpractitioner' in request.form:
                role_right = role_right + request.form['viewpractitioner'] + '~'
            if 'editpractitioner' in request.form:
                role_right = role_right + request.form['editpractitioner'] + '~'

            new_role = Nom_roles(role_name=role_name, code=role_code, user_right=role_right[:-1])
            db.session.add(new_role)
            db.session.commit()

            userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
            userRight = Nom_roles.query.filter_by(code=userRole.role).first()

            return render_template("create_roles.html", user=current_user, roles=userRole, right=userRight)
        else:
                        
            rolesUpdate = Nom_roles.query.filter(Nom_roles.id_nom_roles == id).update(dict(role_name=request.form['roleName']))

            roleEdit = Nom_roles.query.filter(Nom_roles.id_nom_roles == idRole).first()
            userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
            userRight = Nom_roles.query.filter_by(code=userRole.role).first()

            return render_template("create_roles.html", user=current_user, roles=userRole, right=userRight, roleEdit=roleEdit)
    
    if request.method == 'GET':
        roleEdit = Nom_roles.query.filter(Nom_roles.id_nom_roles == id).first()
        userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
        userRight = Nom_roles.query.filter_by(code=userRole.role).first()

        return render_template("create_roles.html", user=current_user, roles=userRole, right=userRight, roleEdit=roleEdit)


@views.route('/view_roles/')
@login_required
def view_roles():
    rolesAll = Nom_roles.query.all()
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    return render_template("view_roles.html", user=current_user, roles=userRole, right=userRight, rolesView=rolesAll)

# @views.route('/view_practitioner/')
# @login_required
# def view_practitioner():
    
#     allUsers = Users.query.all()
#     userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
#     userRight = Nom_roles.query.filter_by(code=userRole.role).first()

#     userInfo = Users.query\
#       .join(Users_roles, Users.id_users == Users_roles.user_id)\
#       .join(Nom_roles, Nom_roles.code == Users_roles.role)\
#       .add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role, Nom_roles.role_name)\
#       .order_by(Nom_roles.role_name)\
#       .all()
    
#     return render_template("view_practitioners.html", user=current_user, roles=userRole, right=userRight, users=allUsers, userInfo=userInfo)

@views.route('/export/', defaults={'id': None}, methods=['GET'])
@views.route('/export/<int:id>', methods=['GET'])
@login_required
def export(id):

    dict_data = []
    csv_columns = [ 'questionnaire', 'resourceType', 'status', 'id', 'authored']
    csv_columns2 = []

    if request.method == 'GET':
        answer = Answers.query\
            .filter_by(id_answers=id)\
            .first()
        content = json.loads(answer.json_data)
        # if id:    
        #     idGet = str(id)
        #     API_ENDPOINT = "http://localhost:8080/fhir/QuestionnaireResponse/" + idGet + "?&_pretty=true"
        # else:
        #     API_ENDPOINT = "http://localhost:8080/fhir/QuestionnaireResponse/?&_pretty=true"
        
        # r = requests.get(url = API_ENDPOINT) 
        # content = r.json()

        # if content['resourceType'] == 'Bundle':

        #     question = content['entry'][0]['resource']['questionnaire']
            
        #     csv_file = "AnswersQ" + question + ".csv"

        #     # API_ENDPOINT2 = "http://localhost:8080/fhir/Questionnaire/" + question + "?_pretty=true"
        #     API_ENDPOINT2 = question
            
        #     for x in content['entry']:
        #         dict_data.append(createCSVid(x['resource']))
        # else:

        #     question = content['questionnaire']
        #     # API_ENDPOINT2 = "http://localhost:8080/fhir/Questionnaire/" + question + "?_pretty=true"
        #     API_ENDPOINT2 = question
            
        #     csv_file = "Answer" + idGet + ".csv"
            
        #     dict_data.append(createCSVid(content))

        path = '/var/www/fhir-server.com/files/'
        idGet = str(id)
        csv_file = path + "Answer" + idGet + ".csv"
        dict_data.append(createCSVid(content))

        # r = requests.get(url = API_ENDPOINT2) 
        questRez = content

        for aQ in questRez['item']:
            csv_columns2.append(aQ['text'])
                
        csv_columns.extend(csv_columns2)

        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
        
        cale = pathlib.Path().resolve()
        path = str(cale)+"\\"+csv_file

        return send_file(path, as_attachment=True)
    else:
        return redirect(url_for('views.show_answers'))

# upload file
# @views.route('/upload')
# def upload_file():
#    return render_template('upload.html')
	
@views.route('/uploader/', methods = ['GET', 'POST'])
@login_required
def uploader():

    UPLOAD_FOLDER = '/var/www/fhir-server.com/files/'
    
    if request.method == 'POST':
        file = request.files['file']
        #f.save(secure_filename(f.filename))
        filename = secure_filename(file.filename).replace('(','').replace(')','').replace(' ','_')
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        file_name = file.filename.replace('(','').replace(')','').replace(' ','_')
        # rez = createFHIR(file_name)
        rez_import = import_questionaire(file_name)
        
        rez = insert_db_from_import(rez_import)

        return redirect(url_for('views.home'))