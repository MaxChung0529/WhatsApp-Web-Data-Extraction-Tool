from spacy import displacy
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span

global nlp
global doc
global text
global masked_text
global masked_doc
person_list = []
org_list = []
gpe_list = []
event_list = []

def maskText(masked_text):
    matcher = Matcher(nlp.vocab, validate=True)

    #Patterns for phone numbers
    phone_patterns = [[{
        'TEXT': {
            'REGEX': r'([+])?\b((?<=[+])\d{2})?(\d)?\d{10}\b'
        }
    }],
                [{
                    'TEXT': {
                        'REGEX': r'([+])?\b((?<=[+])\d{2})?\b'
                    }
                }, {
                    'TEXT': {
                        'REGEX': r'\b\d{4}\b'
                    }
                }, {
                    'TEXT': {
                        'REGEX': r'\b(\d{1})?(\d{6})\b'
                    }
                }]]


    #Pattern of credit cards
    card_patterns = [[{
        'TEXT': {
            'REGEX': r'\b\d{16}\b'
            }
        }],
                    [{
                        'TEXT': {
                            'REGEX': r'\b\d{4}\b'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'([-])?'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'\b\d{4}\b'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'([-])?'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'\b\d{4}\b'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'([-])?'
                        }
                    }, {
                        'TEXT': {
                            'REGEX': r'\b\d{4}\b'
                        }
                    }]]


    matcher.add("[Phone Numbers]", phone_patterns)
    matcher.add("[Card Number]", card_patterns)
    matches = matcher(doc)

    #Mask email addresses
    for token in doc:
        if token.like_email:
            masked_text = masked_text.replace(token.text,'[Email]', 1)

    #Mask Phone numbers and credit card numbers
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        masked_text = masked_text.replace(span.text, string_id, 1)

    print(masked_text)
    return masked_text

#Add an item to the list
def addToList(list, text):

    added = False

    for item in list:
        if (item[0].upper() == text.upper()):   
            list[list.index(item)] = (text,item[1] + 1)
            added = True

    if (not added):
        list.append((text,1))

    sortList(list)    

def values(e):
    return e[1]    

#Sort the list
def sortList(list):
    list.sort(key = values)

def ner(masked_doc):
    
    masked_doc = nlp(masked_text)

    ents = list(masked_doc.ents)

    global person_list
    global org_list
    global gpe_list
    global event_list

    new_ents = []

    titles = ['DR', 'DR.', 'MR', 'MR.', 'MS', 'MS.', 'MRS', 'MRS.', 'SIR', 'SIR.']
    categories = ["PERSON", "ORG", "GPE", "EVENT"]
    suffix_blacklist = ["'s","'S"]

    #Insert into entity lists
    for ent in ents:

        if (not ent.label_ in categories):
            ents.remove(ent)

        if (ent.label_ == "PERSON"):
            
            if (ent.start != 0):
                prev_token = masked_doc[ent.start - 1]
                if ((prev_token.text).upper() in titles):
                    new_ent = Span(doc, ent.start - 1, ent.end, label = ent.label_)
                    new_ents.append((new_ent, ents.index(ent)))
                    addToList(person_list, new_ent.text)
                else:
                    addToList(person_list, ent.text)

        elif (ent.label_ == "ORG"):
            addToList(org_list, ent.text)
        elif (ent.label_ == "GPE"):
            addToList(gpe_list, ent.text)
        elif (ent.label_ == "EVENT"):
            addToList(event_list, ent.text)

    #Add title to PERSON entities
    tmp_masked_doc = ents
    for ent in new_ents:
        tmp_masked_doc[ent[1]] = ent[0]

    masked_doc.ents = tmp_masked_doc

    return masked_doc        

def anonymise():

    nlp = spacy.load("en_core_web_sm")

    with open("data/data.txt", "r") as f:
        text = f.read()

    masked_text = text

    masked_text = maskText(masked_text)

    masked_doc = nlp(masked_text)
    masked_doc = ner(masked_doc)

    if (len(person_list) > 0):
        print("--------PERSON--------")
        for item in person_list:
            print(item)
    if (len(org_list) > 0):
        print("--------ORG--------")
        for item in org_list:
            print(item)
    if (len(gpe_list) > 0):
        print("--------GPE--------")
        for item in gpe_list:
            print(item)
    if (len(event_list) > 0):
        print("--------EVENT--------")
        for item in event_list:
            print(item)

    #Make sure there are entities
    if (len(list(masked_doc.ents)) > 0):
        displacy.serve(masked_doc, style="ent",auto_select_port=True)    
