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
from spacy.matcher import Matcher
from spacy.tokens import Span
from anonymise import anonymise
import time
import sqlite3
import emoji
from guiTest import overview
import tkinter as tk
from tkinter import ttk
import os
import shutil
import time
from datetime import date

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
global window
global main_frame

global images_path
global videos_path
global distribute_path

images_path = os.path.abspath("images")
videos_path = os.path.abspath("videos")
distribute_path = os.path.abspath("distribute")

entities = []
messages = []
message_elements = []

#Window initialisation
window = tk.Tk()
window.title('DATA EXTRACTION')
window.geometry('1280x720')

#Main frame to start
main_frame = ttk.Frame(window, width= 1280, height= 720)
main_frame.pack()

con = sqlite3.connect("sqlite.db")
cur = con.cursor()

nlp = spacy.load("en_core_web_sm")

landing_wrapper_class = "landing-wrapper"
logged_in = '//div[@class="two _aigs"]'

messages_query = '''//div[@role="row"]/div[1]/div[@class="message-in focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]/div[1]/div[@class="x9f619 x1hx0egp x1yrsyyn x1ct7el4 x1dm7udd xwib8y2"]
|//div[@role="row"]/div[1]/div[@class="message-out focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]/div[1]/div[@class="x9f619 x1hx0egp x1yrsyyn x1ct7el4 x1dm7udd xwib8y2"]'''

pic_query = '''//div[@role="row"]/div[1]/div[@class="_amkz message-out focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]
|//div[@role="row"]/div[1]/div[@class="_amkz message-in focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]'''

video_query = '''//div[@role="row"]/div[1]/div[@class="message-in focusable-list-item _amjy _amjz _amjw"]/div[@class="_amk4 _amkv _amk5"]/div[@class="_amk6 _amlo"]
|//div[@role="row"]/div[1]/div[@class="message-out focusable-list-item _amjy _amjz _amjw"]/div[@class="_amk4 _amkv _amk5"]/div[@class="_amk6 _amlo"]
|//div[@role="row"]/div[1]/div[@class="_amkz message-out focusable-list-item _amjy _amjz _amjw"]//div[@class="_amk4 _amkv"]/div[@class="_amk6 _amlo"]
|//div[@role="row"]/div[1]/div[@class="_amkz message-in focusable-list-item _amjy _amjz _amjw"]//div[@class="_amk4 _amkv"]/div[@class="_amk6 _amlo"]'''

def start_window():

    start_btn = ttk.Button(master= main_frame, width= 30,  text= "Start extraction", command= main)
    start_btn.place(relx=0.5, rely=0.5, anchor= "center")

    #Run
    window.mainloop()
    
    loading()

def loading():
    for child in main_frame.winfo_children():
        child.destroy()

    loading_lbl = ttk.Label(master= main_frame, text= "Extracting data...", font=("Arial", 25))
    loading_lbl.place(relx= 0.5, rely= 0.5, anchor= "center")    

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

    titles = ['DR', 'DR.', 'MR', 'MR.', 'MS', 'MS.', 'MRS', 'MRS.', 'SIR', 'SIR.']
    categories = ["PERSON", "ORG", "GPE", "EVENT"]

    suffix_blacklist = ["'", "'S"]

    #Insert into entity lists
    for ent in ents:

        # if (not ent.label_ in categories):
        #     ents.remove(ent)

        if (ent.label_ in categories):
            
            if (ent.label_ == "PERSON"):
            
                if (ent.start != 0):
                    prev_token = masked_doc[ent.start - 1]
                    if ((prev_token.text).upper() in titles):
                        tmp_ent = Span(masked_doc, ent.start - 1, ent.end, label = ent.label_)
                        ent = tmp_ent

            if ((ent.end - 1) != (len(masked_doc) - 1)):
                last_token = masked_doc[ent.end -1]
                if ((last_token.text).upper() in suffix_blacklist):
                    new_ent = Span(masked_doc, ent.start, ent.end - 1, label= ent.label_)
                    ent = new_ent
                

            cur.execute('INSERT INTO entities (category, text) VALUES (?,?)',(ent.label_,ent.text))

            con.commit()

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

def clear_folders():
    shutil.rmtree(images_path)
    os.makedirs(images_path)
    shutil.rmtree(videos_path)
    os.makedirs(videos_path)
    shutil.rmtree(distribute_path)
    os.makedirs(distribute_path)

def move_file(file_type):
    
    while True:
        try:
            file_names = os.listdir(distribute_path)

            for file_name in file_names:
                if file_name.lower().endswith('.crdownload') or file_name.lower().endswith('.tmp') :
                    continue
                if file_type == "Images":
                    shutil.move(os.path.join(distribute_path, file_name), os.path.join(images_path, file_name))

                elif file_type == "Videos":
                    shutil.move(os.path.join(distribute_path, file_name), os.path.join(videos_path, file_name))
            break        
        except PermissionError:
            print("Error")            

