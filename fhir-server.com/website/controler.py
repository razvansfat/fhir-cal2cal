from flask import Blueprint, render_template, request, json, redirect, url_for
from flask_login import login_required, current_user
import requests

from .models import Metatags
from .models import Questionnaire
from .models import Answers
from .models import Patients
from . import db 
from datetime import datetime, date

def save_to_bd(resultFHIR, titleForm, metatags):
    
    # salveaza datele in BD
    new_questionnaire = Questionnaire(title=titleForm, status='active', publisher=current_user.username, date_created=date.today())
    db.session.add(new_questionnaire)
    db.session.commit()
    
    resultFHIR['id'] = new_questionnaire.id_questionnaire

    new_metatag = Metatags(id_questionnaire=resultFHIR['id'], metatags=metatags)
    db.session.add(new_metatag)
    db.session.commit()

    json_data = json.dumps(resultFHIR, indent = 4)

    questionUpdate = Questionnaire.query.filter(Questionnaire.id_questionnaire == new_questionnaire.id_questionnaire).update(dict(json_data=json_data))
    
    db.session.commit()

    return resultFHIR['id']

def saveform(data_recived, id):

    resultFHIR = {}
    itemGroup = []
    itemElem = {}
    metatags = ''

    resultFHIR["resourceType"] = "Questionnaire"

    resultFHIR["text"] = {}
    resultFHIR["text"]["status"] = "generated"
    resultFHIR["text"]["div"] = "<div xmlns=\"http://www.w3.org/1999/xhtml\">\n      <pre>Lifelines Questionnaire 1 part 1\n  1. Do you have allergies?\n  2. General Questions:\n    2.a) What is your gender?\n    2.b) What is your date of birth?\n    2.c) What is your country of birth?\n    2.d) What is your marital status?\n    3. Intoxications:\n      3.a) Do you smoke?\n      3.b) Do you drink alcohol?</pre>\n    </div>"

    resultFHIR['status'] = 'active'

    resultFHIR['publisher'] = current_user.username

    itemName = ''
    linkId = 1

    for elem in data_recived:
        
        if "name" in elem:
            if elem['name'] != 'Metatags' and elem['name'] != 'id':
                if itemName != elem['name']:
                    itemElem = {}
                    itemGroup.append(itemElem)

                    itemElem['linkId'] = str(linkId)
                    itemElem['type'] = elem['type']
                    itemElem['text'] = elem['label']
                    itemName = elem['name']

                    if itemElem['type'] == 'number':
                        if 'step' in elem:

                            itemElem['type'] = 'integer'

                            itemElem['extension'] = []

                            elemSlide1 = {}
                            elemSlide1['url'] = 'http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl'
                            elemSlide1['valueCodeableConcept'] = {}
                            elemSlide1['valueCodeableConcept']['coding'] = []
                            subElemSlide1 = {}
                            subElemSlide1['system'] = 'http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl'
                            subElemSlide1['code'] = 'slider'
                            subElemSlide1['display'] = 'Slider'
                            elemSlide1['valueCodeableConcept']['coding'].append(subElemSlide1)

                            elemSlideMin = {}
                            elemSlideMin['url'] = 'http://hl7.org/fhir/StructureDefinition/minValue'
                            elemSlideMin['valueInteger'] = elem['min']

                            elemSlideMax = {}
                            elemSlideMax['url'] = 'http://hl7.org/fhir/StructureDefinition/maxValue'
                            elemSlideMax['valueInteger'] = elem['max']

                            elemSlideStep = {}
                            elemSlideStep['url'] = 'http://hl7.org/fhir/StructureDefinition/questionnaire-sliderStepValue'
                            elemSlideStep['valueInteger'] = elem['step']

                            itemElem['extension'].append(elemSlide1)
                            itemElem['extension'].append(elemSlideMin)
                            itemElem['extension'].append(elemSlideMax)
                            itemElem['extension'].append(elemSlideStep)

                    if itemElem['type'] == 'select':
                        

                        itemElem['type'] = 'choice'

                        itemElem['extension'] = []

                        elemSlide = {}
                        elemSlide['url'] = 'http://hl7.org/fhir/StructureDefinition/questionnaire-choiceOrientation'
                        elemSlide['valueCode'] = 'horizontal'

                        elemSlide1 = {}
                        elemSlide1['url'] = 'http://hl7.org/fhir/questionnaire-item-control'
                        elemSlide1['valueCodeableConcept'] = {}
                        elemSlide1['valueCodeableConcept']['coding'] = []
                        subElemSlide1 = {}
                        subElemSlide1['system'] = 'http://hl7.org/fhir/questionnaire-item-control'
                        subElemSlide1['code'] = 'radio-button'
                        subElemSlide1['display'] = 'Radio Button'
                        elemSlide1['valueCodeableConcept']['coding'].append(subElemSlide1)

                        
                        itemElem['extension'].append(elemSlide)
                        itemElem['extension'].append(elemSlide1)

                        itemElem['answerOption'] = []
                        answerOpt = []
                        for elemAnsw in elem['values']:
                            choiceAnser = {}
                            answerOpt.append(choiceAnser)

                            choiceAnser['valueString'] = elemAnsw['label']
                        itemElem['answerOption'] = answerOpt

                    if itemElem['type'] == "checkbox-group":
                        itemElem['type'] = 'choice'
                        answerOpt = []
                        for elemAnsw in elem['values']:
                            choiceAnser = {}
                            answerOpt.append(choiceAnser)

                            choiceAnser['valueString'] = elemAnsw['label']
                        itemElem['answerOption'] = answerOpt
                    if itemElem['type'] == "radio-group":
                        itemElem['type'] = 'boolean'

                linkId = linkId + 1
            else:
                if elem['name'] != 'id':
                    if 'value' in elem:
                        metatags = elem['value']
                    else:
                        metatags = ""
                    # add metatags to metatags table
        elif elem['type'] == "header":
            resultFHIR['title'] = elem['label']
            titleForm = elem['label']

    resultFHIR['item'] = itemGroup
    
    if id == 0:
        json_data = json.dumps(resultFHIR, indent = 4)
        rez = save_to_bd(resultFHIR, titleForm, metatags)

        return json_data
    else:
        # UPDATE
        resultFHIR["id"] = id
        
        json_data = json.dumps(resultFHIR, indent = 4)

        update_questionnaire = Questionnaire.query.filter(Questionnaire.id_questionnaire == id).update(dict(json_data=json_data))
        db.session.commit()

        update_metatags = Metatags.query.filter(Metatags.id_questionnaire == id).update(dict(metatags=metatags))
        db.session.commit()
        
        if update_metatags == 0:
            new_metatag = Metatags(id_questionnaire=id, metatags=metatags)
            db.session.add(new_metatag)
            db.session.commit()
        return id

