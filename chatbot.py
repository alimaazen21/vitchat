import os
import google.generativeai as genai


genai.configure(api_key="AIzaSyB0v2dpVkf4E_1-UsoT1NaQU0qIU8oG96k")

model = genai.GenerativeModel('gemini-1.5-flash')

grade_history_file = "new_grade_history.txt"
attendance_records_file = "attendance_records.txt"

while(True):
    try:
        with open(grade_history_file, 'r') as f:
            grade_history = f.read()
        with open(attendance_records_file, 'r') as f:
            attendance_records = f.read()

        myprompt = input("Give a prompt: ")
        prompt = f"Please analyze the following grade history and attendance records and answer the question, just answer the question from data from either and dont mention where you got the answer from: '{myprompt}'\n\n{grade_history}\n\n{attendance_records}"
        response = model.generate_content(prompt, request_options={"timeout": 600})
        print(f"Bot: {response.text}")

    except FileNotFoundError:
        print(f"Error: File '{grade_history_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")