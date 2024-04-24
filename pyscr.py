from selenium import webdriver
from selenium.webdriver.common.by import By
import time, traceback, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service


"""
    author: @ghooost0x2a
     
    This is a script that automates mass twitter unfollowing from a txt file list of users. It has random sleeps to avoid being detected as a bot and only does 30-60 unfollows at once. It uses Firefox with Selenium to emulate user interaction.
    
    The script does it's best to simulate a person unfollowing a bunch of people manually.   
"""

print(f"\n\n################ {time.time()} ################\n")

# List of users to unfollow, loaded from our text file
list_of_users_to_unfollow = []

# Tracking the users we unfollowed this pass
unfollowed_users = []

users_with_errors = []

# Open the txt file containing all the users to unfollow and load them into our list_of_users_to_unfollow list
with open("./inactive_followers.txt","r") as fr:
    for uss in fr:
        # Trim the \n IF there is one and avoid duplicates
        if uss[-1:] == "\n":
            if uss[:-1] not in list_of_users_to_unfollow:
                list_of_users_to_unfollow.append(uss[:-1])
        else:
            if uss not in list_of_users_to_unfollow:
                list_of_users_to_unfollow.append(uss)
    
print(f"Total number of users to unfollow: {len(list_of_users_to_unfollow)}")

# Our Firefox Selenium driver
driver = webdriver.Firefox(service=Service(executable_path="/snap/bin/firefox.geckodriver", service_args = ['--marionette-port', '2828', '--connect-existing'] ))

# XPATHs to our various twitter HTML elements
twitter_search_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input"
search_result_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[2]/div/div[3]"
unfollow_btn_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div[2]/div[4]/div[1]/div/div/span/span"
unfollow_btn2_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div[2]/div[3]/div[1]/div/div/span/span"
unfollow_btn_confirm_xpath = "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span/span"

# Each time we run the script (aka each pass), we are unfollowing between 30 and 60 people at once, to avoid getting banned. Also use random amount to avoid appearing like a bot.
random_amount_to_unfollow_this_pass = random.randint(20, 43)
#random_amount_to_unfollow_this_pass = 67

# First we go to the hope page
driver.get(f"https://twitter.com/ghooost0x2a")

# Sleep to wait for the homepage to finish loading
time.sleep(3)

# We loop through the list_of_users_to_unfollow
for usrr in list_of_users_to_unfollow:
    # We make sure we stop when we reach the limit of unfollows for this pass
    if len(unfollowed_users) > random_amount_to_unfollow_this_pass:
        break
    print(f"Unfollowing {usrr}")
    
    # Sometimes there might be random temporary failures with some profiles, which is why we use the try/except, so that the script doesn't stop if that happens. The problematic users will simply remain in the list_of_users_to_unfollow for the next script pass
    try:
        
        # First we find the search box and put in the name of our user, then we wait 1 to 2 seconds for results to load
        twitter_search_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, twitter_search_xpath)) #This is a dummy element
        )
        #twitter_search_elem = driver.find_element(By.XPATH, twitter_search_xpath)
        twitter_search_elem.send_keys(f"@{usrr}")
        time.sleep(random.randint(2,4))
        
        # We find the first search result and click on it, then wait 2 to 4 seconds for page to load
        #search_result_elem = driver.find_element(By.XPATH, search_result_xpath)
        search_result_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, search_result_xpath)) #This is a dummy element
        )      
        search_result_elem.click()
        time.sleep(random.randint(2,4))
        
        unfollow_btn_elem = None
        try:
            # We find the UNFOLLOW button and click on it, then we wait 1 to 2 seconds for confirmation popup
            #unfollow_btn_elem = driver.find_element(By.XPATH, unfollow_btn_xpath)
            unfollow_btn_elem = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, unfollow_btn_xpath)) #This is a dummy element
            )                
        except:
            unfollow_btn_elem = None
        finally:
            try:
                if not unfollow_btn_elem:
                    unfollow_btn_elem = WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, unfollow_btn2_xpath)) #This is a dummy element
                    ) 
            except:
                unfollow_btn_elem = WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div[2]/div[4]/div")) #This is a dummy element
                    ) 
                unfollo_span = "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div[2]/div/div[3]/div/div/div/div/div[2]/div/span"
                unfollow_span_elem = WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, unfollo_span)) #This is a dummy element
                    ) 
                time.sleep(2)
                unfollow_span_elem.click()
                unfollowed_users.append(usrr)
                continue
                
                
        if unfollow_btn_elem.text.lower() != "following":
            unfollowed_users.append(usrr)
            continue   

        unfollow_btn_elem.click()
        time.sleep(random.randint(1,2))

        # We find the UNFOLLOW button in the confirmation popup and click on it
        unfollow_btn_confirm_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, unfollow_btn_confirm_xpath)) #This is a dummy element
        )        
        #unfollow_btn_confirm_elem = driver.find_element(By.XPATH, unfollow_btn_confirm_xpath)
        unfollow_btn_confirm_elem.click()
        
        # We successfully unfollowed this user, so we add it to our list of unfollowed_users
        unfollowed_users.append(usrr)
    except:
        # Print the exception
        traceback.print_exc()
        
        # Go back home
        driver.get(f"https://twitter.com/ghooost0x2a")
        
        # Sleep to load the page
        time.sleep(1)
        print(f"Error with {usrr=}")
        print(f"{unfollowed_users=}")
        users_with_errors.append(usrr)

    # Random wait between each user, to avoid being seen as a bot
    time.sleep(random.randint(1,5))

# Once we finish with the 30 to 60 users in this pass, we need to date out inactive_followers.txt file to remove the users we just unfollowed so we don't try to unfollow the same ones on the next pass
with open("./inactive_followers.txt","w") as fq:
    for usrrr in list_of_users_to_unfollow:
        if usrrr not in unfollowed_users: 
            fq.write(f"{usrrr}\n")

print(f"\nFIN!\n\nTotal numbers unfollowed this pass: {len(unfollowed_users)}\nNumber left to unfollow: {len(list_of_users_to_unfollow) - len(unfollowed_users)}")
print(f"Users unfollowed this pass: {unfollowed_users}")
print(f"Users with errors ({len(users_with_errors)}): {users_with_errors}")
exit(0)