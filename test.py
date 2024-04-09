import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span


nlp = spacy.load("en_core_web_sm")    

text1 = "This is Chapelles' pen"
doc = nlp(text1)

ents = list(doc.ents)

new_ents = []

titles = ['DR', 'DR.', 'MR', 'MR.', 'MS', 'MS.', 'MRS', 'MRS.', 'SIR', 'SIR.']
categories = ["PERSON", "ORG", "GPE", "EVENT"]
suffix_blacklist = ["'S"]

# for token in doc:
#     print(token)

#Insert into entity lists
for ent in ents:

    if (not ent.label_ in categories):
       ents.remove(ent)

    if (ent.label_ == "PERSON"):
            
        if (ent.start != 0):
            prev_token = doc[ent.start - 1]
            if ((prev_token.text).upper() in titles):
                new_ent = Span(doc, ent.start - 1, ent.end, label = ent.label_)
                ent = new_ent

        if ((ent.end - 1) != (len(doc) - 1)):
            last_token = doc[ent.end -1]
            if ((last_token.text).upper() in suffix_blacklist):
                new_ent = Span(doc, ent.start, ent.end - 1, label= ent.label_)
                ent = new_ent     
        
        print(ent.text)
