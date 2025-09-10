import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

def apply_for_outing(start_time, end_time, place, reason):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # Uncomment the line below if you want headless mode
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://vtopcc.vit.ac.in/vtop/open/page")

    # Login logic
    student_login = driver.find_element(By.ID, "student")
    student_login.click()

    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    username = "ALIMAAZEN"
    password = "Abcd@1234567"

    username_field.send_keys(username)
    password_field.send_keys(password)

    try:
        captcha_field = driver.find_element(By.ID, "captchaStr")
        captcha_image = driver.find_element(By.XPATH, "//img[@class='form-control img-fluid bg-light border-0']")
        image_url = captcha_image.get_attribute("src")
        header, base64_data = image_url.split(',', 1)
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        image.save('captcha.jpg')
        image = Image.open('captcha.jpg')
        image.show()
        captcha = input("Enter Captcha: ")
        captcha_field.send_keys(captcha)
    except Exception as e:
        print("No captcha found.")

    print("\n")
    print("Logging in..")
    submit_button = driver.find_element(By.ID, "submitBtn")
    submit_button.click()

    # Wait for the next page to load and close popup
    wait = WebDriverWait(driver, 30)
    alert_ok = wait.until(expected_conditions.visibility_of_element_located((By.ID, "btnClosePopup")))
    alert_ok.click()

    print("Logged in.\n")

    # Navigate to leave request section
    actions = ActionChains(driver)
    hostels_xpath = '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[13]/button[1]'
    hostels = driver.find_element(By.XPATH, hostels_xpath)
    actions.move_to_element(hostels).perform()
    time.sleep(1)

    leave_request_screen = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[13]/div[1]/a[3]")
    time.sleep(1)
    actions.click(leave_request_screen).perform()

    leave_visibility_test = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/button[1]")))

    leave_request = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/button[1]")

    time.sleep(1)
    actions.click(leave_request).perform()

    time.sleep(2)

    select = Select(driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/form[1]/div[2]/select[1]"))
    select.select_by_value('OG')

    visiting_place = driver.find_element(By.ID, "visitingPlace")
    reason_field = driver.find_element(By.ID, "reason")
    from_date = driver.find_element(By.ID, "leaveFromDate")
    time_from = driver.find_element(By.ID, "fromTime")
    to_date = driver.find_element(By.ID, "leaveToDate")
    time_to = driver.find_element(By.ID, "toTime")

    # Fill the fields with the data from Flask app
    visiting_place.send_keys(place)
    reason_field.send_keys(reason)
    
    # Parse the dates and times from the start_time and end_time
    start_time_split = start_time.split(' ')
    end_time_split = end_time.split(' ')
    
    from_date.send_keys(start_time_split[2])  # DD/MM/YYYY
    time_from.send_keys(start_time_split[0])  # HH:MM AM/PM
    to_date.send_keys(end_time_split[2])     # DD/MM/YYYY
    time_to.send_keys(end_time_split[0])     # HH:MM AM/PM

    submit_leave = driver.find_element(By.ID, "submitControl2")
    submit_leave.click()

    print("Leave request submitted successfully.")

if __name__ == "__main__":
    start_time = sys.argv[1]
    end_time = sys.argv[2]
    place = sys.argv[3]
    reason = sys.argv[4]
    
    apply_for_outing(start_time, end_time, place, reason)
