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
import requests
from PIL import Image 
import base64
from insert import insert
from anonymise import anonymise

landing_wrapper_class = "landing-wrapper"
logged_in = "_3WByx"
user_query = '''//div[@class="_21S-L"]/div[@class="Mk0Bp _30scZ"]/span[@class='ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 l7jjieqr _11JPr'][@dir="auto"]'''

messages_query = '''//div[@role="row"]//div[@class="message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a _3m5cz"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a _3m5cz"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a"]//div[@class="_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _1uv-a"]//div[@class="_1BOF7 _2AOIt"]'''

pics_query = '''//div[@role="row"]
                //div[@class="CzM4m _2zFLj _3sxvM"]
                //div[@class="_3EyT- message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]
                //div[@class="UzMP7 _27hEJ"]    
                |//div[@role="row"]
                //div[@class="CzM4m _2zFLj"]
                //div[@class="_3EyT- message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]
                //div[@class="UzMP7 _27hEJ _3m5cz"]'''

pic_query = '''//div[@role="row"]//div[@class="CzM4m _2zFLj"]//div[@class="_3EyT- message-out focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _27hEJ _3m5cz"]//div[@class = "_1BOF7 _2AOIt"]
|//div[@role="row"]//div[@class="CzM4m _2zFLj _3sxvM"]//div[@class="_3EyT- message-in focusable-list-item _1AOLJ _2UtSC _1jHIY"]//div[@class="UzMP7 _27hEJ"]//div[@class = "_1BOF7 _2AOIt"]'''

top_row = '''//div[@role="row"]//div[@class="CzM4m _2zFLj"]//div[@class="_2OvAm focusable-list-item _2UtSC _1jHIY"]'''
text_class = "_11JPr selectable-text copyable-text"
contact_list = "_199zF _3j691"
title_class = "Mk0Bp _30scZ"

def extract_messages_details_(message, con, cur):

    sender = message.find_element(By.XPATH,'span[1]').get_attribute('aria-label')
    print(sender)

    time_sent = message.find_element(By.XPATH, 'div/div[@class="cm280p3y to2l77zo n1yiu2zv c6f98ldp ooty25bp oq31bsqd"]/div[@class="copyable-text"]').get_attribute('data-pre-plain-text')
    print(time_sent)

    text_sent = message.find_element(By.XPATH, 'div/div[@class="cm280p3y to2l77zo n1yiu2zv c6f98ldp ooty25bp oq31bsqd"]/div[@class="copyable-text"]/div[@class="_21Ahp"]/span[@class="_11JPr selectable-text copyable-text"]/span').text
    print(text_sent)

    #insert(time_sent,sender,text_sent, con, cur)

    print('======================================================================\n')

def extract_images(pic,driver):
    sender = pic.find_element(By.XPATH, 'span[1]').get_attribute('aria-label')
    print(sender)

    time_sent = pic.find_element(By.XPATH, 'div[1]/div[1]/div[@class="dpkuihx7 lhggkp7q j2mzdvlq b9fczbqn"]/div[1]/span[1]').text
    print(time_sent)

    image_src = pic.find_element(By.XPATH, 'div[1]/div[1]/div[1]/div[1]/div[2]/img[1]').get_attribute('src')
    split_src = str(image_src).split("/")
    print(image_src)

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
    
    if type(result) == int :
        raise Exception("Request failed with status %s" % result)
    final_image = base64.b64decode(result)
    filename = 'images/' + split_src[len(split_src) - 1] + '.jpg'
    with open(filename, 'wb') as f:
        f.write(final_image)

def main():
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
            
            while True:
                try:
                    sync_ok_button = driver.find_element(By.XPATH, '//button[@class="emrlamx0 aiput80m h1a80dm5 sta02ykp g0rxnol2 l7jjieqr hnx8ox4h f8jlpxt4 l1l4so3b le5p0ye3 m2gb0jvt rfxpxord gwd8mfxi mnh9o63b qmy7ya1v dcuuyf4k swfxs4et bgr8sfoe a6r886iw fx1ldmn8 orxa12fk bkifpc9x rpz5dbxo bn27j4ou oixtjehm hjo1mxmu snayiamo szmswy5k"]')
                    if (sync_ok_button.find_element(By.XPATH, 'div[1]/div[1]').text == 'OK'):
                        sync_ok_button.click()
                    else:
                        break
                except:
                    continue    
            break

        except NoSuchElementException:
            continue


    #Get contact names
    contacts = driver.find_elements(By.XPATH, '//div[@class="_21S-L"]//div[@class="Mk0Bp _30scZ"]//span[1]')

    for name in contacts:

        #Terminate if no contacts are found
        if (len(contacts) <= 0):
            break

        name.click()

        #Locate the chat pane
        chat_pane = driver.find_element(By.XPATH, '//div[@class="n5hs2j7m oq31bsqd gx1rr48f qh5tioqs"]')    

        reachedTop = False
        while not reachedTop:

            chat_pane.send_keys(Keys.CONTROL + Keys.HOME)
            WebDriverWait(driver, 100)
            
            try:
                #Check if reaches top
                driver.find_element(By.XPATH, '//div[@class="UzMP7 _1hpDv n6BPp"]')
                reachedTop = True
            except NoSuchElementException:
                #Click the button to sync message
                try:
                    sync_msg_button = driver.find_element(By.XPATH, '//div[@class="_38vwC yTWyz"]/button[1]')
                    sync_msg_button.click()
                except NoSuchElementException:
                    continue
                    #print("No Sync older messages")

        messages = []

        try:
            find_message = driver.find_elements(By.XPATH, messages_query)
            if (len(find_message) > 0):
                for message in find_message:
                    messages.append(message)
                    #extract_messages_details_(message, con, cur)  
                
            #print(len(messages))
        except NoSuchElementException:
            continue
            #print('''There are no messages''') 

        
        try:
            pics = driver.find_elements(By.XPATH, pic_query)
            for pic in pics:
                extract_images(pic,driver)
        except NoSuchElementException:
            print('''There are no pictures''') 
  

if __name__ == '__main__':
    main()
            

