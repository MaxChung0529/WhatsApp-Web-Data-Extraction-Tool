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
import time
from datetime import date
import os
import shutil

global images_path
global videos_path
global distribute_path

images_path = os.path.abspath("images")
videos_path = os.path.abspath("videos")
distribute_path = os.path.abspath("distribute")
landing_wrapper_class = "landing-wrapper"
logged_in = '//div[@class="two _aigs"]'
video_query = '''//div[@role="row"]/div[1]/div[@class="message-in focusable-list-item _amjy _amjz _amjw"]/div[1]/div[@class="_amk6 _amlo"]/div[1]/div[1]/div[@role="button"]'''

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



def main():

    clear_folders()

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

        if name.text == "Max":

            #Terminate if no contacts are found
            if (len(contacts) <= 0):
                break

            name.click()

            time.sleep(1)

            profile_btn = driver.find_element(By.XPATH, '//div[@title="Profile details"]')
            profile_btn.click()
            
            contact_detail = driver.find_element(By.XPATH, '//div[@class="_aigv _aig-"]')

            time.sleep(1)

            print(driver.find_element(By.XPATH, '//div[@class="x1emribx x6prxxf x1xojpga"]').text)

            if int(driver.find_element(By.XPATH, '//div[@class="x1emribx x6prxxf x1xojpga"]').text) > 0:

                dialog = contact_detail.find_element(By.XPATH, 'span[1]/div[1]/span[1]/div[1]/div[1]/section[1]/div[2]/div[2]')

                first_item = dialog.find_element(By.XPATH, 'div[1]/div[@role="listitem"]')
                first_item.click()

                time.sleep(1)
                
                left_end = False

                while not left_end:

                    media_details = driver.find_element(By.XPATH, '//div[@class="_ak8l"]')
                    sender = media_details.find_element(By.XPATH, 'div[@role="gridcell"]/div[1]/span[1]').text
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
                        
                        print("Sender: ", sender, "Date: ", media_date, "Time: ", media_time, "Type: ", media_type)
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


            
if __name__ == '__main__':
    main()