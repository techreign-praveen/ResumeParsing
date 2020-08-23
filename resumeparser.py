import constants as cs
import re
import pandas as pd
import spacy
from const import EDUCATION
from dateutil import relativedelta
from spacy.matcher import Matcher
from nltk.corpus import stopwords
from datetime import datetime
from find_job_titles import FinderAcora

nlp = spacy.load('en_core_web_sm')
# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)
STOPWORDS = set(stopwords.words('english'))

def extract_name(resume_text):
    nlp_text = nlp(resume_text)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

    matcher.add('NAME', None, pattern)

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text
def extract_companyname(resume_text):
        try:
            doc = nlp(resume_text)
            entities = []
            for entity in doc.ents:
                if((entity.label_ == "ORG") and ( "ltd" in entity.text.lower()  or "pvt" in entity.text.lower()
                or "private" in entity.text.lower()  or "limted" in entity.text.lower() or "inc." in entity.text.lower()
                or "consulting" in entity.text.lower())):
                        entities.append(entity.text)
            return  entities
        except KeyError:
            return ' '
def extract_jobtitle(resume_text):
        finder = FinderAcora()
        return finder.findall(resume_text)
def extract_entity_sections_grad(text):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for graduates and undergraduates

    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text_split = [i.strip() for i in text.split('\n')]
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)

    # entity_key = False
    # for entity in entities.keys():
    #     sub_entities = {}
    #     for entry in entities[entity]:
    #         if u'\u2022' not in entry:
    #             sub_entities[entry] = []
    #             entity_key = entry
    #         elif entity_key:
    #             sub_entities[entity_key].append(entry)
    #     entities[entity] = sub_entities

    # pprint.pprint(entities)

    # make entities that are not found None
    # for entity in cs.RESUME_SECTIONS:
    #     if entity not in entities.keys():
    #         entities[entity] = None
    return entities
def get_total_experience(experience_list):
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)',
            line,
            re.I
        )
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months
def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume

    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')

    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience
def extract_mobile_number(text):
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
                       text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None
def extract_totalexp(exp):
    matchexp = re.findall("(\d+(\.\d{1,2})?[\+][\s]year)", exp)
    if(matchexp.__len__() == 0):
      matchexp = re.findall("(\d+(\.\d{1,2})?[\s]year)", exp)
    if matchexp:
        try:
            return matchexp[0][0].replace('year','')
        except IndexError:
            return None
def extract_skills(resume_text):
            nlp_text = nlp(resume_text)
            noun_chunks = nlp_text.noun_chunks
            # removing stop words and implementing word tokenization
            tokens = [token.text for token in nlp_text if not token.is_stop]

            # reading the csv file
            data = pd.read_csv("skills.csv")

            # extract values
            skills = list(data.columns.values)

            skillset = []

            # check for one-grams (example: python)
            for token in tokens:
                if token.lower() in skills:
                    skillset.append(token)

            # check for bi-grams and tri-grams (example: machine learning)
            for token in noun_chunks:
                token = token.text.lower().strip()
                if token in skills:
                    skillset.append(token)
                return [i.capitalize() for i in set([i.lower() for i in skillset])]
def extract_education(resume_text):
                nlp_text = nlp(resume_text)
                # Sentence Tokenizer
                nlp_text = [sent.string.strip() for sent in nlp_text.sents]

                edu = {}
                # Extract education degree
                for index, text in enumerate(nlp_text):
                    for tex in text.split():
                        # Replace all special symbols
                        tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                        if tex.upper() in EDUCATION and tex not in STOPWORDS:
                            edu[tex] = text + nlp_text[index + 1]

                # Extract year
                education = []
                for key in edu.keys():
                    year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
                    if year:
                        education.append((key, ''.join(year[0])))
                    else:
                        education.append(key)
                return education
def extract_entities_wih_custom_model(custom_nlp_text):
    '''
    Helper function to extract different entities with custom
    trained model using SpaCy's NER

    :param custom_nlp_text: object of `spacy.tokens.doc.Doc`
    :return: dictionary of entities
    '''
    entities = {}
    for ent in custom_nlp_text.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities
def extract_entity_sections_professional(text):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for professionals
    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) \
                    & set(cs.RESUME_SECTIONS_PROFESSIONAL)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_PROFESSIONAL:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities