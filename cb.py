from selenium import webdriver
from selenium.webdriver.common.by import By
import time, traceback, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
driver = webdriver.Firefox(service=Service(executable_path="/snap/bin/firefox.geckodriver", service_args = ['--marionette-port', '2828', '--connect-existing'] ))



for curr_page in range(1, 40):
    
    try:
        with open(f"./tw_not_following_back/page{curr_page}.html","w") as pa:
            pa.write(driver.page_source)
    except:
        try:
            with open(f"./tw_not_following_back/page{curr_page}.html","w") as pa:
                pa.write(driver.page_source)    
        except:                
            pass
    time.sleep(3)
    next_btn_xp = f'//*[@id="bp{curr_page+1}"]'

    next_btn_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, next_btn_xp)) #This is a dummy element
            )    

    print(f"{next_btn_elem=}")

    curr_page_xp = "/html/body/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div/span/button[3]"

    next_btn_elem.click()

    new_curr_page = curr_page
    while new_curr_page == curr_page:
        curr_page_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, curr_page_xp)) #This is a dummy element
                )   
        print(f"{curr_page_elem.text=}")
        new_curr_page = int(curr_page_elem.text.split("/")[0])
        time.sleep(2)
        print(f"{new_curr_page=}")
        print(f"{curr_page=}")
    time.sleep(3)        
    