def formsrulesupdate(rezRules):

    questionnaire = Questionnaire.query\
        .filter_by(id_questionnaire=request.form['id'])\
        .first()
    
    content = json.loads(questionnaire.json_data)

    enableWhenArr = []
    enableWhenRaspArr = {}
    answ = ''
    for element in rezRules.split('&'):
        z = element.split('=')
        if z[0] != 'selIntrShow':
            if z[1].find('~') != -1:
                answ = answ + z[1][z[1].find('~')+1:] + '#'
        else:
            enableWhenRaspArr['question'] = answ
            enableWhenRaspArr['answerBoolean'] = 'true'
            enableWhenArr.append(enableWhenRaspArr) 
            for elem in content['item']:
                if elem['linkId'] == z[1].strip('"'):
                    elem['enableWhen'] = enableWhenArr
                    enableWhenArr = []
                    enableWhenRaspArr = {}
                    answ = ''

    dataJson = json.dumps(content)

    questionUpdateRules = Questionnaire.query.filter(Questionnaire.id_questionnaire == request.form['id']).update(dict(json_data=dataJson))
    db.session.commit()

    return content

def createCSVid(date):
    rez = {}
    for a in date.items():
        
        if isinstance(a[1], str):

            rez[a[0]] = a[1]
        else:
            if a[0] == 'item':
                
                for b in a[1]:
                    answ = ''
                    print(b)
                    if 'answer' in b:
                        for c in b['answer']:
                            if c['valueString']=='true':
                                answCom = 'Da'
                            elif c['valueString']=='false':
                                answCom = 'Nu'
                            else:
                                answCom = c['valueString']

                            answ = answ + answCom + ','
                        rez[b['text']] = answ[:-1]
    return rez

