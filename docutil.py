from docx import *
import docx2txt

def extract_text_from_docx(doc_path):
    '''
    Helper function to extract plain text from .docx files
    :param doc_path: path to .docx file to be extracted
    :return: string of extracted text
    '''
    try:
        temp = docx2txt.process(doc_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '
def extract_sections_from_docx(doc_path):
    '''
    Helper function to extract plain text from .docx files
    :param doc_path: path to .docx file to be extracted
    :return: string of extracted text
    '''
    try:
        temp = docx2txt.process(doc_path)
        secs = [line for line in temp.split('\n\n\n\n') if line]
        i = 0
        secDict = {
            "Personal": "",
            "Skills": "",
            "Experience": "",
            "Education": "",
            "Others": ""
        }
        for sec in secs:
            text = ""
            text1 = [line.replace('\t', ' ') for line in sec.split('\n') if line]
            text = ' '.join(text1)
            if (("mobile" in text.lower()) or ("@" in text.lower()) or  ("email" in text.lower()) or  ("e-mail" in text.lower())or  ("mail" in text.lower())):
                secDict["Personal"] = secDict["Personal"]+" "+text
            if("skills" in text.lower()):
                    secDict["Skills"] = secDict["Skills"] + " " + text
            if ("experience" in text.lower() or "exp." in text.lower() or "exp" in text.lower()):
                secDict["Experience"] = secDict["Experience"] + " " + text
            else:
                if(i==0):
                    secDict["Personal"] = secDict["Personal"] + " " + text
                secDict["Others"] = secDict["Others"] + " " + text
            i=i+1
        return secDict
    except KeyError:
        return ' '
def extract_paras_from_docx(doc_path):
        try:
            document = Document(doc_path)
            paras = []
            for para in document.paragraphs:
                paras.append(para.text)
            return paras
        except KeyError:
            return ' '