def extract_contact(driver):
    #Get contact names
    contacts = driver.find_elements(By.XPATH, '//div[@class="_21S-L"]//div[@class="Mk0Bp _30scZ"]//span[1]')
    return contacts

def main():

    clear_folders()

    cur.execute('''DROP TABLE IF EXISTS messages''')
    cur.execute('''DROP TABLE IF EXISTS entities''')

    cur.execute('''CREATE TABLE IF NOT EXISTS messages
                (chat TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    texts TEXT NOT NULL,
                    type TEXT NOT NULL,
                    media_src TEXT)''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS entities
                (category TEXT NOT NULL,
                    text TEXT NOT NULL)''')


    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", { "download.default_directory": distribute_path})
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
                        

                        message_detail = (name.text, date_sent, time_sent, sender, text_sent, "Texts")

                        message_elements.append(message_detail)

                    except NoSuchElementException:
                        continue
                    except AttributeError:
                        continue       
                
        except NoSuchElementException:
            continue

        profile_btn = driver.find_element(By.XPATH, '//div[@title="Profile details"]')
        profile_btn.click()
        
        contact_detail = driver.find_element(By.XPATH, '//div[@class="_aigv _aig-"]')

        time.sleep(2)

        print(driver.find_element(By.XPATH, '//div[@class="x1emribx x6prxxf x1xojpga"]').text)

        if int(driver.find_element(By.XPATH, '//div[@class="x1emribx x6prxxf x1xojpga"]').text) > 0:

            dialog = contact_detail.find_element(By.XPATH, 'span[1]/div[1]/span[1]/div[1]/div[1]/section[1]/div[@class="x13mwh8y x1q3qbx4 x1wg5k15 xajqne3 x1n2onr6 x1c4vz4f x2lah0s xdl72j9 xyorhqc x13x2ugz x1i80of2 x6x52a7 xxpdul3 x1a8lsjc"]/div[2]')

            first_item = dialog.find_element(By.XPATH, 'div[1]/div[@role="listitem"]')
            first_item.click()

            time.sleep(1)
            
            left_end = False

            while not left_end:

                media_details = driver.find_element(By.XPATH, '//div[@class="_ak8l"]')
                media_sender = media_details.find_element(By.XPATH, 'div[@role="gridcell"]/div[1]/span[1]').text
                date_time = media_details.find_element(By.XPATH, 'div[@class="_ak8j"]/div[1]').text
                media_date = date_time.split(" at ")[0]
                if media_date == "Today":
                    media_date = date.today().strftime("%m/%d/%Y")
                    
                media_time = date_time.split(" at ")[1]

                try:
                    media_text = driver.find_element(By.XPATH, '//p[@class="_alhd"]/span[@dir="auto"]').text
                except NoSuchElementException:
                    media_text = ""

                media_type = ""
                try:
                    image_block = driver.find_element(By.XPATH, '//div[@class="_ajuf _ajuh _ajui _ajug"]')
                    if media_text == "":
                        media_type = "Image"    
                    else:
                        media_type = "Image and texts"   

                    options.add_experimental_option("prefs", { "download.default_directory": images_path})
                        
                except NoSuchElementException:
                    if media_text == "":
                        media_type = "Video"
                    else:
                        media_type = "Video and texts"   

                try:
                    download = driver.find_element(By.XPATH, '//div[@class="_ajv7"]/div[@title="Download"]')
                    download.click()

                    while len(os.listdir(distribute_path)) == 0 :
                        pass

                    if media_type == "Video" or media_type == "Video and texts":
                        time.sleep(0.7)
                        move_file("Videos")
                    elif media_type == "Image" or media_type == "Image and texts":   
                        time.sleep(0.7)
                        move_file("Images") 
                    
                    
                    media_text = media_text.replace("’","'")

                    message_detail = (name.text, media_date, media_time, media_sender, media_text, media_type)

                    message_elements.append(message_detail)
                except NoSuchElementException:
                    pass    

                prev_btn = driver.find_element(By.XPATH, '//div[@class="_alhq"]/div[1]/div[@aria-label="Previous"]')
                
                if prev_btn.get_attribute('aria-disabled') == "true":
                    left_end = True
                else:
                    prev_btn.click()
                    time.sleep(1)
                    

            close_overlay = driver.find_element(By.XPATH, '//div[@class="_ajv7"]/div[@title="Close"]')
            close_overlay.click()        

    for el in message_elements:
        if len(el) == 7:
            cur.execute('INSERT INTO messages (chat, date, time, sender, texts, type, media_src) VALUES (?,?,?,?,?,?,?)',(el[0],str(el[1]),str(el[2]),str(el[3]),anonymise(el[4]),el[5],el[6]))  
        else:
            cur.execute('INSERT INTO messages (chat, date, time, sender, texts, type, media_src) VALUES (?,?,?,?,?,?,?)',(el[0],str(el[1]),str(el[2]),str(el[3]),anonymise(el[4]),el[5],None))  
        con.commit()  

    print("===========================================")    
        
    for el in entities:
        print(el)
    
    overview()    
  

if __name__ == '__main__':
    # start_window()
    main()
            

