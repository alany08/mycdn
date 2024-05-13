import requests
import json
from datetime import datetime, timezone
import time
import smtplib, ssl
import selenium.webdriver
from selenium.webdriver.common.by import By
import sys, traceback
import pickle

acked_months = []
gmail_pwd = "<Google account app-specific password>"
email = "<Your email address>"
password = "<MyACT password>"
monthafter = 7 #The month after which notifications start
chromedriver_path = "<Your chrome driver path>"
chrome_profiles_dir = "<Your chrome user data directory, eg C:\Users\YourUserName\AppData\Local\Google\Chrome\User Data>"
chrome_profile_name = "<Your chrome profile directory name, eg Profile 1>"

# SESSION DATA IS STORED IN act_login_session.pickle, IN CURRENT DIRECTORY
# The utilizaiton of your chrome profile is to retain the captcha cookie, so you will not have to solve so many captchas
#    - This also helps if you are already logged in on your chrome profile

session = requests.session()

default_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Host": "my.act.org",
    "If-Modified-Since": "0",
    "Prefer": "safe",
    "Referer": "https://my.act.org/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
}

def send_email(subject, body):
    global email
    global gmail_pwd

    #server, port, context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.ehlo()
        server.login(email, gmail_pwd)
        message = "Subject: " + subject + " (automated)" + "\n" + body
        server.sendmail(email, email, message)

def login(waittime=5):
    global session
    global email
    global password
    global chromedriver_path
    global chrome_profiles_dir
    global chrome_profile_name

    print("Logging in!")
    try:
        options = selenium.webdriver.ChromeOptions()
        """
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")"""
        options.add_argument(r"--user-data-dir=" + chrome_profiles_dir)
        options.add_argument(r"--profile-directory=" + chrome_profile_name)
        #preserve cookies so less captchas
        driver = selenium.webdriver.Chrome(executable_path=chromedriver_path, options=options)
        driver.get("https://my.act.org/")
        print("Waiting for site load")
        time.sleep(waittime)
        #check for softblock
        text = driver.execute_script("return document.body.innerText")
        if("in line" in text.lower()):
            send_email("ACT Reminder", "A captcha has been detected, please solve the captcha then continue")
            input("Please solve the captcha, then press enter to continue")
        if("sign in to your account" in text.lower()):
            print("Sign in page detected, entering password...")
            continue_btn = driver.find_element(By.CSS_SELECTOR, '[aria-label="Continue"]')
            if(continue_btn):
                continue_btn.click()
            else:
                raise TypeError("Element not found")
            time.sleep(waittime/10)
            driver.find_element(By.CSS_SELECTOR, '[name="email"]').send_keys(email)
            driver.find_element(By.CSS_SELECTOR, '[type="password"]').send_keys(password)
            time.sleep(waittime/10)
            driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
            time.sleep(waittime/2)
        else:
            print("Already signed in, dumping cookies...")

        #directly dump if no sign in modal
        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"], domain = cookie["domain"])
        with open("act_login_session.pickle", "wb") as handle:
            pickle.dump(session, handle)
        print("Login success!")

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        driver.quit()
        if(waittime != 5):
            print("Login failed after multiple attempts, exiting")
            sys.exit()
        else:
            login(waittime=10)
    driver.quit()

try:
    with open("act_login_session.pickle", "rb") as handle:
        session = pickle.load(handle)
    print("Saved session found, using")
except:
    print("No saved session found, logging in again")
    login()

while True:
    try:
        now_string = datetime.now(timezone.utc).astimezone().strftime("%a+%B+%d+%Y+%H:%M:%S+GMT%z+(Pacific+Daylight+Time)")
        session.cookies.set("OptanonConsent", "isGpcEnabled=0&datestamp=" + now_string + "&version=202307.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=50f97bf2-0fd3-4405-9334-8fc2e0f9390b&interactionCount=0&landingPath=https://my.act.org/&groups=C0001:1,C0003:1,C0002:1,C0004:1,C0005:1", domain="*")

        res = session.get("https://my.act.org/api/test-scheduling/ACTNational/test-centers?product=ACT&radius=80&roomType=PLUS+WRITING&seatAvailability=ALL&standby=true&zipCode=95129",
            headers = default_headers
        )
        if("authentication" in res.text.lower()):
            print("Cookies expired! Logging in again")
            login()
            continue
        results = json.loads(res.text)
        temp_acked_months = []
        new_tests_string = ""
        for site in results:
            for date in site["test_dates"]:
                test_month = int(date["test_date"].split("-")[1])
                test_year = int(date["test_date"].split("-")[0])
                test_day = int(date["test_date"].split("-")[2])
                test_time = date["start_time"]
                if(test_month > monthafter and not (test_month in acked_months)):
                    #past july, as of 5/8/2024 only july has been released
                    temp_acked_months.append(test_month)
                    notify_string = f"Testing for {site['site_name']} on {str(test_month)}/{str(test_day)}/{str(test_year)} at {test_time} released ({date['date_status']})"
                    new_tests_string = new_tests_string + "\n" + notify_string
                    print(notify_string)
        if(len(new_tests_string) > 0):
            print("Sending email...")
            send_email("New ACT Testing dates released", new_tests_string + "\nhttps://my.act.org/")
        acked_months = acked_months + temp_acked_months

    except Exception as e:
        print("Failed to get ACT slots")
        print(e)
        send_email("ACT Registration Reminder", "Failed to pull/process data from ACT's API endpoint, check if you've logged out or logged in again on a new device")
        break
    print("Checked at", datetime.now().isoformat(), "PST")
    time.sleep(300)

print("Exiting...")
