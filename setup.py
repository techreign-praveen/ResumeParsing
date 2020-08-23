from docutil import *
from pdfutil import extract_text_from_pdf
from resumeparser import *

text = extract_text_from_docx("Ashish Tyagi_Resume 2018_.docx")
#text = ''
#for page in extract_text_from_pdf("OmkarResume.pdf"):
 #           text += ' ' + page
print(text)
entities = extract_name(text)

print(entities)