def save_raspuns(raspText):

    itemElem = {}
    itemGroup = []
    raspFHIR = {}

    raspFHIR["resourceType"] = "QuestionnaireResponse"
    raspFHIR["status"] = "completed"

    sursa = {
        "reference": "Practitioner/"+str(current_user.id_users)
    }
    raspFHIR["source"] = sursa

    autor = {
        "reference": "Practitioner/"+str(current_user.id_users)
    }
    raspFHIR["author"] = autor


    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    dateAnswer = current_date 

    raspFHIR["authored"] = dateAnswer
 
    textIntr = " "
    itemElem2 = {}


    for x, y in raspText.items():
        
        if(x == "patients"):
            patient = Patients.query.filter_by(id_patient=y.rsplit('/', 1)[-1]).first()
            rezPatient = json.loads(patient.json_data)

            display = rezPatient['name'][0]['family'] + " " + rezPatient['name'][0]['given'][0] 
            subiect = {"reference": y, "display": display}
            raspFHIR["subject"] = subiect

        if(x == "intrID"):
            raspFHIR["questionnaire"] = "http://localhost:8080/fhir/Questionnaire/" + y
            question = y;

        if 'text~' in x:
            idIntrText = x.split('~')

            questionnaire = Questionnaire.query.filter_by(id_questionnaire=idIntrText[1]).first()
            rezQuestion = json.loads(questionnaire.json_data)

            for elem in rezQuestion['item']:
                if(elem['linkId']) == idIntrText[2]:
                    itemElem = {}

                    itemElem["linkId"] = elem['linkId']

                    itemElem["text"] = elem['text']

                    itemElem["answer"] = []
                    elemAnsw = {"valueString": y}
                    itemElem["answer"].append(elemAnsw)

                    itemGroup.append(itemElem)
        if 'integer~' in x:
            idIntrText = x.split('~')

            questionnaire = Questionnaire.query.filter_by(id_questionnaire=idIntrText[1]).first()
            rezQuestion = json.loads(questionnaire.json_data)
            content = rezQuestion

            for elem in content['item']:
                if(elem['linkId']) == idIntrText[2]:
                    itemElem = {}

                    itemElem["linkId"] = elem['linkId']

                    itemElem["text"] = elem['text']

                    itemElem["answer"] = []
                    elemAnsw = {"valueString": y}
                    itemElem["answer"].append(elemAnsw)

                    itemGroup.append(itemElem)

        if 'choice~' in x:
            idIntrChoice = x.split('~')

            questionnaire = Questionnaire.query.filter_by(id_questionnaire=idIntrChoice[1]).first()
            rezQuestion = json.loads(questionnaire.json_data)
            content = rezQuestion

            for nrElem in range(len(content['item'])):

                if content['item'][nrElem]['type'] == 'choice' and content['item'][nrElem]['linkId'] == idIntrChoice[2]:
                    if textIntr != content['item'][nrElem]['text']:
                        if bool(itemElem2):
                            itemGroup.append(itemElem2)
                            itemElem2 = {}

                        textIntr = content['item'][nrElem]['text']

                        itemElem2["linkId"] = content['item'][nrElem]['linkId']
                        itemElem2["text"] = content['item'][nrElem]['text']

                        itemElem2["answer"] = []
                        elemAnsw = {"valueString": y}
                        itemElem2["answer"].append(elemAnsw)
                    else:
                        elemAnsw = {"valueString": y}
                        itemElem2["answer"].append(elemAnsw)

        if 'boolean~' in x:
            idIntrBool = x.split('~')

            questionnaire = Questionnaire.query.filter_by(id_questionnaire=idIntrBool[1]).first()
            rezQuestion = json.loads(questionnaire.json_data)
            content = rezQuestion

            for elem in content['item']:
                if(elem['linkId']) == idIntrBool[2]:
                    itemElem3 = {}

                    itemElem3["linkId"] = elem['linkId']

                    itemElem3["text"] = elem['text']

                    itemElem3["answer"] = []
                    elemAnsw = {"valueString": y}
                    itemElem3["answer"].append(elemAnsw)

                    itemGroup.append(itemElem3)

        if 'date~' in x:
            idIntrText = x.split('~')

            questionnaire = Questionnaire.query.filter_by(id_questionnaire=idIntrText[1]).first()
            rezQuestion = json.loads(questionnaire.json_data)
            content = rezQuestion           

            for elem in content['item']:
                if(elem['linkId']) == idIntrText[2]:
                    itemElem = {}

                    itemElem["linkId"] = elem['linkId']

                    itemElem["text"] = elem['text']

                    itemElem["answer"] = []
                    elemAnsw = {"valueString": y}
                    itemElem["answer"].append(elemAnsw)

                    itemGroup.append(itemElem)

    if bool(itemElem2):
        itemGroup.append(itemElem2)
        itemElem2 = {}

    lista2 = []
    listaItemID = 0


    for elemLista in itemGroup:
        listaItemID = elemLista['linkId']
        # print(listaItemID)
        lista2.insert(int(listaItemID)-1, elemLista)


    raspFHIR['item'] = lista2
    json_data = json.dumps(raspFHIR, indent=4) 

    print(json_data)
    new_questionnaireResponse = Answers(id_question=int(question), status='active', author=current_user.username, source=current_user.username, subject=display, date_created=dateAnswer, json_data=json_data, time_created=current_time)
    db.session.add(new_questionnaireResponse)
    db.session.commit()
    
#############################################################################
def insert_db_from_import(resultFHIR):
    json_data = json.dumps(resultFHIR, indent = 4)
    titleForm = resultFHIR['title']

    rez = save_to_bd(resultFHIR, titleForm, titleForm)

    return json_data