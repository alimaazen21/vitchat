import base64
from io import BytesIO
from tkinter import Image
from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import time
from PIL import Image
import tkinter as tk
from PIL import ImageTk
from io import StringIO

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto('https://vtopcc.vit.ac.in/vtop/open/page')

            student_login = page.query_selector("//img[@id='student']")
            student_login.click()

            def login(username, password):

                while True:
                    try:
                        username_field = page.query_selector("#username")
                        password_field = page.query_selector("//input[@id='password']")                        
                        captcha_field = page.wait_for_selector("//input[@id='captchaStr']", state="visible", timeout=5000)
                        captcha_image = page.wait_for_selector("//img[@class='form-control img-fluid bg-light border-0']", state="visible", timeout=5000)

                        image_url = captcha_image.get_attribute("src")
                        print("Captcha image URL:", image_url)
                                
                        header, base64_data = image_url.split(',', 1)
                        image_data = base64.b64decode(base64_data)
                        image = Image.open(BytesIO(image_data))
                        
                        root = tk.Tk()
                        root.title("Captcha Verification")

                        img_tk = ImageTk.PhotoImage(image)

                        label_img = tk.Label(root, image=img_tk)
                        label_img.pack(pady=10)

                        label_text = tk.Label(root, text="Enter Captcha: ")
                        label_text.pack()

                        captcha_input = tk.Entry(root)
                        captcha_input.pack(pady=5)

                        def submit_captcha():
                            captcha = captcha_input.get()

                            username_field.type(username)
                            password_field.type(password)
                            captcha_field.click()                    
                            captcha_field.type(captcha)
                            root.quit()
                                
                        submit_button = tk.Button(root, text="Submit", command=submit_captcha)
                        submit_button.pack(pady=10)

                        root.mainloop()
                        break
                                
                    except Exception as e:
                        print("No captcha found or an error occurred:", e)
                        page.reload()

            login(username, password)

            submit_btn = page.query_selector("//button[@id='submitBtn']")
            submit_btn.click()

            alert_ok = page.wait_for_selector("#btnClosePopup", timeout=1800000) 

            alert_ok.click(timeout=900000)

            examinations = page.locator('//div[@id="sidePanel"]//div[8]')
            examinations.hover()

            page.wait_for_timeout(1000) 
            
            grade_history = page.locator("/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[8]/div[1]/a[6]")
            
            # Wait for the element to be visible before interacting (optional but recommended)
            grade_history.wait_for(state="visible", timeout=5000)  # Wait up to 5 seconds for the element to be visible
            
            # Hover over the element (equivalent to Selenium's move_to_element)
            grade_history.hover()
            
            # Wait for a short time before clicking (if necessary, use wait_for_timeout)
            page.wait_for_timeout(1000)  # Wait for 1 second (1000ms)
            
            # Click the element
            grade_history.click()


            page.wait_for_timeout(5000)


            browser.close()
    
    return render_template('new_login.html')
    
if __name__ == '__main__':
    app.run(debug=True)






