from flask import Blueprint, render_template, request, json, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import requests

from .models import Users, Users_roles, Nom_roles, Questionnaire, Answers
from . import db 

graphs = Blueprint('graphs', __name__)

@graphs.route('/view_graphs')
@login_required
def view_graphs():
    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    answersParinte = Users.query.join(Users_roles, Users.id_users == Users_roles.user_id).add_columns(Users.id_users, Users.first_name, Users.last_name, Users.password, Users.username, Users_roles.role).filter(Users_roles.parinte == current_user.id_users).all()
    questParinte = "publisher=" + current_user.username
    if answersParinte != None:
        for row in answersParinte:
            print(row[5])
            questParinte = questParinte + "," + row[5]
    try:
        # API_ENDPOINT = "http://localhost:8080/fhir/Questionnaire?" + questParinte 
        try:
            r = requests.get(url=API_ENDPOINT)
            content = r.json()
            API_ENDPOINT = "http://localhost:8080/fhir/Questionnaire?_sort=-_id&" + questParinte + "&_count=" + str(content['total']) 
            try:
                r2 = requests.get(url=API_ENDPOINT)
                contentAnswers = r2.json()
                userRight = Nom_roles.query.filter_by(code=userRole.role).first()
                return render_template("graphs.html", user=current_user, formulare=contentAnswers, roles=userRole, right=userRight)
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

@graphs.route('/view_graph/<id>')
@login_required
def view_graph(id):
    data = []
    dateGraph = {}
    labels = []
    values = []

    userRole = Users_roles.query.filter_by(user_id=current_user.id_users).first()
    userRight = Nom_roles.query.filter_by(code=userRole.role).first()

    questionnaire = Questionnaire.query.filter_by(id_questionnaire=id).first()
    rezQuestion = json.loads(questionnaire.json_data)


    # API_ENDPOINT_Q = "http://localhost:8080/fhir/Questionnaire/"+ id +"?&_pretty=true"
    # rQ = requests.get(url = API_ENDPOINT_Q) 
    # contentQ = rQ.json()

    contentQ = rezQuestion
    # print(contentQ['title'])
    # print(contentQ['item'])
    for a in contentQ['item']:
        if a['type'] == 'boolean':
            valDa = a['text'] + ' - Da'
            valNu = a['text'] + ' - Nu'
            dateGraph[valDa] = 0
            dateGraph[valNu] = 0
        if a['type'] == 'choice':
            for b in a['answerOption']:
                dateGraph[b['valueString']] = 0

    # print(dateGraph)
    # searchQlink = "http://localhost:8080/fhir/Questionnaire/"+ id
    # API_ENDPOINT = "http://localhost:8080/fhir/QuestionnaireResponse?questionnaire="+ searchQlink +"&_pretty=true"
    # r = requests.get(url = API_ENDPOINT) 
    # content = r.json()

    rezAns = []
    response = Answers.query.filter_by(id_question=id).all()
    print(response)
    for xRezA in response:
        rezAns.append(json.loads(xRezA.json_data))
    
    content = rezAns

    # if 'entry' in content:
    print('OK')
    print(content)

    # question = content['entry']
    question = content
    
    for key in question:
        if key == 'questionnaire':
            if question[key].rsplit('/', 1)[-1] == id:
                
                for b in question['item']:

                    for c in b['answer']:
                        if c['valueString'] in dateGraph:
                            dateGraph[c['valueString']] = dateGraph[c['valueString']] + 1
                        else:
                            # print(c['valueString'])
                            if c['valueString'] == 'false' and b['text'] + ' - Nu' in dateGraph:
                                dateGraph[b['text'] + ' - Nu'] = dateGraph[b['text'] + ' - Nu'] + 1
                            if c['valueString'] == 'true' and b['text'] + ' - Da' in dateGraph:
                                dateGraph[b['text'] + ' - Da'] = dateGraph[b['text'] + ' - Da'] + 1

    testArr = {}
    totalQ = {}

    for a2 in contentQ['item']:
        totalQ[a2['text']] = 0
        if a2['type'] == 'boolean':
            testArr[a2['text']] = {'Yes': 0, 'No': 0}
        if a2['type'] == 'choice':
            testArr[a2['text']] = {}
            for x in a2['answerOption']:

                testArr[a2['text']][x['valueString']] = 0

    for x in content:
        for y in x['item']:
            # print(y['answer'][0]['valueString'])
            if y['text'] in testArr:
                # print(y['answer'])
                # print(testArr[y['text']][y['answer'][0]['valueString']])
                for z in y['answer']:
                    # print(z['valueString'])
                    if z['valueString'] == 'true':
                        trueFalse = 'Yes'
                    elif z['valueString'] == 'false':
                        trueFalse = 'No'
                    else:
                        trueFalse = z['valueString']
                    totalQ[y['text']] = totalQ[y['text']] + 1
                    testArr[y['text']][trueFalse] = testArr[y['text']][trueFalse] + 1

    data = [(k, v) for k, v in dateGraph.items()]
    
    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template("graph.html", fullData = testArr, total = totalQ, labels=labels, values=values, titleQ = contentQ['title'], user=current_user, roles=userRole, right=userRight)
    # else:
    #     print('KO')
    #     return render_template("graph.html", fullData = "", total = 0, labels="", values="", titleQ = contentQ['title'], user=current_user, roles=userRole, right=userRight)