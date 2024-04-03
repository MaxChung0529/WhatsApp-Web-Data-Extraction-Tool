from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import base64
from insert import insert
from anonymise import anonymise
import time
import sqlite3
import emoji
import re

global nlp
global doc
global text
global masked_text
global masked_doc
global messages
global message_elements
global entities
global con
global cur
entities = []
messages = []
message_elements = []


con = sqlite3.connect("sqlite.db")
cur = con.cursor()

nlp = spacy.load("en_core_web_sm")

landing_wrapper_class = "landing-wrapper"
logged_in = '//div[@class="two _aigs"]'

messages_query = '''//div[@role="row"]/div[1]/div[@class="message-in focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]/div[1]/div[@class="x9f619 x1hx0egp x1yrsyyn x1ct7el4 x1dm7udd xwib8y2"]
|//div[@role="row"]/div[1]/div[@class="message-out focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]/div[1]/div[@class="x9f619 x1hx0egp x1yrsyyn x1ct7el4 x1dm7udd xwib8y2"]'''

pic_query = '''//div[@role="row"]/div[1]/div[@class="_amkz message-out focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]
|//div[@role="row"]/div[1]/div[@class="_amkz message-in focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]'''


# top_row = '''//div[@role="row"]//div[@class="CzM4m _2zFLj"]//div[@class="_2OvAm focusable-list-item _2UtSC _1jHIY"]'''
# text_class = "_11JPr selectable-text copyable-text"
# contact_list = "_199zF _3j691"
# title_class = "Mk0Bp _30scZ"

def convert_emoji_to_text(emoji_text):
    text_with_emoji = emoji.demojize(emoji_text)
    return text_with_emoji

def maskText(masked_text, doc):
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

    #print(masked_text)
    return masked_text

def ner(masked_doc):

    ents = list(masked_doc.ents)

    new_ents = []

    titles = ['DR', 'DR.', 'MR', 'MR.', 'MS', 'MS.', 'MRS', 'MRS.', 'SIR', 'SIR.']
    categories = ["PERSON", "ORG", "GPE", "EVENT"]
    suffix_blacklist = ["'s","'S"]

    #Insert into entity lists
    for ent in ents:

        if (not ent.label_ in categories):
            ents.remove(ent)

        if (ent.label_ in categories):
            
            if (ent.label_ == "PERSON"):
            
                if (ent.start != 0):
                    prev_token = masked_doc[ent.start - 1]
                    if ((prev_token.text).upper() in titles):
                        new_ent = Span(doc, ent.start - 1, ent.end, label = ent.label_)
                        new_ents.append((new_ent, ents.index(ent)))
                        cur.execute('INSERT INTO entities (category, text) VALUES (?,?)',(new_ent.label_,new_ent.text))
                    else:
                        cur.execute('INSERT INTO entities (category, text) VALUES (?,?)',(ent.label_,ent.text))

                    con.commit()    

    #Add title to PERSON entities
    tmp_masked_doc = ents
    for ent in new_ents:
        tmp_masked_doc[ent[1]] = ent[0]

    masked_doc.ents = tmp_masked_doc

    return masked_doc        


def anonymise(text):

    masked_text = text
    doc = nlp(text)

    masked_text = maskText(masked_text, doc)
    #demojised_masked_text = re.sub("\:.*?\:","",masked_text)

    #masked_doc = nlp(demojised_masked_text)
    masked_doc = nlp(masked_text)
    masked_doc = ner(masked_doc)

    return masked_text        

    # #Make sure there are entities
    # if (len(list(masked_doc.ents)) > 0):
    #     displacy.serve(masked_doc, style="ent",auto_select_port=True)    

def extract_images(split_src, image_src, driver):

    result = driver.execute_async_script("""
                        var uri = arguments[0];
                        var callback = arguments[1];
                        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
                        var xhr = new XMLHttpRequest();
                        xhr.responseType = 'arraybuffer';
                        xhr.onload = function(){ callback(toBase64(xhr.response)) };
                        xhr.onerror = function(){ callback(xhr.status) };
                        xhr.open('GET', uri);
                        xhr.send();
                        """, image_src)
    
    # if type(result) == int :
    #     raise Exception("Request failed with status %s" % result)
    try:
        final_image = base64.b64decode(result)
        filename = 'images/' + split_src[len(split_src) - 1] + '.jpg'
        with open(filename, 'wb') as f:
            f.write(final_image)
        return filename   
    except TypeError:
        print("WTF")
        pass     

def extract_contact(driver):
    #Get contact names
    contacts = driver.find_elements(By.XPATH, '//div[@class="_21S-L"]//div[@class="Mk0Bp _30scZ"]//span[1]')
    return contacts

