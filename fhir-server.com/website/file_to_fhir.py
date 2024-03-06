import PyPDF2
import os 

def createFHIR(file_name):
        
    path = os.getcwd()
    pdf_file = open(os.path.join(path, file_name), 'rb')

    doc = PyPDF2.PdfFileReader(pdf_file)

    for i in range(1):
        current_page = doc.getPage(i)
        text = current_page.extractText()
        
    q = {}
    nrQ = 1
    print(text)
    textNew = text.replace('\n', ' ').split(" ")

    for i in range(len(textNew)):
        try:
            val = int(textNew[i])
            q[nrQ] = i
            nrQ = nrQ + 1
            
        except ValueError:
            pass

    rez = {}
    lenQ = len(q)
    for x in q:
        try:
            index_list = []
            if x < lenQ:
                for z in range(q[x], q[x+1]):
                    index_list.append(z)

                res_list = ' '.join([str(elem) for elem in [textNew[i] for i in index_list]]).split("?")
                rez[x] = res_list
                # print (res_list)
                # print('####################################################################################')
        except ValueError:
            pass
    
    return rez