from pydoc import doc
import PyPDF2
import os 

def import_questionaire(file_name):
# file_name = "DHCS_7098_I_English_SHA_Senior.pdf"
# pdf_file = open(file_name, 'rb')
    #path = os.getcwd() + 'files'
    path = '/var/www/fhir-server.com/files/'
    pdf_file = open(os.path.join(path, file_name), 'rb')

    doc = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = doc.getNumPages()
    
    text = ""
    for i in range(number_of_pages):
        current_page = doc.getPage(i)
        text += current_page.extractText()
    
    q = {}
    nrQ = 1
    nrQ2 = 0
    nrCrt = 0

    textNew0 = text.replace('?', ' ?') 
    textNew = textNew0.replace('\n', ' ').split(" ")

    
    for i in range(len(textNew)):
        try:
            val = int(textNew[i])
            # print(val)
            # print(nrCrt)
            if i >= nrQ2:
                if val == nrCrt + 1:
                    q[nrQ] = []
                    q[nrQ].append(i)
                    nrCrt = val
                
                    for ii in range(i, len(textNew)):
                        if textNew[ii] == '?':
                            q[nrQ].append(ii)
                            nrQ2 = ii
                            break
                    nrQ = nrQ + 1

        except ValueError:
            pass

    # print(q)

    # Inceput creare json FHIR
    resultFHIR = {}
    itemGroup = []
    itemElem = {}
    metatags = ''
    resultFHIR["resourceType"] = "Questionnaire"

    # resultFHIR['id'] = 150  
    resultFHIR['status'] = 'active'
    resultFHIR['title'] = doc.getDocumentInfo().title

    resultFHIR["text"] = {}
    resultFHIR["text"]["status"] = "generated"
    resultFHIR["text"]["div"] = "<div xmlns=\"http://www.w3.org/1999/xhtml\">\n      <pre>Lifelines Questionnaire 1 part 1\n  1. Do you have allergies?\n  2. General Questions:\n    2.a) What is your gender?\n    2.b) What is your date of birth?\n    2.c) What is your country of birth?\n    2.d) What is your marital status?\n    3. Intoxications:\n      3.a) Do you smoke?\n      3.b) Do you drink alcohol?</pre>\n    </div>"

    

    for z in q:
        if len(q[z]) > 1:
            question = ''
            for y in range(q[z][0], q[z][1]+1):
                question = question + textNew[y].strip() + ' '
            # print(question)
            # print('@@@@@@@@@@@@@@@@@@@@')
            itemElem = {}
            itemGroup.append(itemElem)

            itemElem['linkId'] = str(z)
            
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

            itemElem['text'] = question.strip()
            # itemName = elem['name']
            answerOpt = [
                {"valueString": "Yes"},
                {"valueString": "No"},
                {"valueString": "Skip"}
            ]
            itemElem['answerOption'] = answerOpt


    resultFHIR['item'] = itemGroup

    return resultFHIR