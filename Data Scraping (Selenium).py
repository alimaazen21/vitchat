import os
import sys
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64
from selenium.webdriver.support import expected_conditions 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.action_chains import ActionChains
import tkinter as tk
from PIL import ImageTk
import subprocess

app = Flask(__name__)
socketio = SocketIO(app)

def run_selenium_script(username, password, progress_callback):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach",True)
       # options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get("https://vtopcc.vit.ac.in/vtop/open/page")

        student_login = driver.find_element(By.ID,"student")
        student_login.click()

        username_field = driver.find_element(By.ID,"username")
        password_field = driver.find_element(By.ID,"password")

        #username = input("Enter Username: ")
        #password = input("Enter Password: ")


        while True:
            try:
                captcha_field = driver.find_element(By.ID,"captchaStr")
                captcha_image = driver.find_element(By.XPATH, "//img[@class='form-control img-fluid bg-light border-0']")
                image_url = captcha_image.get_attribute("src")
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

                    username_field.send_keys(username)
                    password_field.send_keys(password)                    
                    captcha_field.send_keys(captcha)
                    root.quit()
                    root.destroy()
                        
                submit_button = tk.Button(root, text="Submit", command=submit_captcha)
                submit_button.pack(pady=10)

                root.mainloop()
                break


            except Exception as e:
                print("No captcha found.",e)

        print("\n")
        print("Logging in..")
        submit_button = driver.find_element(By.ID,"submitBtn")
        submit_button.click()
        progress_callback(10)
        #print(driver.current_url)
        wait = WebDriverWait(driver,180)
        alert_ok = wait.until(expected_conditions.visibility_of_element_located((By.ID,"btnClosePopup")))
        alert_ok.click()

        print("Logged in.")
        print("\n")

        actions = ActionChains(driver)

        print("Fetching grade history..")

        examinations_xpath = '//div[@id="sidePanel"]//div[8]'
        examinations = driver.find_element(By.XPATH,examinations_xpath)
        actions.move_to_element(examinations).perform()
        time.sleep(1)

        grade_history = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[8]/div[1]/a[6]")

        time.sleep(1)
        actions.move_to_element(grade_history).perform()
        time.sleep(1)
        actions.click(grade_history).perform()

        #cgpa = wait.until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR,"body > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > section:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > form:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(9) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3)")))
        #print("\n")
        #print("Your CGPA is: ",cgpa.text)
        time.sleep(2)

        table_visibility_test = wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[3]/td[9]")))
        grade_list = []
        for x in range(3,100):

            try:

                serial_number = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[1]").text
                course_code = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[2]").text
                course_name = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[3]").text
                course_type = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[9]").text
                grade = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[6]").text
                credit = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{x}]/td[5]").text


                record = {"S.NO":serial_number,"Course Code":course_code,"Course Name":course_name,"Course Type":course_type,"Grade":grade,"Credit":credit}

                grade_list.append(record)

            finally:
                continue

        

        credits_registered = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/table[1]/tbody[1]/tr[1]/td[1]").text
        credits_earned = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/table[1]/tbody[1]/tr[1]/td[2]").text
        current_cgpa = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/div[1]/div[2]/div[5]/div[1]/div[1]/div[2]/table[1]/tbody[1]/tr[1]/td[3]").text

        with open('new_grade_history.txt', 'w') as file:
            file.write("S.NO\tCourse Code\tCourse Name\tCourse Type\tGrade\tCredit\n")
            file.write("=" * 80 + "\n")

            for record in grade_list:
                file.write(f"{record['S.NO']}\t{record['Course Code']}\t{record['Course Name']}\t{record['Course Type']}\t{record['Grade']}\t{record['Credit']}\n")

            file.write("\n")
            file.write(f"Credits Registered: {credits_registered}\n")
            file.write(f"Credits Earned: {credits_earned}\n")
            file.write(f"Current CGPA: {current_cgpa}\n")

            file.write("Grade Points: S=10, A=9, B=8, C=7, D=6, E=5, F=0, N1=0, P=None(not considered for cgpa calculation)\n")



        print("Grade History saved to txt file.")
        progress_callback(20)

        academics = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[6]/button[1]")
        actions.move_to_element(academics).perform()
        time.sleep(1)
        attendance = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[6]/div[1]/a[10]")
        actions.move_to_element(attendance).perform()
        time.sleep(1)
        actions.click(attendance).perform()

        dropdown_element = wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[1]/select[1]")))
        select = Select(dropdown_element)

        print("\n")
        i=0
        for option in select.options:
            print(i,end=" ")
            print(option.text)
            i=i+1

        print("\n")

        semester_choice = 2
        select.select_by_index(semester_choice)
        time.sleep(1)
        view = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[2]/div[1]/button[1]")
        actions.click(view).perform()
        time.sleep(3)

        print("Fetching attendance records..")

        table2_visibility_test = wait.until(expected_conditions.visibility_of_element_located((By.TAG_NAME,"table")))
        attendance_records = []
        for y in range(1,100):
            try:
                serial_number2 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{y}]/td[1]/p[1]").text
                course_code2 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{y}]/td[2]/p[1]").text
                course_name2 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{y}]/td[3]/p[1]").text
                attended = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{y}]/td[10]/p[1]").text
                total = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{y}]/td[11]/p[1]").text
                total_int = int(total)
                attended_int = int(attended)

                percentage = (attended_int/total_int)*100
                percentage = f"{percentage:.2f}"
                percentage = float(percentage)


                record = {"S.NO": serial_number2, "Course Code": course_code2, "Course Name": course_name2, "Attended Classes": attended, "Total Classes": total, "Percentage": percentage}
                attendance_records.append(record)

            finally:
                continue

        current_credits = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[11]/td[1]/b[1]/span[1]").text

        with open('new_attendance_records.txt', 'w') as file:
            file.write("S.NO\tCourse Code\tCourse Name\tAttended Classes\tTotal Classes\tPercentage\n")
            file.write("=" * 100 + "\n")  

            for record in attendance_records:
                file.write(f"{record['S.NO']}\t{record['Course Code']}\t{record['Course Name']}\t{record['Attended Classes']}\t{record['Total Classes']}\t{record['Percentage']}\n")
            
            file.write(f"Current Credits (This semester): {current_credits}")


        print("Attendance Records saved to txt file.")
        progress_callback(30)

        table2_visibility_test = wait.until(expected_conditions.visibility_of_element_located((By.TAG_NAME,"table")))
        detailed_attendance_records = []
        for i in range(1,20):
            try:
                time.sleep(5)
                course_code = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({i}) td:nth-child(2) p:nth-child(1)").text
                course_name = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({i}) td:nth-child(3) p:nth-child(1)").text
                faculty_name = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({i}) td:nth-child(6) p:nth-child(2)").text
                attendance_view = driver.find_element(By.XPATH,f"(//a[contains(text(),'View')])[{i}]")
                                                    
                actions.click(attendance_view).perform()
                time.sleep(3)

                for j in range(1,50):
                    try:
                        sno = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({j}) td:nth-child(1) p:nth-child(1)").text
                        date = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({j}) td:nth-child(2)").text
                        slot = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({j}) td:nth-child(3)").text
                        day_time = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({j}) td:nth-child(4) p:nth-child(1)").text
                        status = driver.find_element(By.CSS_SELECTOR,f"tbody tr:nth-child({j}) td:nth-child(5) span:nth-child(1)").text

                        record = {"S.NO":sno,"Course Code":course_code,"Course Name":course_name, "Faculty/Professor/Teacher Name":faculty_name, "Date": date, "Slot": slot, "Day and Time": day_time, "Status": status}
                        print(record)
                        print("\n")
                        detailed_attendance_records.append(record)
                    finally:
                        continue
                back_btn = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[1]/h3[1]/button[1]")
                actions.click(back_btn).perform()
                time.sleep(3)
            finally:
                continue


        with open('detailed_attendance_records.txt','w') as file:
            file.write("S.NO\tCourse Code\tCourse Name\tDate\tSlot\tDay and Time\tStatus")
            file.write("=" * 100 + "\n")

            for record in detailed_attendance_records:
                file.write(f"{record['S.NO']}\t{record['Course Code']}\t{record['Course Name']}\t{record['Faculty/Professor/Teacher Name']}\t{record['Date']}\t{record['Slot']}\t{record['Day and Time']}\t{record['Status']}\n")

        print("Detailed Attendance Records saved to txt file.")
        progress_callback(60)


        print("Fetching calendar data..")

        academics = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[6]/button[1]/i[1]")
        actions.move_to_element(academics).perform()
        time.sleep(1)

        academic_timetable = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[6]/div[1]/a[18]")

        time.sleep(1)
        actions.move_to_element(academic_timetable).perform()
        time.sleep(1)
        actions.click(academic_timetable).perform()

        time.sleep(3)
        select = Select(driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[2]/div[1]/select[1]"))
        select.select_by_value('CH20242501')
        time.sleep(5)

        calendar_records = []

        for k in range(1,9):
            try:
                selected_month =  driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[1]/a[{k}]")
                actions.click(selected_month).perform()
                time.sleep(3)
                for j in range(2,7):
                    for i in range(1,8):
                        try:
                            month = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/h4[1]").text
                            date = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[1]").text
                            day = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/th[{i}]").text

                            event1 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[2]").text
                            event2 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[3]").text
                            event3 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[4]").text
                            event4 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[5]").text
                            event5 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[6]").text
                            event6 = driver.find_element(By.XPATH,f"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[2]/form[1]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[{j}]/td[{i}]/span[7]").text

                            record = {"month":month,"date":date,"day":day,"Event1":event1,"Event2":event2,"Event3":event3, "Event4":event4, "Event5":event5, "Event6":event6}
                            print(record)
                            calendar_records.append(record)
                            print("\n")
                        finally:
                            continue
                time.sleep(3)
            finally:
                continue             



        with open('calendar_data.txt', 'w') as file:

            file.write("Month\tDate\tDay\tEvent1\tEvent2\tEvent3\tEvent4\tEvent5\tEvent6\n")
            file.write("=" * 100 + "\n")

            for record in calendar_records:
                file.write(f"{record['month']}\t{record['date']}\t{record['day']}\t{record['Event1']}\t{record['Event2']}\t{record['Event3']}\t{record['Event4']}\t{record['Event5']}\t{record['Event6']}\n")
            
        print("Calendar Records saved to txt file.")
        progress_callback(90)



        print("Fetching personal details..")


        my_info = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/button[1]")
        actions.move_to_element(my_info).perform()
        profile = wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]")))
        time.sleep(1)
        actions.move_to_element(profile).perform()
        time.sleep(1)
        actions.click(profile).perform()
        time.sleep(5)

        name = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/p[1]").text
        regno = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/label[2]").text
        program = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/label[2]").text
        vitemail = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/label[2]").text
        school = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/label[2]").text


        proctor_info = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/h2[1]/button[1]/strong[1]")
        time.sleep(2)
        actions.move_to_element(proctor_info).perform()
        time.sleep(2)
        actions.click(proctor_info).perform()
        time.sleep(2)

        proctor_name = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]").text
        proctor_email = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[7]/td[2]").text
        proctor_phone = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[9]/td[2]").text
        proctor_designation = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[3]/td[2]").text
        proctor_id = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[2]").text
        proctor_school = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[4]/td[2]").text
        proctor_dept = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[4]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[6]/td[2]").text

        hostel_info = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/h2[1]/button[1]/strong[1]")
        time.sleep(1)
        actions.move_to_element(hostel_info).perform()
        time.sleep(1)
        actions.click(hostel_info).perform()
        time.sleep(2)

        app_no = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[2]").text
        block_name = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[3]/td[2]").text
        room_no = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[4]/td[2]").text
        bed_type = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[5]/td[2]").text
        mess_info = driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/section[1]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[6]/td[2]").text


        with open('personal_data.txt', 'w') as file:
            file.write("== My Personal Information ==\n")
            file.write(f"My Name: {name}\n")
            file.write(f"My Application Number: {app_no}\n")
            file.write(f"My Registration Number: {regno}\n")
            file.write(f"My Program and/or Branch: {program}\n")
            file.write(f"My VIT College/University Email: {vitemail}\n")
            file.write(f"My School: {school}\n")
            file.write(f"My Hostel Block: {block_name}\n")
            file.write(f"My Room Number: {room_no}\n")
            file.write(f"My Room/Bed Type: {bed_type}\n")
            file.write(f"My Mess Information: {mess_info}\n \n\n")

            file.write("== My Proctor's Information ==\n")
            file.write(f"My Proctor's Name: {proctor_name}\n")
            file.write(f"My Proctor's Email: {proctor_email}\n")
            file.write(f"My Proctor's Phone/Mobile Number: {proctor_phone}\n")
            file.write(f"My Proctor's Designation: {proctor_designation}\n")
            file.write(f"My Proctor's Faculty ID Number: {proctor_id}\n")
            file.write(f"My Proctor's School: {proctor_school}\n")
            file.write(f"My Proctor's Department: {proctor_dept}\n")

        print("Personal Data saved to txt file.")

        progress_callback(100)

        socketio.emit('scraping_complete', {'message':'Scraping complete! Redirecting now'})

        driver.close()

        stop_flask_and_start_second_app()

def stop_flask_and_start_second_app():
    print("Stopping the first Flask app...")
    sys.exit(0)  

    print("Checking if app.py exists...")
    if os.path.exists('app.py'):
        print("app.py found!")
    else:
        print("app.py not found. Please check the path.")

    print("Starting the second Flask app...")
    try:
        subprocess.Popen([sys.executable, 'app.py'])  
    except Exception as e:
        print(f"Error starting second Flask app: {e}")



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        thread = threading.Thread(target=run_selenium_script, args=(username, password, progress_callback))
        thread.start()

    return render_template('new_login.html')

def progress_callback(progress):
    socketio.emit('progress_update', {'progress': progress})

@socketio.on('connect')
def on_connect():
    print("Client connected")

if __name__ == '__main__':
    socketio.run(app, debug=True)