def main():

    cur.execute('''DROP TABLE IF EXISTS messages''')
    cur.execute('''DROP TABLE IF EXISTS entities''')

    cur.execute('''CREATE TABLE IF NOT EXISTS messages
                (chat TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    texts TEXT NOT NULL,
                    type TEXT NOT NULL)''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS entities
                (category TEXT NOT NULL,
                    text TEXT NOT NULL)''')


    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)


    driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    driver.get("https://web.whatsapp.com/")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, landing_wrapper_class)) #Check if it has arrived at the login page yet
        )
    finally:
        print("Login Page")


    while True:

        try:
            form = driver.find_element(
                By.XPATH, logged_in
            )  #Check if user has logged in yet by checking for classes that only appears in logged in interface
            print("Logged in")
            break

        except NoSuchElementException:
            continue


    #Get contact names
    contacts = driver.find_elements(By.XPATH, '//div[@aria-label = "Chat list"]/div[@role="listitem"]/div[1]/div[1]/div[1]/div[2]/div[@role="gridcell"]//span[@dir="auto"]')
    #contacts = extract_contact(driver)
    time.sleep(0.5)

    for name in contacts:

        #Terminate if no contacts are found
        if (len(contacts) <= 0):
            break

        name.click()

        time.sleep(2)

        try:
            sync_ok_button = driver.find_element(By.XPATH, '//button[@class="emrlamx0 aiput80m h1a80dm5 sta02ykp g0rxnol2 l7jjieqr hnx8ox4h f8jlpxt4 l1l4so3b le5p0ye3 m2gb0jvt rfxpxord gwd8mfxi mnh9o63b qmy7ya1v dcuuyf4k swfxs4et bgr8sfoe a6r886iw fx1ldmn8 orxa12fk bkifpc9x rpz5dbxo bn27j4ou oixtjehm hjo1mxmu snayiamo szmswy5k"]')
            print("FOUND SYNC OK BUTTON")
                            
            #if (sync_ok_button.text == 'OK'):
            sync_ok_button.click()
            clickedOnBtn = True
            print("CLICKED SYNC OK BUTTON")
        except NoSuchElementException:
            print("COULDN'T FIND BUTTON")  

        #Locate the chat pane
        chat_pane = driver.find_element(By.XPATH, '//div[@class="_ajyl"]')    

        reachedTop = False
        while not reachedTop:

            chat_pane.send_keys(Keys.CONTROL + Keys.HOME)
            WebDriverWait(driver, 10)
            
            try:
                #Check if reaches top
                driver.find_element(By.XPATH, '//div[@class="_amk4 _amkg _amkb"]')
                reachedTop = True
                break
            except NoSuchElementException:
                #Click the button to sync message
                try:
                    sync_msg_button = driver.find_element(By.XPATH, '//div[@class="_ahmw copyable-area"]/div[2]/div[2]/button[1]')
                    sync_msg_button.click()
                except NoSuchElementException:
                    print("No Sync older messages")
                except StaleElementReferenceException:
                    pass


        try:
            find_message = driver.find_elements(By.XPATH, messages_query)
            print(len(find_message))
            if (len(find_message) > 0):
                for message in find_message:
                        

                    try:

                        time_and_sender = message.find_element(By.XPATH, 'div[1]').get_attribute('data-pre-plain-text')  

                        
                        time_and_sender = time_and_sender.replace("] ","]|").split("|")
                        

                        date_sent = time_and_sender[0].split(", ")[1].replace("]","")
                        time_sent = time_and_sender[0].split(", ")[0].replace("[","")
                        sender = time_and_sender[1].replace(": ","").replace("['","").replace("']","")

                        if sender != name.text:
                            sender = "You"

                        text_sent = message.find_element(By.XPATH, 'div[1]/div[1]/span[1]/span').text
                        text_sent = text_sent.replace("’","'")
                        
                        #text_sent = convert_emoji_to_text(text_sent)

                        message_detail = (name.text, date_sent, time_sent, sender, text_sent, "Texts")

                        # if (text_sent != None and (not message_detail in message_elements)):
                        message_elements.append(message_detail)

                    except NoSuchElementException:
                        continue
                    except AttributeError:
                        continue       
                
        except NoSuchElementException:
            continue

        try:
            pics = driver.find_elements(By.XPATH, pic_query)
            for pic in pics:

                img = pic.find_element(By.XPATH, 'div[1]/div[1]/div[1]/div[1]/div[2]/img')
                
                image_src = img.get_attribute('src')

                haveText = not img.get_attribute('alt') == ""

                if (haveText):

                    time_and_sender = pic.find_element(By.XPATH, 'div[1]').get_attribute('data-pre-plain-text')                          
                    time_and_sender = time_and_sender.replace("] ","]|").split("|")
                        
                    date_sent = time_and_sender[0].split(", ")[1].replace("]","")
                    time_sent = time_and_sender[0].split(", ")[0].replace("[","")
                    sender = time_and_sender[1].replace(": ","").replace("['","").replace("']","")

                    if sender != name.text:
                        sender = "You"

                    text_sent = img.get_attribute('alt').replace("’","'")
                    text_sent = convert_emoji_to_text(text_sent)

                    
                    message_detail = (name.text, date_sent, time_sent, sender, text_sent, "Images and texts")
                        
                    if (text_sent != None and (not message_detail in message_elements)):
                        message_elements.append(message_detail)
                        

                split_src = str(image_src).split("/")

                try:
                    tmp = pic.find_element(By.XPATH, 'div[@class="x9f619 xyqdw3p x10ogl3i xg8j3zb x1k2j06m x1n2onr6 x1vjfegm xf58f5l"]')
                    sender = name.text
                    time_sent = tmp.text
                    date_sent = "Unkown"
                except:
                    sender = "You"    

                filename = extract_images(split_src, image_src, driver)
                if not haveText:
                    message_detail = (name.text, date_sent, time_sent, sender, filename, "Image")   
                    message_elements.append(message_detail)     
        except NoSuchElementException:
            continue

    for el in message_elements:
        cur.execute('INSERT INTO messages (chat, date, time, sender, texts, type) VALUES (?,?,?,?,?,?)',(el[0],str(el[1]),str(el[2]),str(el[3]),anonymise(el[4]),el[5]))  
        con.commit()  

    print("===========================================")    
        
    for el in entities:
        print(el)
  

if __name__ == '__main__':
    main()
            

