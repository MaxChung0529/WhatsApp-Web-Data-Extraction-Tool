from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from insert import insert

landing_wrapper_class = "landing-wrapper"
logged_in = "_3WByx"
user_query = '''//div[@class="_21S-L"]/div[@class="Mk0Bp _30scZ"]/span[@class='ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 l7jjieqr _11JPr'][@dir="auto"]'''

messages_query = '''//div[@role="row"]//div[@class="message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a _3m5cz"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a _3m5cz"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a"]//div[@class="_1BOF7 _2AOIt"]'''

pics_query = '''//div[@class="cm280p3y ktbp76dp ocd2b0bc folpon7g aa0kojfi snweb893 g0rxnol2 jnl3jror"]//div[1]//div[@class="gndfcl4n l8fojup5 paxyh2gw sfeitywo cqsf3vkf p357zi0d ac2vgrno laorhtua gfz4du6o r7fjleex g0rxnol2"]//div[@class="g0rxnol2 ln8gz9je ppled2lx"]//div[@class="lhggkp7q jnl3jror p357zi0d gndfcl4n ac2vgrno ln8gz9je ppled2lx"][2]//img[1]
|//div[@class="cm280p3y eu4mztcy ocd2b0bc folpon7g aa0kojfi snweb893 g0rxnol2 jnl3jror"]//div[1]//div[@class="gndfcl4n l8fojup5 paxyh2gw sfeitywo cqsf3vkf p357zi0d ac2vgrno laorhtua gfz4du6o r7fjleex g0rxnol2"]//div[@class="g0rxnol2 ln8gz9je ppled2lx"]//div[@class="lhggkp7q jnl3jror p357zi0d gndfcl4n ac2vgrno ln8gz9je ppled2lx"][2]//img[1]'''

top_row = '''//div[@role="row"]//div[@class="CzM4m _2zFLj"]//div[@class="_2OvAm focusable-list-item _2UtSC _1jHIY"]'''
text_class = "_11JPr selectable-text copyable-text"
contact_list = "_199zF _3j691"
title_class = "Mk0Bp _30scZ"

import sqlite3

con = sqlite3.connect("sqlite.db")
cur = con.cursor()

cur.execute('''DROP TABLE IF EXISTS messages''')

cur.execute('''CREATE TABLE IF NOT EXISTS messages
            (time TEXT NOT NULL,
                 sender TEXT NOT NULL,
                 texts TEXT NOT NULL)''')


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)


driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
driver.get("https://web.whatsapp.com/")
wait = WebDriverWait(driver, 2)

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, landing_wrapper_class)) #Check if it has arrived at the login page yet
    )
finally:
    print("Login Page")


while True:
    try:
        form = driver.find_element(
            By.CLASS_NAME, logged_in
        )  #Check if user has logged in yet by checking for classes that only appears in logged in interface

        break
    except NoSuchElementException:
        continue

#Get contact names
contacts = driver.find_elements(By.XPATH, '//div[@class="_21S-L"]//div[@class="Mk0Bp _30scZ"]//span[1]')

for name in contacts:
    print(name.text)
    name.click()

    #Locate the chat pane
    chat_pane = driver.find_element(By.XPATH, '//div[@class="n5hs2j7m oq31bsqd gx1rr48f qh5tioqs"]')

    reachedTop = False
    while not reachedTop:
        chat_pane.send_keys(Keys.CONTROL + Keys.HOME)
        WebDriverWait(driver, 5)
        
        try:
            top = driver.find_element(By.XPATH, '//div[@class="UzMP7 _1hpDv n6BPp"]')
            reachedTop = True
        except NoSuchElementException:
            print("Can't find top")

    try:
        messages = driver.find_elements(By.XPATH, messages_query)
        print(len(messages))
    except NoSuchElementException:
        print('''There are no messages''') 

    try:
        pics = driver.find_elements(By.XPATH, pics_query)
        print(len(pics))
    except NoSuchElementException:
        print('''There are no pictures''') 
            

            

